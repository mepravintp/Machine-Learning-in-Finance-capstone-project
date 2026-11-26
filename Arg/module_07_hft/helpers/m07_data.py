"""
Module 7 — order-book data: loading, checks, the split, the inputs
==================================================================

WHAT THIS FILE DOES
    - load_orderbook(): reads data/nova_hft_orderbook.csv, parses Trading_Day (day-first: 05-01-2026 = 5 January),
      keeps the file order as Seq, and maps FLAT → NO_MOVE (decision M7-01; the brief: "Treat FLAT as
      equivalent to NO_MOVE").
    - add_inputs(): builds the engineered inputs from the current and EARLIER events of the same stock and day
      only (never later ones), e.g. order-flow imbalance and past price moves (decision M7-08).
    - split_by_day(): days 1–14 train, 15–17 tune, 18–20 test (decision M7-04).
    - LEAKAGE_COLUMNS: Future_Return_100ms and Future_Price_100ms build the label, so they are never inputs
      (decision M7-02, the brief's own warning). They are used only to score results.
    It is a helper because both task notebooks and the runner's data check use it (project decision P-15).

    The inputs (decision M7-08), in plain words:
        OBI_Level1/L2/L3   (bid size − ask size) ÷ (bid size + ask size) at price levels 1, 2, 3; −1 to +1;
                           positive = more buyers waiting
        OFI                change in best-bid size − change in best-ask size since the stock's previous event
        Signed_volume      last trade's volume, + if a buy, − if a sell; Signed_volume_5 = sum over the last 5 events
        Past_ret_k         mid-price change over the stock's last k events (k = 1, 5, 10)
        Spread_ticks       spread ÷ ₹0.05 tick;  Relative_Spread = spread ÷ mid (given)
        Short_Term_Volatility, Cancellation_Rate, Order_Arrival_Rate   given in the data
        Abs_OBI            size of the imbalance |OBI_Level1| (helps with NO_MOVE)

HOW TO USE
    from m07_data import load_orderbook, add_inputs, split_by_day, INPUTS
    df = add_inputs(load_orderbook()); train, tune, test = split_by_day(df)
    python module_07_hft/helpers/m07_data.py     # data check
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
FILE = DATA_DIR / "nova_hft_orderbook.csv"

LEAKAGE_COLUMNS = ["Future_Return_100ms", "Future_Price_100ms"]      # decision M7-02: never inputs
TARGET = "Price_Move_Class"
CLASSES = ["DOWN", "NO_MOVE", "UP"]                                   # alphabetical, as models order them
TICK = 0.05                                                           # smallest price step, ₹
INPUTS = ["OBI_Level1", "OBI_L2", "OBI_L3", "OFI", "Signed_volume", "Signed_volume_5", "Past_ret_1", "Past_ret_5",
          "Past_ret_10", "Spread_ticks", "Relative_Spread", "Short_Term_Volatility", "Cancellation_Rate",
          "Order_Arrival_Rate", "Abs_OBI"]                                       # the 15 agreed inputs (decision M7-08)
INPUT_MEANINGS = {
    "OBI_Level1": "Order-book imbalance at the best price: (bid size − ask size) ÷ total; +1 all buyers, −1 all sellers",
    "OBI_L2": "Same imbalance at the second-best price level",
    "OBI_L3": "Same imbalance at the third-best price level",
    "OFI": "Order-flow imbalance: change in best-bid size − change in best-ask size since the stock's last event",
    "Signed_volume": "Last trade's volume, positive for a buy, negative for a sell",
    "Signed_volume_5": "Signed volume added up over the stock's last 5 events",
    "Past_ret_1": "Mid-price change since the stock's previous event",
    "Past_ret_5": "Mid-price change over the stock's last 5 events",
    "Past_ret_10": "Mid-price change over the stock's last 10 events",
    "Spread_ticks": "Spread in ticks of ₹0.05",
    "Relative_Spread": "Spread ÷ mid price (given in the data)",
    "Short_Term_Volatility": "Recent swing of the price (given in the data)",
    "Cancellation_Rate": "How fast orders are being cancelled (given)",
    "Order_Arrival_Rate": "How fast new orders arrive (given)",
    "Abs_OBI": "Size of the imbalance, ignoring its direction (strong imbalance → fewer no-moves)",
}


def load_orderbook(path: Path = FILE) -> pd.DataFrame:
    """Read the file, parse days (day-first), keep file order as Seq, map FLAT → NO_MOVE (decision M7-01)."""
    df = pd.read_csv(path)
    df["Seq"] = range(len(df))                                         # file order = time order (checked)
    df["Trading_Day"] = pd.to_datetime(df["Trading_Day"], dayfirst=True)
    df[TARGET] = df[TARGET].replace({"FLAT": "NO_MOVE"})
    return df


def add_inputs(df: pd.DataFrame) -> pd.DataFrame:
    """Add the engineered inputs, each from the current or EARLIER events of the same stock and day.

    groupby(...).diff() / .shift(k) look only backwards within each stock and day, so no input ever uses a
    later event (no leakage). The first events of a stock's day have no history: those inputs are blank
    and the models fill them with the training median.
    """
    df = df.sort_values("Seq").copy()
    g = df.groupby(["Stock", "Trading_Day"])
    df["OFI"] = g["Bid_Size_1"].diff() - g["Ask_Size_1"].diff()
    for k in (1, 5, 10):
        df[f"Past_ret_{k}"] = df["Mid_Price"] / g["Mid_Price"].shift(k) - 1
    df["Signed_volume"] = np.where(df["Trade_Side"] == "BUY", 1, -1) * df["Trade_Volume"]
    df["Signed_volume_5"] = df.groupby(["Stock", "Trading_Day"])["Signed_volume"].transform(lambda s: s.rolling(5, min_periods=1).sum())
    df["OBI_L2"] = (df["Bid_Size_2"] - df["Ask_Size_2"]) / (df["Bid_Size_2"] + df["Ask_Size_2"])
    df["OBI_L3"] = (df["Bid_Size_3"] - df["Ask_Size_3"]) / (df["Bid_Size_3"] + df["Ask_Size_3"])
    df["Spread_ticks"] = (df["Spread"] / TICK).round()
    df["Abs_OBI"] = df["OBI_Level1"].abs()
    return df


def feature_columns(df: pd.DataFrame) -> list[str]:
    """Every column that may be an input: everything except the target, leakage columns and IDs."""
    excluded = set(LEAKAGE_COLUMNS) | {TARGET, "Timestamp", "Trading_Day", "Seq"}
    return [c for c in df.columns if c not in excluded]


def split_by_day(df: pd.DataFrame, train_days: int = 14, tune_days: int = 3):
    """Decision M7-04: first 14 days train, next 3 tune (choose models and cut-offs), last 3 test (once)."""
    days = sorted(df["Trading_Day"].unique())
    train = df[df["Trading_Day"].isin(days[:train_days])]
    tune = df[df["Trading_Day"].isin(days[train_days:train_days + tune_days])]
    test = df[df["Trading_Day"].isin(days[train_days + tune_days:])]
    return train, tune, test


def data_report(df: pd.DataFrame) -> dict:
    """Health check printed by the runner's first cell."""
    mid = (df["Bid_Price_1"] + df["Ask_Price_1"]) / 2
    label_ok = ((df["Future_Price_100ms"] / df["Mid_Price"] - 1) - df["Future_Return_100ms"]).abs().max() < 1e-6
    train, tune, test = split_by_day(df)
    return {
        "rows": len(df),
        "missing_values": int(df.isna().sum().sum()),
        "trading_days": df["Trading_Day"].nunique(),
        "stocks": df["Stock"].nunique(),
        "event_types": df["Event_Type"].value_counts().to_dict(),
        "class_share": df[TARGET].value_counts(normalize=True).round(3).to_dict(),
        "mid_price_matches_bid_ask": bool((mid - df["Mid_Price"]).abs().max() < 1e-6),
        "future_return_equals_future_price_over_mid": bool(label_ok),
        "leakage_columns_in_features": [c for c in LEAKAGE_COLUMNS if c in feature_columns(df)],
        "split_rows_train_tune_test": (len(train), len(tune), len(test)),
    }


if __name__ == "__main__":
    for key, value in data_report(load_orderbook()).items():
        print(f"{key}: {value}")

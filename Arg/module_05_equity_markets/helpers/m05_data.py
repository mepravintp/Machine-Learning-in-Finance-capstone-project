"""
Module 5 — market data: load, check, rebalance dates, target and inputs
=======================================================================

WHAT THIS FILE DOES
    Shared by Module 5 Tasks 1 and 2 and by Module 6 (same dataset), so it is a helper.

    - load_market()          reads data/nova_market_data.csv, checks the columns, sorts by stock and date
    - month_end_dates()      the rebalance dates: last trading day of each month (decision M5-03)
    - forward_returns()      the target: each stock's return from one rebalance date to the next (M5-01)
    - add_features()         builds the 22 candidate inputs, all known at the close of each day
    - monthly_panel()        one row per stock per month-end: inputs, sector, next month's return
    - data_report()          quick data check (rows, missing values, dates, ...)

    Lists of inputs:
      ALL_INPUTS (22)  every input built in Task 1 step 2 (13 price/trading + 1 given + 8 macro)
      MACRO (8)        the four macro columns, raw and as 20-day averages (dropped by M5-07)
      INPUTS (13)      the inputs the models get (decision M5-07), plus sector as 0/1 columns

UNITS
    Prices in rupees per share; returns as fractions (0.03 = 3%).

HOW TO USE
    from m05_data import load_market, month_end_dates, add_features, monthly_panel, INPUTS
    python module_05_equity_markets/helpers/m05_data.py        # quick data check
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
FILE = DATA_DIR / "nova_market_data.csv"

EXPECTED_COLUMNS = [
    "Ticker", "Date", "Open", "High", "Low", "Close", "Volume", "Sector", "Market_Return",
    "GDP_Growth", "Interest_Rate", "VIX", "Return", "Momentum_20D", "Volatility_20D",
]

# The four columns that describe the whole economy or market ("macro" = macroeconomic).
MACRO_COLUMNS = ["Market_Return", "GDP_Growth", "Interest_Rate", "VIX"]

# ---- input lists (decision M5-07) -------------------------------------------------------
PRICE_INPUTS = [
    "Past_1D", "Past_5D", "Past_20D", "Past_60D", "Past_120D", "Past_250D",   # past returns
    "Volatility_60D",                                                          # risk
    "Dist_MA50", "RSI_14",                                                     # price trend
    "Volume_z", "Range_HL", "Gap_open",                                        # trading
]
GIVEN_INPUTS = ["Momentum_20D", "Volatility_20D"]                               # given in the data
MACRO = [c for m in MACRO_COLUMNS for c in (m, f"{m}_20Davg")]                  # 8 macro inputs
ALL_INPUTS = PRICE_INPUTS + GIVEN_INPUTS + MACRO                                # 22 candidates
# The models get the price/trading inputs without the macro ones, and without Past_20D,
# which is identical to the given Momentum_20D (correlation 1.00).
INPUTS = [c for c in PRICE_INPUTS + GIVEN_INPUTS if c != "Past_20D"]            # 13 inputs

INPUT_MEANINGS = {
    "Past_1D": "return over the last day",
    "Past_5D": "return over the last week (5 trading days)",
    "Past_20D": "return over the last month (20 trading days); same as Momentum_20D",
    "Past_60D": "return over the last 3 months (60 trading days)",
    "Past_120D": "return over the last 6 months (120 trading days)",
    "Past_250D": "return over the last year (250 trading days)",
    "Momentum_20D": "given: 20-day price change",
    "Volatility_20D": "given: how much daily returns swung over 20 days (standard deviation)",
    "Volatility_60D": "how much daily returns swung over 60 days",
    "Dist_MA50": "how far the price is above (+) or below (−) its 50-day average",
    "RSI_14": "relative strength index: 0–100 gauge of recent up days vs down days (14 days)",
    "Volume_z": "today's trading volume vs its 60-day normal, in standard deviations",
    "Range_HL": "today's high minus low, as a share of the closing price",
    "Gap_open": "today's opening price vs yesterday's close (overnight jump)",
}


def load_market(path: Path = FILE) -> pd.DataFrame:
    """Read the market file, check every expected column is there, sort by stock then date."""
    df = pd.read_csv(path, parse_dates=["Date"])
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    df["Ticker"] = df["Ticker"].astype(str)          # plain text, so joins behave
    return df.sort_values(["Ticker", "Date"]).reset_index(drop=True)


def month_end_dates(df: pd.DataFrame) -> pd.DatetimeIndex:
    """Last trading day of each month (decision M5-03).

    Jan 2021 – Aug 2026 = 5 years × 12 + 8 months = 68 month-ends."""
    dates = pd.Series(df["Date"].unique()).sort_values()
    return pd.DatetimeIndex(dates.groupby(dates.dt.to_period("M")).max().values)


def forward_returns(df: pd.DataFrame, rebalance_dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Target (decision M5-01): each stock's return from one rebalance date to the next.

        y(stock, t) = Close(stock, next rebalance date) ÷ Close(stock, t) − 1

    Example: Close ₹1,500 on 31 Jan and ₹1,560 on 28 Feb → y = 1,560 ÷ 1,500 − 1 = 4%.
    The last date (31 Aug 2026) has no month after it, so 68 month-ends give 67 targets."""
    closes = (df[df["Date"].isin(rebalance_dates)]
              .pivot(index="Date", columns="Ticker", values="Close").sort_index())
    fwd = closes.shift(-1) / closes - 1                      # next month's close ÷ this month's − 1
    out = fwd.stack(future_stack=True).rename("Next_Month_Return").reset_index()
    out.columns = ["Date", "Ticker", "Next_Month_Return"]
    return out


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build the 22 candidate inputs. Every one uses only prices up to and including day t,
    so each is known at the close of day t (no look-ahead).

    Formulas (per stock, day t):
        Past_kD      = Close(t) ÷ Close(t − k days) − 1
        Volatility_60D = standard deviation of the last 60 daily returns
        Dist_MA50    = Close(t) ÷ average Close of the last 50 days − 1
        RSI_14       = 100 − 100 ÷ (1 + average up-move ÷ average down-move, last 14 days)
        Volume_z     = (Volume(t) − 60-day average volume) ÷ 60-day standard deviation of volume
        Range_HL     = (High(t) − Low(t)) ÷ Close(t)
        Gap_open     = Open(t) ÷ Close(t − 1) − 1
        <macro>_20Davg = average of the macro column over the last 20 days
    """
    g = df.groupby("Ticker")
    f = df[["Ticker", "Date", "Sector", "Close"]].copy()
    for k in [1, 5, 20, 60, 120, 250]:
        f[f"Past_{k}D"] = g["Close"].pct_change(k)                       # return over k days
    f["Momentum_20D"] = df["Momentum_20D"]                                # given
    f["Volatility_20D"] = df["Volatility_20D"]                            # given
    f["Volatility_60D"] = g["Return"].transform(lambda s: s.rolling(60).std())
    f["Dist_MA50"] = df["Close"] / g["Close"].transform(lambda s: s.rolling(50).mean()) - 1
    up = g["Return"].transform(lambda s: s.clip(lower=0).rolling(14).mean())       # avg up-move
    down = g["Return"].transform(lambda s: (-s.clip(upper=0)).rolling(14).mean())  # avg down-move
    f["RSI_14"] = 100 - 100 / (1 + up / down)
    vol_mean = g["Volume"].transform(lambda s: s.rolling(60).mean())
    vol_sd = g["Volume"].transform(lambda s: s.rolling(60).std())
    f["Volume_z"] = (df["Volume"] - vol_mean) / vol_sd
    f["Range_HL"] = (df["High"] - df["Low"]) / df["Close"]
    f["Gap_open"] = df["Open"] / g["Close"].shift(1) - 1
    for c in MACRO_COLUMNS:
        f[c] = df[c]                                                      # raw macro column
        f[f"{c}_20Davg"] = g[c].transform(lambda s: s.rolling(20).mean()) # its 20-day average
    return f


def monthly_panel(df: pd.DataFrame) -> pd.DataFrame:
    """One row per stock per month-end that has a next month: the 22 inputs, sector
    (also as 0/1 columns 'Sec_<name>'), and Next_Month_Return (the target).

    68 month-ends − 1 = 67 months × 15 stocks = 1,005 rows."""
    me = month_end_dates(df)
    feats = add_features(df)
    panel = feats[feats["Date"].isin(me)].merge(forward_returns(df, me), on=["Date", "Ticker"], how="inner")
    panel = panel.dropna(subset=["Next_Month_Return"]).reset_index(drop=True)
    sectors = pd.get_dummies(panel["Sector"], prefix="Sec", dtype=float)  # 8 yes/no columns
    return pd.concat([panel, sectors], axis=1)


def data_report(df: pd.DataFrame) -> dict:
    """Quick data check: size, gaps, dates, and that Return is today's close-to-close change."""
    by_ticker = df.groupby("Ticker")
    recomputed = by_ticker["Close"].pct_change()
    return {
        "rows": len(df),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated(["Ticker", "Date"]).sum()),
        "tickers": df["Ticker"].nunique(),
        "rows_per_ticker": sorted(by_ticker.size().unique().tolist()),
        "date_range": (str(df["Date"].min().date()), str(df["Date"].max().date())),
        "sectors": sorted(df["Sector"].unique().tolist()),
        "Return_is_same_day_close_to_close": bool((recomputed - df["Return"]).abs().max() < 1e-9),
        "month_end_rebalance_dates": len(month_end_dates(df)),
    }


if __name__ == "__main__":
    for key, value in data_report(load_market()).items():
        print(f"{key}: {value}")

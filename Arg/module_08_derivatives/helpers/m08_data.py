"""Module 8 — load and validate nova_options.csv.

    from m08_data import load_options
    python module_08_derivatives/helpers/m08_data.py     # quick data check
"""
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
FILE = DATA_DIR / "nova_options.csv"

EXPECTED_COLUMNS = [
    "Option_ID", "Underlying", "Option_Type", "Strike", "Spot", "Expiry", "Time_to_Maturity",
    "Volatility", "Interest_Rate", "Black_Scholes_Price", "Market_Price",
]


def load_options(path: Path = FILE) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Expiry"])
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    return df


def data_report(df: pd.DataFrame) -> dict:
    return {
        "rows": len(df),
        "missing_values": int(df.isna().sum().sum()),
        "option_types": df["Option_Type"].value_counts().to_dict(),
        "underlyings": df["Underlying"].nunique(),
        "maturity_years_range": (round(float(df["Time_to_Maturity"].min()), 3), round(float(df["Time_to_Maturity"].max()), 3)),
        "volatility_range": (round(float(df["Volatility"].min()), 3), round(float(df["Volatility"].max()), 3)),
        "non_positive_prices": int((df[["Strike", "Spot", "Market_Price"]] <= 0).sum().sum()),
        "mean_abs_gap_market_vs_given_BS": round((df["Market_Price"] - df["Black_Scholes_Price"]).abs().mean(), 2),
    }


if __name__ == "__main__":
    for key, value in data_report(load_options()).items():
        print(f"{key}: {value}")

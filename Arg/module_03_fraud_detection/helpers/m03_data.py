"""
Module 3 — load and check the transaction data
==============================================

WHAT THIS FILE DOES
    Loads nova_transactions.csv from the shared data/ folder, checks it, and adds the derived
    columns every Module 3 task uses. It is a helper because all four tasks load the same data
    (project decision P-15).

    It provides:
      - load_transactions(): the 30,000 transactions, sorted by time
      - add_features():      derived columns (decision M3-07), each using only information
                             available at the moment of the transaction
      - BRIEF_COLUMNS:       the variables the brief lists
      - INPUT_SETS, make_inputs(): the two model input sets (decision M3-11) as model-ready numbers
      - data_report():       a short quality summary (rows, missing values, fraud rate, ...)

MONEY
    Plain rupees, as given in the file (project decision P-02).

HOW TO USE
    from m03_data import load_transactions, add_features
    python module_03_fraud_detection/helpers/m03_data.py     # quick data check
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"     # the shared data/ folder at the project root
FILE = DATA_DIR / "nova_transactions.csv"

# The variables the brief lists, plus the three extra columns in the file.
BRIEF_COLUMNS = ["Amount", "Transaction_Type", "Merchant_Category", "Location", "Device_ID",
                 "Account_Age_Months", "Historical_Avg_Transaction", "Transaction_Frequency", "Fraud_Flag"]
EXTRA_COLUMNS = ["Transaction_ID", "Customer_ID", "Timestamp"]
EXPECTED_COLUMNS = EXTRA_COLUMNS + BRIEF_COLUMNS
CATEGORY_COLUMNS = ["Transaction_Type", "Merchant_Category", "Location"]


def load_transactions(path: Path = FILE) -> pd.DataFrame:
    """Read the file, check its columns, parse Timestamp and sort by time.

    Sorting by time matters: later tasks may split by time, and the history columns in
    add_features() must only look at earlier transactions.
    """
    df = pd.read_csv(path)
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    for col in CATEGORY_COLUMNS:
        df[col] = df[col].astype("category")          # labels, not numbers
    return df.sort_values(["Timestamp", "Transaction_ID"]).reset_index(drop=True)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derived columns (decision M3-07). None of them uses Fraud_Flag.

    Amount_Ratio     = Amount ÷ Historical_Avg_Transaction   how unusual this amount is for the customer
    Hour, Weekday    = from Timestamp                       when the transaction happened
    Device_Change    = 1 if this Device_ID differs from the customer's previous transaction
    Location_Change  = 1 if this Location differs from the customer's previous transaction
                       (both look only at EARLIER transactions of the same Customer_ID;
                        a customer's first transaction counts as "no change")
    """
    out = df.copy()
    out["Amount_Ratio"] = out.Amount / out.Historical_Avg_Transaction
    out["Hour"] = out.Timestamp.dt.hour
    out["Weekday"] = pd.Categorical(out.Timestamp.dt.day_name(),
                                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    # Previous transaction of the same customer (the data is already in time order).
    prev_device = out.groupby("Customer_ID").Device_ID.shift()
    prev_location = out.groupby("Customer_ID").Location.shift()
    out["Device_Change"] = (prev_device.notna() & (prev_device != out.Device_ID)).astype(int)
    out["Location_Change"] = (prev_location.notna()
                              & (prev_location.astype(str) != out.Location.astype(str))).astype(int)
    return out


# Model input sets (decision M3-11). Names are the columns of add_features() output.
STRONG_WEAK = ["Amount", "Amount_Ratio", "Historical_Avg_Transaction", "Transaction_Type"]
ALL_COLUMNS = STRONG_WEAK + ["Merchant_Category", "Location", "Account_Age_Months", "Transaction_Frequency",
                             "Hour", "Weekday", "Device_Change", "Location_Change"]
INPUT_SETS = {"Strong + weak": STRONG_WEAK, "All columns": ALL_COLUMNS}
LOG_COLUMNS = ["Amount", "Amount_Ratio", "Historical_Avg_Transaction"]    # money and ratios: used as ln(x)


def make_inputs(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Turn the chosen columns into numbers a model can use (decision M3-11).

    - Amount, Amount_Ratio, Historical_Avg_Transaction → natural log (ln), because money is skewed:
      a few very large values would otherwise dominate. ln keeps the order and evens the spacing.
    - Label columns (Transaction_Type, Merchant_Category, Location, Weekday) → one 0/1 column per
      value except the first (one-hot). Built from the column's fixed list of categories, so the
      training and test tables always get the same columns.
    - Everything else is used as it is.
    Fraud_Flag is never an input.
    """
    assert "Fraud_Flag" not in columns
    parts = []
    for col in columns:
        if col in LOG_COLUMNS:
            parts.append(np.log(df[col]).rename(f"ln_{col}"))
        elif isinstance(df[col].dtype, pd.CategoricalDtype):
            dummies = pd.get_dummies(df[col], prefix=col, drop_first=True).astype(float)
            dummies.columns = [str(c) for c in dummies.columns]
            parts.append(dummies)
        else:
            parts.append(df[col].astype(float))
    return pd.concat(parts, axis=1)


def data_report(df: pd.DataFrame) -> dict:
    """A short quality and size summary."""
    fraud = df["Fraud_Flag"] == 1
    return {
        "rows": len(df),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_transaction_ids": int(df["Transaction_ID"].duplicated().sum()),
        "time_range": (str(df["Timestamp"].min().date()), str(df["Timestamp"].max().date())),
        "customers": int(df["Customer_ID"].nunique()),
        "devices": int(df["Device_ID"].nunique()),
        "fraud_rate": round(float(fraud.mean()), 4),
        "fraud_count": int(fraud.sum()),
        "fraud_value_crore": round(float(df.loc[fraud, "Amount"].sum() / 1e7), 2),
        "transaction_types": df["Transaction_Type"].value_counts().to_dict(),
        "cities": int(df["Location"].nunique()),
    }


if __name__ == "__main__":
    for key, value in data_report(load_transactions()).items():
        print(f"{key}: {value}")

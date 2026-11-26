"""
Module 4 — load and check the customer data
===========================================

WHAT THIS FILE DOES
    Loads nova_customers.csv from the shared data/ folder, checks it, and adds the business-based
    features every Module 4 task uses. It is a helper because all three tasks load the same data
    (project decision P-15).

    It provides:
      - load_customers():  the 5,000 customers
      - add_features():    the 5 business-based features (decision M4-11)
      - GIVEN_INPUTS, DERIVED_INPUTS, MODEL_INPUTS: the churn model's inputs (10 + 5 = 15)
      - data_report():     a short quality summary

MONEY
    Plain rupees, as given in the file (project decision P-02).

HOW TO USE
    from m04_data import load_customers, add_features, MODEL_INPUTS
    python module_04_customer_analytics/helpers/m04_data.py     # quick data check
"""
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"     # the shared data/ folder at the project root
FILE = DATA_DIR / "nova_customers.csv"

EXPECTED_COLUMNS = [
    "Customer_ID", "Age", "Annual_Income", "Account_Balance", "Products_Held",
    "Transactions_Per_Month", "Digital_Usage", "Complaints", "Loan_Balance",
    "Investment_Balance", "Relationship_Length_Years", "Churn_Flag", "Estimated_CLV",
]

# The 10 given customer columns (Customer_ID, Churn_Flag and Estimated_CLV excluded: Estimated_CLV is an
# exact formula of other columns and is Task 2's subject, decision M4-03).
GIVEN_INPUTS = ["Age", "Annual_Income", "Account_Balance", "Products_Held", "Transactions_Per_Month",
                "Digital_Usage", "Complaints", "Loan_Balance", "Investment_Balance", "Relationship_Length_Years"]

# The 5 business-based features (decision M4-11), each with the reason a bank would expect it to matter.
DERIVED_FORMULAS = {
    "Complaints_Per_Year": "Complaints ÷ Relationship_Length_Years  (how often the customer complains)",
    "Total_Balances": "Account_Balance + Loan_Balance + Investment_Balance  (size of the relationship)",
    "Balance_Per_Product": "Total_Balances ÷ Products_Held  (how deep each product is)",
    "Loan_To_Income": "Loan_Balance ÷ Annual_Income  (debt burden)",
    "Savings_To_Income": "(Account_Balance + Investment_Balance) ÷ Annual_Income  (savings held with the bank)",
}
DERIVED_INPUTS = list(DERIVED_FORMULAS)
MODEL_INPUTS = GIVEN_INPUTS + DERIVED_INPUTS                   # 15 inputs in total


def load_customers(path: Path = FILE) -> pd.DataFrame:
    """Read the file and check its columns."""
    df = pd.read_csv(path)
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add the 5 business-based features (decision M4-11). None of them uses Churn_Flag."""
    out = df.copy()
    out["Complaints_Per_Year"] = out.Complaints / out.Relationship_Length_Years
    out["Total_Balances"] = out.Account_Balance + out.Loan_Balance + out.Investment_Balance
    out["Balance_Per_Product"] = out.Total_Balances / out.Products_Held
    out["Loan_To_Income"] = out.Loan_Balance / out.Annual_Income
    out["Savings_To_Income"] = (out.Account_Balance + out.Investment_Balance) / out.Annual_Income
    return out


def data_report(df: pd.DataFrame) -> dict:
    """A short quality and size summary."""
    return {
        "rows": len(df),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_ids": int(df["Customer_ID"].duplicated().sum()),
        "churners": int(df["Churn_Flag"].sum()),
        "churn_rate": round(float(df["Churn_Flag"].mean()), 4),
        "clv_mean": round(float(df["Estimated_CLV"].mean()), 0),
        "clv_zero": int((df["Estimated_CLV"] == 0).sum()),
    }


if __name__ == "__main__":
    for key, value in data_report(load_customers()).items():
        print(f"{key}: {value}")

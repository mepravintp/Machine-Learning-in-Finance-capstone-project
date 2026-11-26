"""
Module 2 — load and check the loan data
=======================================

WHAT THIS FILE DOES
    Loads nova_loans.csv from the shared data/ folder, checks it, and gives every loan its
    identifier, Loan_ID (decision M2-01).
    It is a helper because every Module 2 task loads the same data (project decision P-15).

    It provides:
      - load_loans():  the 5,000 loans as a table, with Loan_ID as the identifier
      - add_ratios():  the four lending ratios agreed in decision M2-11 (RATIO_FORMULAS)
      - MODEL_INPUTS:  the 15 model inputs (decision M2-11)
      - data_report(): a short quality summary (rows, missing values, default rate, ...)

THE LOAN IDENTIFIER (decision M2-01)
    The brief asks for "Loan_ID". The provided file calls the same column "Customer_ID"
    (each customer holds exactly one loan: instructor clarification 6). We never edit the
    raw file. Instead, on loading:
      - if the file already has a Loan_ID column (e.g. an evaluator renamed it), we use it as is;
      - otherwise we rename Customer_ID to Loan_ID.
    Either way, every notebook, output and report uses Loan_ID only.

MONEY
    Plain rupees, as given in the file (project decision P-02).

HOW TO USE
    from m02_data import load_loans, add_ratios, MODEL_INPUTS
    python module_02_credit_risk/helpers/m02_data.py     # quick data check
"""
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"     # the shared data/ folder at the project root
FILE = DATA_DIR / "nova_loans.csv"

ID_COLUMN = "Loan_ID"                        # the identifier used everywhere in Module 2
SOURCE_ID_COLUMN = "Customer_ID"             # its name in the provided file

# Every column the analysis needs (apart from the identifier, which may have either name).
EXPECTED_COLUMNS = [
    "Customer_Type", "Annual_Income", "Employment_Length", "Debt_to_Income",
    "Credit_Score", "Existing_Loan", "Loan_Amount", "Loan_Term_Months", "Interest_Rate",
    "Collateral_Value", "Past_Default", "Sector_Risk", "Default_Flag",
]


def load_loans(path: Path = FILE) -> pd.DataFrame:
    """Load the loans, check the columns, and make Loan_ID the identifier.

    Steps:
      1. read the CSV;
      2. identifier: keep Loan_ID if present, else rename Customer_ID → Loan_ID;
         stop with a clear message if neither exists;
      3. check every other expected column is present;
      4. check Loan_ID is unique (one row per loan);
      5. store Customer_Type as a category (Retail / Corporate).
    """
    df = pd.read_csv(path)

    # ---- 2. The identifier --------------------------------------------------------------
    if ID_COLUMN in df.columns:
        # Already called Loan_ID (e.g. renamed at the evaluator's end). If both columns exist,
        # Loan_ID wins and Customer_ID is dropped, so there is only one identifier.
        df = df.drop(columns=[SOURCE_ID_COLUMN], errors="ignore")
    elif SOURCE_ID_COLUMN in df.columns:
        df = df.rename(columns={SOURCE_ID_COLUMN: ID_COLUMN})
    else:
        raise ValueError(f"No identifier column: expected '{ID_COLUMN}' or '{SOURCE_ID_COLUMN}' in {path.name}")

    # ---- 3. All other columns must be present ------------------------------------------------
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    # ---- 4. One row per loan ------------------------------------------------------------
    if df[ID_COLUMN].duplicated().any():
        raise ValueError("Loan_ID must be unique: each row is one loan")

    # ---- 5. Types; identifier first for readability ---------------------------------------
    df["Customer_Type"] = df["Customer_Type"].astype("category")
    return df[[ID_COLUMN] + [c for c in df.columns if c != ID_COLUMN]]


# ---- The model inputs (decision M2-11) ----------------------------------------------------
# Four standard lending ratios, each computed from the loan's own numbers (no other rows, no
# outcome), so they are known at application time and cannot leak. None uses Interest_Rate:
# the rate is the bank's own risk view (the champion), not an input to the challengers.
RATIO_FORMULAS = {
    "Loan_to_Value": "Loan_Amount ÷ Collateral_Value  (above 1 = loan larger than the asset pledged)",
    "Loan_to_Income": "Loan_Amount ÷ Annual_Income  (size of the loan against yearly income)",
    "Total_Debt_to_Income": "(Existing_Loan + Loan_Amount) ÷ Annual_Income  (all debt after this loan)",
    "Principal_to_Income": "(Loan_Amount ÷ (Loan_Term_Months ÷ 12)) ÷ Annual_Income  (share of yearly income "
                           "needed just to repay the principal)",
}

# The 11 given inputs (10 from the brief's list, minus Interest_Rate, plus Customer_Type).
GIVEN_INPUTS = ["Annual_Income", "Employment_Length", "Debt_to_Income", "Credit_Score", "Existing_Loan",
                "Loan_Amount", "Loan_Term_Months", "Collateral_Value", "Past_Default", "Sector_Risk",
                "Customer_Type"]
MODEL_INPUTS = GIVEN_INPUTS + list(RATIO_FORMULAS)          # 15 inputs in total


def add_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the loans with the four ratio columns added (formulas in RATIO_FORMULAS)."""
    out = df.copy()
    out["Loan_to_Value"] = out["Loan_Amount"] / out["Collateral_Value"]
    out["Loan_to_Income"] = out["Loan_Amount"] / out["Annual_Income"]
    out["Total_Debt_to_Income"] = (out["Existing_Loan"] + out["Loan_Amount"]) / out["Annual_Income"]
    out["Principal_to_Income"] = (out["Loan_Amount"] / (out["Loan_Term_Months"] / 12)) / out["Annual_Income"]
    return out


def data_report(df: pd.DataFrame) -> dict:
    """A short quality summary: size, gaps, default rate, mix of borrowers, loan book in ₹ crore."""
    return {
        "rows": len(df),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "default_rate": round(float(df["Default_Flag"].mean()), 3),
        "customer_type": df["Customer_Type"].value_counts().to_dict(),
        "loan_book_crore": round(float(df["Loan_Amount"].sum()) / 1e7, 1),   # 1 crore = 1,00,00,000 rupees
        "credit_score_range": (int(df["Credit_Score"].min()), int(df["Credit_Score"].max())),
        "debt_to_income_above_1": int((df["Debt_to_Income"] > 1).sum()),
        "negative_money_values": int((df[["Annual_Income", "Existing_Loan", "Loan_Amount",
                                          "Collateral_Value"]] < 0).sum().sum()),
    }


if __name__ == "__main__":
    loans = load_loans()
    print("Identifier column:", loans.columns[0])
    for key, value in data_report(loans).items():
        print(f"{key}: {value}")

"""
Module 1 — load and validate strategic_initiatives.csv
=======================================================

WHAT THIS FILE DOES
    Every Module 1 task starts by reading the same CSV file. This file does that once,
    in one place, so all tasks see exactly the same data with the same types.
    It provides:
      - load_initiatives():               read the CSV, check the columns are all there, set column types.
      - add_features(df):                 add derived columns (cash flows, 3-year NPV, revenue growth,
                                          cash return, ROI spread), listed in DERIVED_COLUMNS. Used by Task 1 and Task 2.
      - load_initiatives_with_features(): the two above in one call.
      - data_report():                    a short health check (row count, missing values, duplicates, ...).

    Why add_features lives here and not in a task notebook (project decision P-15):
    it is CODE needed by more than one task, so it is written once and imported by each task.
    A task notebook never runs another task notebook's cells.

UNITS
    All money columns (Initial_Investment, Revenue_Year1-3, Operating_Cost) are in ₹ lakh.
    1 lakh = ₹1,00,000 and 100 lakh = ₹1 crore. See project decision P-02.

HOW TO USE
    From another script or a notebook:
        from m01_data import load_initiatives
        df = load_initiatives()
    As a quick check from a terminal (any folder):
        python module_01_corporate_finance/helpers/m01_data.py
"""
# `Path` builds file paths that work on Windows, Mac, Linux and Colab alike.
from pathlib import Path

# pandas is the table library: a CSV becomes a "DataFrame" (rows and columns, like Excel).
import pandas as pd

# Finance formulas (yearly cash flows, 3-year NPV) from the other shared Module 1 script.
from m01_finance import cash_flows, npv

# ---------------------------------------------------------------------------------------
# Where the data lives
# ---------------------------------------------------------------------------------------
# __file__ is the path of THIS file:      <project folder>/module_01_corporate_finance/helpers/m01_data.py
# .resolve() turns it into a full path.
# .parents[0] = helpers folder, .parents[1] = module_01 folder, .parents[2] = project root.
# So DATA_DIR = <project folder>/data, no matter which folder you run Python from.
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
FILE = DATA_DIR / "strategic_initiatives.csv"

# The columns the brief lists for Module 1. If any is missing, the analysis cannot run,
# so we check for them on loading and stop with a clear message instead of failing later.
EXPECTED_COLUMNS = [
    "Initiative_ID", "Business_Unit", "Initial_Investment", "Revenue_Year1",
    "Revenue_Year2", "Revenue_Year3", "Operating_Cost", "Expected_ROI",
    "Business_Growth", "GDP_Growth", "Interest_Rate", "Competition_Index",
    "Risk_Rating", "Historical_Success",
]

# Derived columns that add_features() creates: name → formula. Task 2 picks its model inputs from
# this documented list. RULE: every derived column is row-by-row arithmetic on that initiative's own
# given numbers. Nothing here is learned from other rows (so it cannot leak between training and test
# folds), and nothing is built from the target Historical_Success (so the model is never handed the
# answer). Steps that learn from data (scaling, one-hot encoding, rebalancing) belong inside Task 2's
# scikit-learn Pipeline instead.
DERIVED_COLUMNS = {
    "CF1": "Revenue_Year1 − Operating_Cost  (₹ lakh)",
    "CF2": "Revenue_Year2 − Operating_Cost  (₹ lakh)",
    "CF3": "Revenue_Year3 − Operating_Cost  (₹ lakh)",
    "NPV_3yr": "−Initial_Investment + CF1/(1 + r) + CF2/(1 + r)² + CF3/(1 + r)³, r = Interest_Rate ÷ 100  (₹ lakh)",
    "Revenue_Growth_Y1_Y3": "(Revenue_Year3 ÷ Revenue_Year1 − 1) × 100  (%)",
    "Cash_Return_Pct": "average(CF1, CF2, CF3) ÷ Initial_Investment × 100  (% a year)",
    "ROI_Spread": "Expected_ROI − Interest_Rate  (% points; above 0 = passes the hurdle)",
}

# Risk_Rating has a natural order. Listing it here lets pandas sort Low → Medium → High
# (instead of alphabetical High → Low → Medium) in every table and chart.
RISK_LEVELS = ["Low", "Medium", "High"]


def load_initiatives(path: Path = FILE) -> pd.DataFrame:
    """Read strategic_initiatives.csv, check its columns, and set column types.

    Parameters
    ----------
    path : where the CSV is. Defaults to data/strategic_initiatives.csv.

    Returns
    -------
    A DataFrame with one row per initiative (180 rows). Money is in ₹ lakh.
    """
    # Step 1: read the CSV file into a DataFrame. pandas guesses each column's type
    # (numbers become float/int, text becomes "object").
    df = pd.read_csv(path)

    # Step 2: make sure every expected column is present.
    # set(A) - set(B) gives the names in A that are not in B.
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        # Stop immediately with a readable message rather than a confusing error later.
        raise ValueError(f"Missing columns: {sorted(missing)}")

    # Step 3: Risk_Rating becomes an *ordered category*. Two benefits:
    #   - groupby/sort follow Low → Medium → High;
    #   - any unexpected label (e.g. "high" in lower case) turns into a missing value (NaN),
    #     which data_report() and the Task 1 quality checks would then show.
    df["Risk_Rating"] = pd.Categorical(df["Risk_Rating"], categories=RISK_LEVELS, ordered=True)

    # Step 4: Business_Unit is a label with only 6 possible values, so "category" type
    # (saves memory and makes groupby faster and tidier).
    df["Business_Unit"] = df["Business_Unit"].astype("category")
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add the derived columns listed in DERIVED_COLUMNS. All come from given numbers; nothing is invented.

      CF1, CF2, CF3          yearly cash flow = revenue − yearly operating cost (₹ lakh)
      NPV_3yr                Net Present Value over the 3 years, at the row's Interest_Rate (₹ lakh)
      Revenue_Growth_Y1_Y3   how much revenue grows from Year 1 to Year 3, in %
      Cash_Return_Pct        average yearly cash flow ÷ investment, in % a year (a cash-based ROI)
      ROI_Spread             Expected_ROI − Interest_Rate, in % points (above 0 = passes the hurdle)

    No column is built from Historical_Success (the target), see the RULE above DERIVED_COLUMNS.
    """
    # Work on a copy so the caller's DataFrame is never changed by surprise.
    out = df.copy()

    # Yearly cash flows (see m01_finance.cash_flows). Assigning a 3-column table to 3 names.
    cf = cash_flows(out)
    out[["CF1", "CF2", "CF3"]] = cf

    # 3-year NPV (see m01_finance.npv): −investment + discounted CF1, CF2, CF3.
    out["NPV_3yr"] = npv(out)

    # Revenue growth: (Year 3 ÷ Year 1 − 1) × 100. Example: 111.5 → 149.1 gives +33.7%.
    out["Revenue_Growth_Y1_Y3"] = (out["Revenue_Year3"] / out["Revenue_Year1"] - 1) * 100

    # Cash return: mean of CF1-CF3 divided by the investment, × 100 for %.
    # cf.mean(axis=1) averages across the three columns for each row.
    out["Cash_Return_Pct"] = cf.mean(axis=1) / out["Initial_Investment"] * 100

    # Hurdle gap: how far the promised return is above (or below) the cost of money.
    out["ROI_Spread"] = out["Expected_ROI"] - out["Interest_Rate"]

    # Safety check: exactly the documented derived columns were added, nothing else.
    added = set(out.columns) - set(df.columns)
    assert added == set(DERIVED_COLUMNS), f"Derived columns differ from DERIVED_COLUMNS: {sorted(added)}"
    return out


def load_initiatives_with_features(path: Path = FILE) -> pd.DataFrame:
    """Load the data and add the derived columns in one call (what Task 1 and Task 2 start with)."""
    return add_features(load_initiatives(path))


def data_report(df: pd.DataFrame) -> dict:
    """Basic quality checks: size, missing values, duplicates, negative money, target rate.

    Returns a dictionary (name → value) so it can be printed or tested.
    """
    # The five money columns. None of them should ever be negative.
    money_cols = ["Initial_Investment", "Revenue_Year1", "Revenue_Year2", "Revenue_Year3", "Operating_Cost"]
    return {
        # How many initiatives (rows) we have.
        "rows": len(df),
        # df.isna() marks each empty cell True; .sum().sum() counts them across all columns.
        "missing_values": int(df.isna().sum().sum()),
        # .duplicated() is True for a repeat of an ID already seen; each initiative must be unique.
        "duplicate_ids": int(df["Initiative_ID"].duplicated().sum()),
        # (df[money_cols] < 0) marks negative cells; summing twice counts them.
        "negative_money_values": int((df[money_cols] < 0).sum().sum()),
        # Historical_Success is 1 or 0, so its average is the share of successes (0.767 = 76.7%).
        "success_rate": round(df["Historical_Success"].mean(), 3),
        # Total money asked by all initiatives. Divide ₹ lakh by 100 to get ₹ crore.
        "total_investment_crore": round(df["Initial_Investment"].sum() / 100, 1),
        # How many initiatives per business unit and per risk level.
        "business_units": df["Business_Unit"].value_counts().to_dict(),
        "risk_ratings": df["Risk_Rating"].value_counts().to_dict(),
    }


# This block runs only when the file is run directly (python m01_data.py),
# not when another file imports it.
if __name__ == "__main__":
    for key, value in data_report(load_initiatives()).items():
        print(f"{key}: {value}")

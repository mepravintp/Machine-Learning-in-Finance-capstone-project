"""
Module 1 — finance calculations (used in Task 1 for NPV, and fully in Task 3)
=============================================================================

WHAT THIS FILE DOES
    Turns each initiative's revenues and costs into money measures:
      cash_flows()        yearly cash flow = revenue − yearly operating cost
      discount_rate()     the yearly rate used to discount future cash (the row's Interest_Rate)
      npv()               Net Present Value over the 3 years given
      expected_npv()      the brief's formula: P(Success) × NPV
      hurdle_pass()       does the promised return beat the cost of money?
      break_even_years()  how many years of Year 3 cash flow are needed to pay back

    The Fund / Review / Reject rule itself (decision M1-06) is in the Task 3 notebook, where it
    is applied step by step; only calculations used by more than one task live here (P-15).

ALL MONEY IN ₹ LAKH (1 lakh = ₹1,00,000).

FORMULAS (plain form; docs/decisions.md M1-01 to M1-05 explain each choice)
    Cash flow in year t:   CFt = Revenue_Year t − Operating_Cost             (Operating_Cost is yearly, M1-01)
    Discount rate:         r   = Interest_Rate ÷ 100                          (each row's own rate, M1-02)
    NPV:                   NPV = −Initial_Investment + CF1/(1 + r) + CF2/(1 + r)² + CF3/(1 + r)³   (M1-03)
    Expected NPV:          Expected NPV = P(Success) × NPV                    (brief's formula)
    Hurdle pass:           Expected_ROI > Interest_Rate                       (M1-05)
    Break-even life:       smallest N where NPV of (CF1, CF2, CF3, CF3, ..., N years) ≥ 0   (M1-04)

WHY DISCOUNT?
    ₹100 today is worth more than ₹100 in a year, because today's ₹100 could be lent out at
    the interest rate. At 7%, ₹107 next year is worth ₹100 today: 107 ÷ 1.07 = 100.
    Dividing by (1 + r) once per year of waiting converts future cash into "today's money".
"""
import numpy as np      # fast maths on whole columns/arrays at once
import pandas as pd

# The three revenue columns, in year order. Used to build the yearly cash flows.
REVENUE_COLS = ["Revenue_Year1", "Revenue_Year2", "Revenue_Year3"]


def cash_flows(df: pd.DataFrame) -> pd.DataFrame:
    """Yearly cash flow = revenue − yearly operating cost, for years 1, 2 and 3.

    Example (initiative 1002): revenues 111.52, 141.54, 149.05; Operating_Cost 89.01
        → CF1 = 22.51, CF2 = 52.53, CF3 = 60.04  (₹ lakh)
    """
    # df[REVENUE_COLS] picks the three revenue columns (a 3-column table).
    # .sub(series, axis=0) subtracts Operating_Cost from every column, row by row
    # (axis=0 means "line the subtraction up by row").
    cf = df[REVENUE_COLS].sub(df["Operating_Cost"], axis=0)
    # Rename the columns so later code can say CF1, CF2, CF3.
    cf.columns = ["CF1", "CF2", "CF3"]
    return cf


def discount_rate(df: pd.DataFrame, risk_premium: dict | None = None) -> pd.Series:
    """The yearly discount rate as a decimal (7.02% → 0.0702), one per initiative.

    Base case (decision M1-02): each row's own Interest_Rate, the market cost of money.
    Optional: add a risk premium (extra return demanded for risk) by Risk_Rating, used ONLY
    for sensitivity tables, e.g. {"Low": 0.02, "Medium": 0.04, "High": 0.06}.
    """
    # Interest_Rate is stored in percent (e.g. 6.63). Divide by 100 for the decimal 0.0663.
    r = df["Interest_Rate"] / 100
    if risk_premium:
        # .astype(str) turns the category into plain text, .map(dict) looks each label up
        # in the dictionary, giving a premium per row; we add it to that row's rate.
        r = r + df["Risk_Rating"].astype(str).map(risk_premium)
    return r


def npv(df: pd.DataFrame, r: pd.Series | None = None) -> pd.Series:
    """Net Present Value over the 3 years of data (decision M1-03). One value per initiative.

    NPV = −Initial_Investment + CF1/(1 + r) + CF2/(1 + r)² + CF3/(1 + r)³

    Example (1002, r = 6.63%): −286.69 + 22.51/1.0663 + 52.53/1.0663² + 60.04/1.0663³ ≈ −169.9
    """
    # Use the base-case discount rate unless a different one is passed in (sensitivity runs).
    r = discount_rate(df) if r is None else r
    cf = cash_flows(df)
    # Start from minus the investment: money paid out today is already in today's value,
    # so it is not discounted. astype(float) avoids integer maths surprises.
    value = -df["Initial_Investment"].astype(float)
    # Add each year's cash flow after dividing by (1 + r) raised to the number of years waited.
    for t in range(1, 4):                       # t = 1, 2, 3
        value = value + cf[f"CF{t}"] / (1 + r) ** t
    return value


def expected_npv(npv_values: pd.Series, p_success: pd.Series) -> pd.Series:
    """Brief's formula: Expected NPV = P(Success) × NPV.

    P(Success) comes from the Task 2 model (a probability between 0 and 1).
    Example: NPV −170 and P(Success) 0.80 → Expected NPV = −136.
    """
    # Multiplication happens row by row because both are pandas Series with the same index.
    return p_success * npv_values


def hurdle_pass(df: pd.DataFrame) -> pd.Series:
    """True where the project's promised yearly return beats the yearly cost of money (M1-05).

    Expected_ROI and Interest_Rate are both in % a year, so they compare directly.
    """
    return df["Expected_ROI"] > df["Interest_Rate"]


def break_even_years(df: pd.DataFrame, r: pd.Series | None = None, max_years: int = 30) -> pd.Series:
    """How many years of cash flow are needed for NPV to reach 0 (decision M1-04).

    Years 1-3 use the given cash flows; after year 3 we repeat the Year 3 cash flow.
    This is a MEASUREMENT of how much a project relies on cash after the data ends, not a forecast.
    Returns NaN ("never") if it does not pay back within max_years (e.g. CF3 ≤ 0).

    Example (1002): after 3 years NPV is −169.9; adding 60.04 a year (discounted) reaches 0 in year 8.
    """
    r = discount_rate(df) if r is None else r
    # Convert to plain numpy arrays: a simple loop over numbers is clearer and fast enough for 180 rows.
    cf = cash_flows(df).to_numpy()                          # shape (rows, 3)
    invest = df["Initial_Investment"].to_numpy(dtype=float)
    rates = r.to_numpy()
    # Start with "never" (NaN) for every row; overwrite when a row breaks even.
    result = np.full(len(df), np.nan)
    for i in range(len(df)):                                # one initiative at a time
        value = -invest[i]                                  # running NPV, starting at −investment
        for t in range(1, max_years + 1):                   # year 1, 2, ..., max_years
            # min(t, 3) - 1 picks column 0, 1, 2 for years 1-3, then stays at column 2 (CF3).
            value += cf[i, min(t, 3) - 1] / (1 + rates[i]) ** t
            if value >= 0:                                  # paid back: record the year and stop
                result[i] = t
                break
    return pd.Series(result, index=df.index, name="Break_Even_Years")


if __name__ == "__main__":
    # Self-check against the worked example in docs/documentation.md (initiative 1002).
    from m01_data import load_initiatives

    data = load_initiatives()
    values = npv(data)
    be = break_even_years(data)
    # Find the row position of initiative 1002.
    row = data.index[data["Initiative_ID"] == 1002][0]
    print("Initiative 1002 NPV (₹ lakh):", round(values[row], 1), "| break-even years:", be[row])
    print("Initiatives with 3-year NPV > 0:", int((values > 0).sum()), "of", len(data))
    print("Median break-even years:", be.median(), "| never break even:", int(be.isna().sum()))
    print("Hurdle pass:", int(hurdle_pass(data).sum()), "of", len(data))

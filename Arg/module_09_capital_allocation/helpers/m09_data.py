"""
Module 9 — the evidence from Modules 1–8
=========================================

WHAT THIS FILE DOES
    Module 9 has no dataset of its own. Its "data" is what Modules 1–8 hand over: each module's
    final notebook step saves `module9_inputs.csv` with the same fields (return per ₹ deployed,
    bad-year result, capacity, evidence, horizon, gaps, controls), and its `key_numbers.json`
    holds the exact figures behind them.

    This helper:
      - evidence_table(root): every module's `module9_inputs.csv` in one table (with the module number);
      - load_inputs(root): the exact numbers Module 9 allocates with, read from the modules' key numbers
        and final files (never typed in by hand), as one dictionary;
      - data_report(root): a quick health check that every module's inputs exist.

HOW TO USE
    from m09_data import evidence_table, load_inputs
    python module_09_capital_allocation/helpers/m09_data.py      # health check
"""
import json
from pathlib import Path

import pandas as pd

MODULES = {1: "module_01_corporate_finance", 2: "module_02_credit_risk", 3: "module_03_fraud_detection",
           4: "module_04_customer_analytics", 5: "module_05_equity_markets", 6: "module_06_portfolio_optimization",
           7: "module_07_hft", 8: "module_08_derivatives"}
LAST_STEP = {1: "task3", 2: "task3", 3: "task4", 4: "task3", 5: "task2", 6: "partB", 7: "task2", 8: "task2"}


def _key(root: Path, n: int, folder: str = None) -> dict:
    """Read one module's key_numbers.json (from its last task unless another folder is named)."""
    return json.loads((root / MODULES[n] / "outputs" / (folder or LAST_STEP[n]) / "key_numbers.json").read_text(encoding="utf-8"))


def evidence_table(root: Path) -> pd.DataFrame:
    """All modules' standard Module 9 fields in one table, module number first."""
    parts = []
    for n, mod in MODULES.items():
        d = pd.read_csv(root / mod / "outputs" / LAST_STEP[n] / "module9_inputs.csv")
        d.insert(0, "Module", n)
        parts.append(d)
    return pd.concat(parts, ignore_index=True)


def load_inputs(root: Path) -> dict:
    """The numbers Module 9 allocates with, each read from the module that measured it.

    Returns a dictionary of plain numbers (% a year, ₹ crore) and small tables:
      initiatives_by_unit : Module 1, Fund + Review initiatives by business unit (capacity, expected return, 1-in-20 bad case)
      fund_now            : Module 1 initiatives approved individually ("Fund"), by unit, ₹ crore
      lending             : Module 2, approved and Review loans by type (return, bad year, severe year, ₹ crore)
      equity_return, equity_range, equity_swing_real, equity_crash : Module 6 (equal weight)
      put                 : Module 8, cost and crash result of 1-year puts at 100/90/80% floors
      equity_turnover, timing_saving_pct_of_orders : Modules 6 and 7 (order timing on equity trades)
      option_book_hedge   : Module 8, choice C (cash tied up, yearly cost) in ₹ crore
      fraud_cost          : Module 3, cost of fraud risk per ₹ moved, with the rule and with no screening
      wealth_fee          : Module 4, net fee yield on client balances
      risk_free           : Module 6's 6.8%
    """
    root = Path(root)
    k1, k2 = _key(root, 1), _key(root, 2)
    k6a, k6b = _key(root, 6, "partA"), _key(root, 6, "partB")
    k7, k8 = _key(root, 7), _key(root, 8)
    m1 = pd.read_csv(root / MODULES[1] / "outputs" / "task3" / "10c_business_unit_returns.csv")
    dec = pd.read_csv(root / MODULES[1] / "outputs" / "task3" / "FINAL_M1_T3_initiative_decisions.csv")
    m1 = m1[m1.Scope.str.startswith("Fund")].set_index("Business unit")
    fund_now = dec[dec.Decision == "Fund"].groupby("Business_Unit")["Investment (₹ lakh)"].sum() / 100
    lend = pd.read_csv(root / MODULES[2] / "outputs" / "task3" / "module9_lending_risk.csv")
    put = pd.read_csv(root / MODULES[8] / "outputs" / "task2" / "protect_equity_money.csv")
    eq_daily = pd.read_csv(root / MODULES[6] / "outputs" / "partA" / "daily_returns.csv", parse_dates=["Date"])["Equal weight"]
    m6in = pd.read_csv(root / MODULES[6] / "outputs" / "partB" / "module9_inputs.csv").iloc[0]
    m3in = pd.read_csv(root / MODULES[3] / "outputs" / "task4" / "module9_inputs.csv").iloc[0]
    m4in = pd.read_csv(root / MODULES[4] / "outputs" / "task3" / "module9_inputs.csv").iloc[0]
    m8in = pd.read_csv(root / MODULES[8] / "outputs" / "task2" / "module9_inputs.csv")
    run = m8in[m8in.Category.str.contains("option book")].iloc[0]
    lo, hi = (float(x) for x in m6in["Return range (% a year)"].split(" (")[0].split(" to "))
    return {
        "risk_free": 100 * k6a["risk_free"],
        "initiatives_by_unit": m1, "fund_now": fund_now,
        "lending": lend,
        "equity_return": float(m6in["Return per ₹ deployed (% a year)"]), "equity_range": (lo, hi),
        "equity_swing_real": 100 * k6b["vol_data_vs_real"]["Equal weight"][1], "equity_crash": -20.0,
        "equity_days": len(eq_daily),
        "put": put,
        "equity_turnover": k8["equity_turnover_year"], "timing_saving_pct_of_orders": k7["test2"]["saving_rupees_per_crore"] / 1e7 * 100,
        "option_book_hedge": {"cash_crore": float(run["Capacity (₹ crore)"]), "cost_pct_of_book": float(run["Return per ₹ deployed (% a year)"])},
        "fraud_cost": {"rule": -float(m3in["Return per ₹ deployed (% a year)"]), "bad": -float(m3in["Bad-year result per ₹ (% a year)"])},
        "wealth_fee": {"net": float(m4in["Return per ₹ deployed (% a year)"]), "bad": float(m4in["Bad-year result per ₹ (% a year)"])},
        "hft": {"pilot_net_per_crore": k7["test1"]["per_trade_rupees"]["After spread and charges"], "pilot_range_lakh": k7["test1"]["total_range_lakh"]},
        "m1_fund_crore": k1["fund_capital_crore"], "m1_review_crore": k1["review_capital_crore"],
        "m2_module9": k2.get("module9_lending"),
    }


def data_report(root: Path) -> dict:
    """Check every module has handed over its Module 9 inputs."""
    ev = evidence_table(root)
    return {"modules": int(ev.Module.nunique()), "rows": len(ev), "categories": ev.Category.tolist()}


if __name__ == "__main__":
    ROOT = Path(__file__).resolve().parents[2]
    for k, v in data_report(ROOT).items():
        print(k, ":", v)
    x = load_inputs(ROOT)
    print("Risk-free", x["risk_free"], "| equities", x["equity_return"], x["equity_range"], "| swing", round(x["equity_swing_real"], 1))

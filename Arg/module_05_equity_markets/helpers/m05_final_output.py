"""
Module 5 — final output workbook
================================

WHAT THIS FILE DOES
    Builds outputs/FINAL_M5_module_output.xlsx: the one file where Module 6, the Board, the presenter and the
    evaluator see everything Module 5 produced (project decision P-21). Tabs: Read me, Key numbers,
    Board actions, the task final files (plus the stock scorecard and the September 2026 picks),
    Hand-off to Module 6, Decisions, Evidence index.
    Module 5 hands to Module 6 (decision M5-15); its figures for Module 9 were replaced by Module 6's (M6-11).

HOW TO USE
    Run after Tasks 1–2: runner cell "Final output workbook", or python helpers/m05_final_output.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

here = Path(__file__).resolve() if "__file__" in globals() else Path.cwd() / "helpers" / "m05_final_output.py"
MODULE_DIR = here.parents[1]
sys.path.insert(0, str(MODULE_DIR.parent / "scripts"))
from final_workbook import build_workbook, handoff_row, key_row, action_row   # noqa: E402

OUT = MODULE_DIR / "outputs"
K1 = json.loads((OUT / "task1" / "key_numbers.json").read_text(encoding="utf-8"))
K2 = json.loads((OUT / "task2" / "key_numbers.json").read_text(encoding="utf-8"))
T1 = OUT / "task1" / "FINAL_M5_T1_return_predictions.csv"
T2 = OUT / "task2" / "FINAL_M5_T2_stock_selections.csv"
SC = OUT / "task2" / "stock_scorecard.csv"
SEP = OUT / "task2" / "september_2026_portfolio.csv"
TAB1, TAB2, TABS, TABP = "T1 return predictions", "T2 stock selections", "T2 stock scorecard", "T2 September 2026 picks"
p1, sel, sep = pd.read_csv(T1), pd.read_csv(T2), pd.read_csv(SEP)


def annual(monthly: pd.Series) -> float:
    """Compounded yearly return from monthly returns: (growth) ^ (12 ÷ months) − 1."""
    return float((1 + monthly).prod() ** (12 / len(monthly)) - 1)


ridge = sel[sel.Strategy == "Ridge regression"]
bench = ridge.groupby("Rebalance date")["Actual next-month return"].mean()           # all 15, equal weight
top5 = ridge[ridge.Selected == "Yes"].groupby("Rebalance date")["Actual next-month return"].mean()
ridge_sep = ", ".join(sep[(sep.Strategy == "Ridge regression") & (sep.Selected == "Yes")].sort_values("Rank").Ticker)
months = p1.Date.nunique()

handoff = pd.DataFrame([
    handoff_row("Model whose predictions Module 6 uses", "Ridge regression", "—", "Conclusion", TAB1, "Pred: Ridge regression",
                "The column, for all 43 months × 15 stocks", "M5-15", "Expected returns for the ML-predicted-return portfolio"),
    handoff_row("Are returns predictable from this data?", p1["Returns predictable"].iloc[0], "—", "Conclusion", TAB1, "Returns predictable",
                "Every row carries the verdict", "M5-08", "Treat the forecasts as having no proven skill"),
    handoff_row("Ridge's ranking skill (IC)", K1["models"]["Ridge regression"]["ic"], "−1 to +1 (0 = random)", "Measured", TAB1,
                "Pred: Ridge regression, Next_Month_Return", "Each month: rank correlation between the two columns across the 15 stocks; averaged over 43 months",
                "M5-08", f"0.03–0.05 would be useful; shuffled-returns p {K1['models']['Ridge regression']['shuffle_p']:.2f}"),
    handoff_row("Test months", months, "months (31 Jan 2023 – 31 Jul 2026, held to 31 Aug 2026)", "Measured", TAB1, "Date",
                "Count of distinct dates", "M5-04", "Module 6 backtests the same months"),
    handoff_row("Benchmark: all 15 stocks, equal weight, before costs", round(100 * annual(bench), 1), "% a year", "Measured", TAB2,
                "Rebalance date, Actual next-month return", "Rows where Strategy = Ridge regression: average of the 15 stocks per date, compounded over 43 months ^ (12 ÷ 43) − 1",
                "M5-11", "Module 6's equal-weight portfolio should match this before costs"),
    handoff_row("Ridge's top 5, equal weight, before costs", round(100 * annual(top5), 1), "% a year", "Measured", TAB2,
                "Rebalance date, Selected, Actual next-month return", "Rows where Strategy = Ridge regression and Selected = Yes: average per date, compounded",
                "M5-05, M5-12", "No top-5 portfolio beats the benchmark beyond luck (p ≥ 0.40)"),
    handoff_row("Ridge's picks for September 2026", ridge_sep, "—", "Conclusion (not a recommendation)", TABP, "Strategy, Ticker, Selected, Rank",
                "Rows where Strategy = Ridge regression and Selected = Yes, by Rank", "M5-17", "The models' picks; the evidence favours holding all 15"),
    handoff_row("Module 9 inputs: Equity investments: ML stock selection (extra over holding all 15)", "0.0 (bad year -7.42)", "% a year per ₹",
                "Measured + Assumption", "Module 9 inputs", "Return per ₹ deployed, Bad-year result per ₹", "Final notebook step 'What goes to Module 9'", "M5-19",
                "Standard fields for Module 9; gaps marked as assumptions"),
    handoff_row("Assumptions behind these figures", "Monthly rebalancing; walk-forward with 24 training months; before trading costs; 15 stocks; data looks synthetic (random macro columns, independent stocks)",
                "—", "Assumption", "—", "—", "—", "M5-03, M5-04, M5-13", "Module 6 applies trading costs"),
])

top = K2["top5"]
key_numbers = pd.DataFrame([
    key_row("Test months × stocks", f"{months} × 15 = {len(p1)}", "predictions per model", "Walk-forward: each month predicted from earlier months only", "—",
            "68 month-ends − 1 − 24 training months", TAB1),
    key_row("Inputs that predict next month's return", "0 of 66 tests", "—", "22 inputs × next day, week, month", "More would be better; none here",
            "Line 0.05 ÷ 66 = 0.0008", "Task 1"),
    key_row("Models' ranking skill (IC)", " / ".join(f"{m.split()[0]} {K1['models'][m]['ic']:+.3f}" for m in ("Linear regression", "Ridge regression", "Random forest", "LightGBM")),
            "−1 to +1 (0 = random)", "How well each model orders the 15 stocks each month", "0.03–0.05 is useful; luck alone gives −0.08 to +0.08",
            "Monthly rank correlation, averaged", "Task 1"),
    key_row("Benchmark: all 15, equal weight", round(100 * K2["benchmark_annual"], 1), "% a year, before costs", "What holding everything earned",
            "—", "Compounded over 43 months", TAB2),
    key_row("Top-5 portfolios' yearly return", " / ".join(f"{m.split()[0]} {100 * top[m]['annual']:.1f}%" for m in top), "% a year",
            "Each model's top 5, 20% each", "Higher is better; none beats 15.8% beyond luck (p ≥ 0.40)", "Compounded", TAB2),
    key_row("Random top 5: luck's 95% range", f"{100 * K2['luck_range_top5'][0]:.1f}% to {100 * K2['luck_range_top5'][1]:.1f}%", "% a year",
            "What 1,000 random top-5 portfolios made", "Every strategy sits inside", "1,000 random picks", "Task 2"),
    key_row("Risk: top 5 vs all 15", f"{100 * min(t['vol'] for t in top.values()):.1f}%–{100 * max(t['vol'] for t in top.values()):.1f}% vs {100 * K2['benchmark_vol']:.1f}%",
            "% a year (volatility)", "Holding 5 instead of 15 swings about 1.8 times as much", "Lower is better", "sd of monthly returns × √12", "Task 2"),
    key_row("Best and worst stock", f"{K2['scorecard']['best'][0]} {100 * K2['scorecard']['best'][1]:+.1f}% / {K2['scorecard']['worst'][0]} {100 * K2['scorecard']['worst'][1]:+.1f}%",
            "% a year", "The spread between stocks", "—", "Compounded daily returns, test period", TABS),
    key_row("Spread between stocks vs luck", f"{100 * K2['scorecard']['spread']:.1f}% (luck {100 * K2['scorecard']['luck_range'][0]:.1f}%–{100 * K2['scorecard']['luck_range'][1]:.1f}%)",
            "sd of the 15 yearly returns", "Inside luck's range: winners and losers are what chance produces", "—", "2,000 simulated sets of 15 stocks", TABS),
    key_row("Did winners stay winners?", f"{K2['scorecard']['halves_rank_corr']:+.2f} (p {K2['scorecard']['halves_p']:.2f})", "rank correlation, first vs second half",
            "+1 = same order; 0 = unrelated", "Here unrelated", "Spearman correlation", TABS),
])

board_actions = pd.DataFrame([
    action_row(1, "Don't use these models to pick stocks", "Top 5 earned 8.3%–19.1% vs 15.8% for all 15, none beyond luck",
               "They add about 1.8× the risk and 11–16 portfolio turns a year", TAB2),
    action_row(2, "Hold the stocks broadly: equal weight, or Module 6's optimised mix", "15.8% a year before costs, the least risk", "No model beats it", "Module 6"),
    action_row(3, "Don't fund an ML stock-picking programme on this evidence", "A small edge (IC 0.03–0.05) would be worth ₹3–5 crore a year on ₹100 crore",
               "It could exist and stay hidden in 43 months of 15 stocks", "Task 1"),
    action_row(4, "Re-test with real market data, more stocks, a longer history and fundamentals", "—", "This data's macro columns are random and stocks independent", "Report §9"),
])

read_me = {
    "question": "NovaFin manages an equity portfolio. The investment committee wants to know: Can ML identify stocks with superior future returns?",
    "answer": ["On this data, no. No model predicts which stocks will do better (ICs −0.049 to +0.005, all inside luck's range).",
               "No portfolio of the models' top picks beats holding all 15 stocks beyond luck (15.8% a year before costs), at 3, 5 or 7 stocks, monthly or quarterly.",
               "The stocks' winners and losers are what chance produces; holding all 15 owns the winners without having to find them."],
    "tasks": [("Task 1 — Predict future returns", "FINAL_M5_T1_return_predictions.csv", "every model's walk-forward prediction, 43 months × 15 stocks"),
              ("Task 2 — Stock ranking", "FINAL_M5_T2_stock_selections.csv", "rank, selected, weight, reason, and whether each pick beat the average")],
    "how_to_read": ["Returns are monthly fractions in the task tabs (0.03 = 3%).", "This module hands to Module 6; Module 9's equity figures come from Module 6's workbook.",
                    "Full explanation: reports/module_5_report.md."],
}
task_tabs = [(TAB1, T1, "Task 1: every model's predicted next-month return per stock and month"),
             (TAB2, T2, "Task 2: every strategy × month × stock: rank, selected, weight, reason, outcome"),
             (TABS, SC, "Task 2: the 15 stocks best to worst, with what happened to each in words"),
             (TABP, SEP, "Task 2: every strategy's ranking on 31 Aug 2026 (the latest rebalance date)")]

# Every column of every task tab, in one plain sentence (shown in the Read me tab)
COLUMN_GUIDE = {'Date': 'The month-end on which the prediction was made', 'Ticker': 'The stock', 'Sector': "The stock's industry", 'Next_Month_Return': 'What the stock actually did over the next month (0.03 = rose 3%)', 'Pred: Predict zero': 'Benchmark: predicts 0% for every stock', 'Pred: Past average': "Benchmark: each stock's average monthly return so far", 'Pred: Linear regression': "Linear regression's forecast of next month's return", 'Pred: Ridge regression': "Ridge regression's forecast (the model passed to Module 6)", 'Pred: Random forest': "Random forest's forecast", 'Pred: LightGBM': "LightGBM's forecast", 'Pred: Ridge regression, all 22 inputs': 'Check: ridge using all 22 inputs, including the random macro columns', 'Pred: LightGBM, all 22 inputs': 'Check: LightGBM using all 22 inputs', 'Returns predictable': 'The verdict: no model beats luck', 'Rebalance date': 'The month-end when the portfolio is reset', 'Held until': 'The next month-end, when the holding ends', 'Strategy': 'Which ranker chose the stocks (a model or the past-average benchmark)', 'Predicted return': "That ranker's forecast of the stock's next-month return", 'Rank': "The stock's position among the 15 by that forecast: 1 = highest", 'Selected': 'Yes if in the top 5 and bought', 'Weight': 'Share of the money in the stock (0.2 = 20%)', 'Reason': "Why it was or wasn't bought, in words", 'Actual next-month return': 'What the stock actually did over the month', "Stock's return vs the 15-stock average (points)": 'Its return minus the average of all 15 that month; positive = beat the average', 'Beat the 15-stock average that month?': 'Yes or No', 'Ranking skill (Task 1)': 'Reminder: no model ranks stocks better than luck', 'Rank (best = 1)': 'Position from best to worst yearly return over the test period', 'Yearly return': 'Steady yearly growth over 31 Jan 2023 – 31 Aug 2026 (0.45 = 45% a year)', 'Yearly swing': 'How much the price swings in a year (volatility); higher = bumpier', 'Worst fall': 'The biggest drop from a previous high', 'First half (yearly)': 'Yearly return over the first half of the test period', 'Second half (yearly)': 'Yearly return over the second half', '2021–22 (yearly)': 'Yearly return before the test period', 'Average month vs the 15-stock average': 'How far its typical month was above or below the 15-stock average', 'Forecast-tracking (ridge)': "How closely ridge's forecasts followed what the stock did: −1 to +1, 0 = no link", 'September 2026 picks (of 5 strategies)': 'How many of the 5 strategies picked it for September 2026', 'Return per unit of risk': 'Yearly return ÷ yearly swing; higher is better', 'Months in top 5: Past average': 'Months (of 43) the past-average ranker held it', 'Months in top 5: Linear regression': 'Months linear regression held it', 'Months in top 5: Ridge regression': 'Months ridge regression held it', 'Months in top 5: Random forest': 'Months random forest held it', 'Months in top 5: LightGBM': 'Months LightGBM held it', 'What happened, in words': "The stock's story in one sentence"}

if __name__ == "__main__" or "get_ipython" in globals():
    path = build_workbook(MODULE_DIR, 5, read_me, key_numbers, board_actions, task_tabs, handoff, column_guide=COLUMN_GUIDE, receiver="Module 6",
                          m9_inputs=pd.read_csv(MODULE_DIR / "outputs" / 'task2/module9_inputs.csv'))
    print("Saved:", path.name)
    print(handoff[["Figure", "Value", "Unit"]].to_string(index=False))

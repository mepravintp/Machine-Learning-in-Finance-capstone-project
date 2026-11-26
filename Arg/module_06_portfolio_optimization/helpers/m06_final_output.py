"""
Module 6 — final output workbook
================================

WHAT THIS FILE DOES
    Builds outputs/FINAL_M6_module_output.xlsx: the one file where Module 9, the Board, the presenter and the
    evaluator see everything Module 6 produced, with the equity hand-off for Modules 5 and 6 combined
    (project decision P-21; decisions M6-11, M6-12). Tabs: Read me, Key numbers, Board actions, Part A and
    Part B final files (plus the strategy comparison, cost checks and daily returns the hand-off rests on),
    Hand-off to Module 9, Decisions, Evidence index.

    Every hand-off figure is computed here from those tabs' rows, as its "How it comes from the rows" says.

HOW TO USE
    Run after Parts A and B: runner cell "Final output workbook", or python helpers/m06_final_output.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

here = Path(__file__).resolve() if "__file__" in globals() else Path.cwd() / "helpers" / "m06_final_output.py"
MODULE_DIR = here.parents[1]
sys.path.insert(0, str(MODULE_DIR.parent / "scripts"))
from final_workbook import build_workbook, handoff_row, key_row, action_row   # noqa: E402

OUT = MODULE_DIR / "outputs"
YEAR, MONTH_DAYS, RISK_FREE = 261, 22, 0.068          # decisions M6-03, M6-05; 22 = 261 ÷ 12 rounded
TA = OUT / "partA" / "FINAL_M6_A_portfolio_weights.csv"
TC = OUT / "partA" / "strategy_comparison.csv"
TK = OUT / "partA" / "cost_checks.csv"
TD = OUT / "partA" / "daily_returns.csv"
TB = OUT / "partB" / "FINAL_M6_B_risk_summary.csv"
TABA, TABC, TABK, TABD, TABB = "A portfolio weights", "A strategy comparison", "A cost checks", "A daily returns", "B risk summary"
EW, ML = "Equal weight", "ML (ridge forecasts)"
w, comp, costs, daily, risk = (pd.read_csv(f) for f in (TA, TC, TK, TD, TB))
daily["Date"] = pd.to_datetime(daily["Date"])


def cagr(r: pd.Series) -> float:
    """(end ÷ start) ^ (261 ÷ days) − 1."""
    return float((1 + r).prod() ** (YEAR / len(r)) - 1)


def risk_value(measure: str, strategy: str = EW) -> float:
    return float(risk[(risk.Strategy == strategy) & (risk.Measure == measure)].Value.iloc[0])


r_ew = daily[EW]
ret_after = cagr(r_ew)
ret_before = float(costs[(costs.Strategy == EW) & (costs["Cost per ₹ traded"] == 0)].CAGR.iloc[0])
months = w[["Rebalance date", "Held until"]].drop_duplicates().apply(pd.to_datetime)
monthly = np.array([(1 + r_ew[(daily.Date > a) & (daily.Date <= b)]).prod() - 1 for a, b in months.values])
half_width = 1.96 * monthly.std(ddof=1) / np.sqrt(len(monthly)) * 12
swing_real = risk_value("Yearly swing (volatility), real-market correlation") / 100
sd_month_real = swing_real / np.sqrt(YEAR) * np.sqrt(MONTH_DAYS)
cvar_month_real = -(MONTH_DAYS * r_ew.mean() - sd_month_real * 2.063) * 100
ml_gap = 100 * ((1 + daily[ML]).prod() - (1 + r_ew).prod())
years = len(daily) / YEAR
REAL = "Measure = '{m}' and Strategy = Equal weight"

handoff = pd.DataFrame([
    handoff_row("Recommended equity portfolio", "Equal weight: 15 stocks at 6.67% each, reset monthly", "—", "Conclusion", TABA, "Strategy, Weight",
                "Rows where Strategy = Equal weight: Weight = 0.0667 for every stock and month", "M6-11", "Hold broadly; no model-driven stock-picking"),
    handoff_row("Expected return, after trading costs", round(100 * ret_after, 1), "% a year", "Measured (43 months)", TABD, EW,
                "Compound the column's 934 daily returns: (product of 1 + r) ^ (261 ÷ 934) − 1", "M6-11", "Return assumption for the equity bucket"),
    handoff_row("95% range of that return", f"{100 * (ret_after - half_width):.1f} to {100 * (ret_after + half_width):.1f}", "% a year", "Measured", f"{TABD} + {TABA}",
                f"{EW} (daily); Rebalance date, Held until", "Compound the daily returns into the 43 holding months; return ± 1.96 × sd of those months ÷ √43 × 12",
                "M6-12", "The 15.6% is uncertain: test the allocation at the low end"),
    handoff_row("Return before trading costs", round(100 * ret_before, 1), "% a year", "Measured", TABK, "Cost per ₹ traded, Strategy, CAGR",
                "Row where Cost per ₹ traded = 0 and Strategy = Equal weight", "M5-11, M6-04", "Cross-check: Module 5 gives 15.8% too"),
    handoff_row("Trading-cost drag", round(100 * (ret_before - ret_after), 1), "% a year", "Measured", f"{TABK} + {TABD}", "as above",
                "Return before costs − return after costs", "M6-04", "Already in the 15.6%"),
    handoff_row("Yearly swing (volatility), real-market", round(100 * swing_real, 1), "% a year", "Stress estimate (correlation 0.4 assumed)", TABB, "Measure, Strategy, Value",
                REAL.format(m="Yearly swing (volatility), real-market correlation"), "M6-06, M6-11", "Use this for equity risk"),
    handoff_row("Yearly swing (volatility), this data", round(float(comp[comp.Strategy == EW].Volatility.iloc[0]) * 100, 1), "% a year",
                "Measured; understates real risk (stocks independent here)", TABC, "Strategy, Volatility", "Row where Strategy = Equal weight",
                "M6-11", "Reference only; don't size the allocation on it"),
    handoff_row("Sharpe ratio at real-market risk", round((ret_after - RISK_FREE) / swing_real, 2), "ratio", "Stress estimate", f"{TABD} + {TABB}",
                "as above", "(return after costs − 6.8% risk-free) ÷ real-market swing", "M6-12", "Compare with other businesses' return per unit of risk"),
    handoff_row("VaR 95%, 1 day, real-market", round(risk_value("VaR 95%, 1 day, real-market correlation"), 2), "₹ crore per ₹100 crore", "Stress estimate",
                TABB, "Measure, Strategy, Value", REAL.format(m="VaR 95%, 1 day, real-market correlation"), "M6-06", "Daily risk limit"),
    handoff_row("VaR 95%, 1 month, real-market", round(risk_value("VaR 95%, 1 month, real-market correlation"), 2), "₹ crore per ₹100 crore", "Stress estimate",
                TABB, "Measure, Strategy, Value", REAL.format(m="VaR 95%, 1 month, real-market correlation"), "M6-06, M6-11", "Monthly risk budget for the equity bucket"),
    handoff_row("CVaR 95%, 1 month, real-market", round(cvar_month_real, 2), "₹ crore per ₹100 crore", "Stress estimate", f"{TABD} + {TABB}", f"{EW}; real-market swing",
                "−(22 × average daily return − 1-month real-market sd × 2.063) × 100; sd = swing ÷ √261 × √22; 2.063 = average depth of a bell curve's worst 5%",
                "M6-12", "Average loss in the worst 1 month in 20"),
    handoff_row("Loss if every stock falls 20%", round(risk_value("Every stock falls 20%"), 1), "₹ crore per ₹100 crore", "Stress estimate (scenario)",
                TABB, "Measure, Strategy, Value", REAL.format(m="Every stock falls 20%"), "M6-06", "Crash loss diversification can't remove; size the allocation or hedge (Module 8)"),
    handoff_row("Worst month seen in the data", round(risk_value("Worst month"), 2), "₹ crore per ₹100 crore", "Measured; understates real risk",
                TABB, "Measure, Strategy, Value", REAL.format(m="Worst month"), "M6-06", "Reference only"),
    handoff_row("Extra return from ML stock-picking", 0, "% a year", "Conclusion", TABC, "Strategy, p (vs equal weight)",
                "No strategy beats equal weight beyond luck (every p ≥ 0.39; line 0.017); Module 5: no model ranks better than random",
                "M5-08, M6-10, M6-11", "Allocate no capital on an ML equity edge"),
    handoff_row("Cost of following the ML portfolio instead", round(ml_gap, 1), f"₹ crore per ₹100 crore over {years:.2f} years", "Measured", TABD, f"{ML}, {EW}",
                "₹100 crore × (product of 1 + r for ML − product of 1 + r for Equal weight)", "M6-08", "The ₹ answer to 'why not ML here?'"),
    handoff_row("Module 9 inputs: Equity investments (equal weight, 15 stocks)", "15.6 (bad year -16.24)", "% a year per ₹",
                "Measured + Assumption", "Module 9 inputs", "Return per ₹ deployed, Bad-year result per ₹", "Final notebook step 'What goes to Module 9'", "M6-14",
                "Standard fields for Module 9; gaps marked as assumptions"),
    handoff_row("Assumptions behind these figures", "Trading cost 0.15% per ₹ traded; risk-free 6.8%; 43 test months (31 Jan 2023 – 31 Aug 2026); 15 stocks; data looks synthetic (independent stocks, random macro columns); no dividends",
                "—", "Assumption", "—", "—", "—", "M6-04, M6-05, M6-09", "State these when using the figures"),
])

c = comp.set_index("Strategy")
key_numbers = pd.DataFrame([
    key_row("Test period", f"{len(daily)} days = {years:.2f} years", "—", "31 Jan 2023 – 31 Aug 2026, reset every month-end", "—", "261 trading days a year in this data", TABD),
    key_row("Yearly return after costs", " / ".join(f"{s.split(' (')[0]} {100 * c.loc[s, 'CAGR']:.1f}%" for s in c.index), "% a year",
            "Each strategy's compounded growth", "Higher is better", "(end ÷ start) ^ (261 ÷ days) − 1", TABC),
    key_row("Sharpe ratio", " / ".join(f"{s.split(' (')[0]} {c.loc[s, 'Sharpe']:.2f}" for s in c.index), "ratio",
            "Return above 6.8% per unit of swing", "Higher is better; above 1 good", "(return − 6.8%) ÷ volatility", TABC),
    key_row("Worst fall (maximum drawdown)", " / ".join(f"{s.split(' (')[0]} {100 * c.loc[s, 'Maximum drawdown']:.1f}%" for s in c.index), "%",
            "Worst fall from a previous high", "Closer to 0 is better", "min(value ÷ running high − 1)", TABC),
    key_row("Traded a month (turnover)", " / ".join(f"{s.split(' (')[0]} {100 * c.loc[s, 'Turnover a month']:.0f}%" for s in c.index), "% of the portfolio",
            "Buys + sells at each reset", "Lower is cheaper", "sum of |new − old weight|", TABC),
    key_row("p vs equal weight", " / ".join(f"{s.split(' (')[0]} {c.loc[s, 'p (vs equal weight)']:.2f}" for s in c.index if s != EW), "0–1",
            "Chance luck gives a gap this big", "Below 0.017 would be real; none is", "t-test of 43 monthly differences", TABC),
    key_row("Minimum-risk Markowitz vs equal weight", "Identical (largest weight gap 0.00%)", "—", "With alike, independent stocks, spreading evenly is the lowest-risk mix",
            "—", "Optimiser on the 1-year covariance", "Part A"),
    key_row("1-day VaR 95%: equal weight vs others", f"₹{risk_value('VaR 95%, 1 day'):.2f} crore vs ₹{min(risk_value('VaR 95%, 1 day', s) for s in c.index if s != EW):.2f}–{max(risk_value('VaR 95%, 1 day', s) for s in c.index if s != EW):.2f} crore",
            "₹ crore per ₹100 crore", "Loss not exceeded on 95% of days", "Lower is better", "5th percentile of daily returns", TABB),
    key_row("Yearly swing: this data vs real-market (equal weight)", f"{risk_value('Yearly swing (volatility), this data'):.1f}% vs {100 * swing_real:.1f}%", "% a year",
            "How much this data's independent stocks understate risk (× 2.5)", "—", "Stress test (c): every correlation set to 0.4", TABB),
    key_row("Cost of following the ML portfolio", round(ml_gap, 1), "₹ crore per ₹100 crore", "vs equal weight over 3.58 years", "—", "Difference in end values", TABD),
])

board_actions = pd.DataFrame([
    action_row(1, "Hold the equity portfolio equally weighted, reset monthly", f"₹100 crore → ₹{100 * (1 + r_ew).prod():.1f} crore after costs; about 0.2% a year in trading costs",
               "Best return per unit of risk, smallest falls, lowest cost", TABC),
    action_row(2, "Don't optimise on expected returns from this data", f"The ML portfolio cost ₹{abs(ml_gap):.1f} crore vs equal weight",
               "Neither past averages nor ML forecasts predict; optimisers concentrate on noise", TABA),
    action_row(3, "Plan equity risk at real-market levels", f"About {100 * swing_real:.0f}% yearly swing; about ₹{risk_value('VaR 95%, 1 month, real-market correlation'):.0f} crore 1-month VaR per ₹100 crore",
               "This data's 7.8% swing relies on independent stocks", TABB),
    action_row(4, "Control crash risk through the size of the equity allocation (Module 9) and hedging (Module 8)", "₹20 crore per ₹100 crore in a 20% fall",
               "Diversification can't reduce a fall in every stock", TABB),
    action_row(5, "Re-test minimum-risk Markowitz on real market data", "—", "There stocks differ in risk and move in groups", "Report §8"),
])

read_me = {
    "question": "One must transform ML predictions into an actual portfolio. Compare strategies- Equal-weight portfolio, Traditional Markowitz portfolio, ML-predicted-return portfolio. Perform backtesting to demonstrate performance and generate performance metrics.",
    "answer": [f"Hold the equity portfolio equally weighted: it earned {100 * ret_after:.1f}% a year after costs with the best return per unit of risk and the smallest falls.",
               "Markowitz (past returns) earned slightly more but not beyond luck (p 0.79) and with 1.5× the swing; the ML-predicted-return portfolio did worst.",
               f"This data understates real risk about 2.5 times: Module 9 should plan with a {100 * swing_real:.1f}% yearly swing, not 7.8%."],
    "tasks": [("Part A — Three portfolios, backtested", "FINAL_M6_A_portfolio_weights.csv", "every strategy's weights per month and stock, with both forecasts, trades, outcome and reason"),
              ("Part B — VaR and stress tests", "FINAL_M6_B_risk_summary.csv", "every risk figure per strategy, with basis, rank and meaning in words")],
    "how_to_read": ["Weights and returns are fractions (0.0667 = 6.67%); risk figures are ₹ crore per ₹100 crore unless the Unit says %.",
                    "The Hand-off is the final equity hand-off to Module 9 for Modules 5 and 6 combined.", "Full explanation: reports/module_6_report.md."],
}
task_tabs = [(TABA, TA, "Part A: every strategy × month × stock: weight, forecasts, rank, trade, outcome, reason"),
             (TABC, TC, "Part A: every measure per strategy (the backtest results)"),
             (TABK, TK, "Part A: yearly return and Sharpe at trading costs 0%, 0.10%, 0.15%, 0.30%"),
             (TABD, TD, "Part A: each strategy's daily return after costs (934 days)"),
             (TABB, TB, "Part B: every risk figure per strategy, in words")]

# Every column of every task tab, in one plain sentence (shown in the Read me tab)
COLUMN_GUIDE = {'Rebalance date': 'The month-end when the portfolio is reset', 'Held until': 'The next month-end', 'Strategy': 'Equal weight, Markowitz (past returns), ML (ridge forecasts) or Top 5 (Module 5)', 'Ticker': 'The stock', 'Sector': "The stock's industry", 'Weight': 'Share of the money put in the stock (0.0667 = 6.67%)', 'Weight vs equal weight (points)': 'How far above (+) or below (−) the even 6.67% share', 'Past-year average (a month)': "The stock's average monthly return over the past year: what Markowitz expects", 'Ridge forecast (a month)': "Ridge's forecast of next month's return: what the ML portfolio expects", 'Expected return this strategy used': 'The forecast this strategy acted on', 'Rank of that expected return (1 = highest)': 'Where that forecast ranks among the 15 stocks', 'Bought (+) / sold (−) at this reset': 'How much was bought or sold at the month-end, as a share of the portfolio', 'Actual return that month': 'What the stock actually did that month', 'Contribution to portfolio return (weight × actual)': "How much the stock added to (+) or took from (−) the portfolio's month", 'Reason in words': 'Why the strategy held this much, and how it turned out', 'CAGR': 'Steady yearly growth rate after trading costs (0.156 = 15.6% a year)', 'Volatility': 'How much returns swing in a year; lower = calmer', 'Sharpe': 'Return above a safe 6.8% bond, per unit of swing; above 1 is good', 'Sortino': 'Like Sharpe, counting only downward swings', 'Maximum drawdown': 'The worst fall from a previous high', 'Calmar': 'Yearly return ÷ the worst fall; higher is better', 'VaR 95% (1 day, historical)': 'Loss not exceeded on 95% of days, from the actual days', 'VaR 95% (1 day, parametric)': 'The same, from a bell curve', 'CVaR 95% (1 day)': 'Average loss on the worst 5% of days', 'Turnover a month': 'Share of the portfolio bought plus sold at each month-end', 'Largest weight (average)': 'The biggest single holding, averaged over the months', 'Stocks held above 1% (average)': 'How many stocks hold more than 1% of the money', 'Tracking error': "How far the strategy's returns wander from equal weight's in a year", 'Information ratio': 'Extra yearly return over equal weight ÷ tracking error; 0.5 is good', 'p (vs equal weight)': 'Chance luck alone gives a gap this big; below 0.017 would be real', 'Months beating equal weight': 'Months (of 43) the strategy did better than equal weight', 'Beats equal weight?': 'Yes only if better beyond luck', 'Cost per ₹ traded': 'Trading cost assumed: 0.0015 = 0.15% of every ₹ bought or sold', 'Date': 'The trading day', 'Equal weight': "That day's return of the equal-weight portfolio, after costs", 'Markowitz (past returns)': "That day's return of the Markowitz portfolio", 'ML (ridge forecasts)': "That day's return of the ML portfolio", 'Top 5 (Module 5)': "That day's return of Module 5's top 5", 'Measure': 'Which risk figure', 'Value': 'The figure, in the Unit shown', 'Unit': '₹ crore lost per ₹100 crore invested, or % a year', 'Basis': 'Actual days, a bell curve, or a stress scenario', 'Rank among the 4 (1 = smallest)': '1 = the smallest loss of the 4 strategies', 'What it means, in words': 'The figure as one plain sentence'}

if __name__ == "__main__" or "get_ipython" in globals():
    path = build_workbook(MODULE_DIR, 6, read_me, key_numbers, board_actions, task_tabs, handoff, column_guide=COLUMN_GUIDE, receiver="Module 9",
                          m9_inputs=pd.read_csv(MODULE_DIR / "outputs" / 'partB/module9_inputs.csv'))
    print("Saved:", path.name)
    print(handoff[["Figure", "Value", "Unit"]].to_string(index=False))

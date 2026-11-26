"""
Module 8 — final output workbook
================================

WHAT THIS FILE DOES
    Builds outputs/FINAL_M8_module_output.xlsx: the one file where Module 9, the Board, the presenter and the
    evaluator see everything Module 8 produced (project decision P-21). Tabs: Read me (with a column guide),
    Key numbers, Board actions, the Task 1 and Task 2 final files (plus pricing by stock, hedging choices, scenarios, choice rule, hedge by stock), Hand-off to
    Module 9, Decisions, Evidence index. Hand-off figures are computed here from the task tabs' rows.

HOW TO USE
    Run after Tasks 1–2: runner cell "Final output workbook", or python helpers/m08_final_output.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

here = Path(__file__).resolve() if "__file__" in globals() else Path.cwd() / "helpers" / "m08_final_output.py"
MODULE_DIR = here.parents[1]
sys.path.insert(0, str(MODULE_DIR.parent / "scripts"))
from final_workbook import build_workbook, handoff_row, key_row, action_row   # noqa: E402

OUT = MODULE_DIR / "outputs"
K1 = json.loads((OUT / "task1" / "key_numbers.json").read_text(encoding="utf-8"))
K2 = json.loads((OUT / "task2" / "key_numbers.json").read_text(encoding="utf-8"))
T1 = OUT / "task1" / "FINAL_M8_T1_bs_benchmark.csv"
T2 = OUT / "task2" / "FINAL_M8_T2_ml_pricing.csv"
TH = OUT / "task2" / "hedge_scenarios.csv"
TC = OUT / "task2" / "hedging_choices.csv"
TR = OUT / "task2" / "hedging_choice_rule.csv"
TS = OUT / "task2" / "hedge_by_stock.csv"
TP = OUT / "task2" / "test_by_stock.csv"
TAB1, TAB2, TABH = "T1 BS benchmark", "T2 ML pricing", "T2 hedge scenarios"
TABC, TABR, TABS, TABP = "T2 hedging choices", "T2 choice rule", "T2 hedge by stock", "T2 pricing by stock"
TL, TW, TU = OUT / "task2" / "hedge_loss_chances.csv", OUT / "task2" / "hedge_loss_chances_written_book.csv", OUT / "task2" / "hedge_running.csv"
TABL, TABW, TABU = "T2 loss chances", "T2 loss chances (written)", "T2 running the hedge"
b1, p2 = pd.read_csv(T1), pd.read_csv(T2)
hs = pd.read_csv(TH, dtype={"Stocks move": str, "Volatility change (points)": str})
hc, hr, hb, pb = pd.read_csv(TC).set_index("Choice"), pd.read_csv(TR), pd.read_csv(TS), pd.read_csv(TP)
hl, hw, hu = pd.read_csv(TL).set_index("Choice"), pd.read_csv(TW).set_index("Choice"), pd.read_csv(TU).set_index("Choice")
L99, CASH, REH = "1-in-100 bad day: loss (₹)", "Cash tied up (₹: bought − sold − premium)", "Re-hedging charges a year (₹: 252 days × 0.1%)"
REC = K2["hedge"]["recommended"]
WORST = "Worst result (₹)"; TRADE = "Total trading (₹: shares + calls sold)"
DN, HN = K2["best"]["Direct"], K2["best"]["Hybrid"]
DCOL, HCOL = f"Direct ML price (₹, {DN})", f"Hybrid ML price (₹, {HN})"

# Figures computed from the rows
bs_mae1 = float(b1["Gap: market − BS (₹)"].abs().mean())
book_value = float(b1["Market price (₹)"].sum())
stock_eq = float(b1["Stock-equivalent exposure (₹)"].sum())
theta_day = float(b1["Theta (₹ per day)"].sum())
vega = float(b1["Vega (₹ per +1 volatility point)"].sum())
below = int((b1["Market price below floor?"] == "Yes").sum())
mae = {n: float(p2[c].abs().mean()) for n, c in [("BS", "Gap: market − BS (₹)"), ("Direct", "Gap: market − direct ML (₹)"),
                                                 ("Hybrid", "Gap: market − hybrid ML (₹)")]}
GAPS = "Gap: market − BS (₹), Gap: market − direct ML (₹), Gap: market − hybrid ML (₹)"

handoff = pd.DataFrame([
    handoff_row("Does ML price options better than Black-Scholes?", "No: BS is closest to the market on unseen options", "—", "Measured (2,000 test options)",
                TAB2, GAPS, "Average |gap| of each pricer over all rows", "M8-13",
                "Keep BS for valuing the option book; no capital or budget for ML pricing on this evidence"),
    handoff_row("Average pricing gap: BS / direct ML / hybrid ML", f"₹{mae['BS']:.2f} / ₹{mae['Direct']:.2f} / ₹{mae['Hybrid']:.2f}", "₹ per option",
                "Measured", TAB2, GAPS, "Average |gap| per column", "M8-13",
                f"Direct ML ₹2.41 worse (range ₹2.09–₹2.71); hybrid ₹0.15 worse (₹0.07–₹0.23); no group where ML wins"),
    handoff_row("BS pricing gap on the whole book", f"₹{bs_mae1:.2f} per option (about {K1['median_abs_pct']:.1%} of price); no bias",
                "₹ per option", "Measured (10,000 options)", TAB1, "Gap: market − BS (₹), Gap (% of BS; options ≥ ₹1)",
                "Average |gap|; median |gap %|", "M8-06", "Valuation uncertainty of about 3% per option; it cancels across the book (net ₹+530)"),
    handoff_row("Option book value (one unit of each option)", round(book_value / 1e5, 1), "₹ lakh", "Measured + Assumption (one unit each, M8-05)",
                TAB1, "Market price (₹)", "Sum of the column ÷ 1 lakh", "M8-05", "Scale by NovaFin's real position sizes"),
    handoff_row("Stock exposure of the book", round(stock_eq / 1e5, 1), "₹ lakh of shares", "Measured + Assumption", TAB1,
                "Stock-equivalent exposure (₹)", "Sum of the column (delta × spot) ÷ 1 lakh", "M8-04",
                "The book moves like this much stock; add it to the equity exposure from Modules 5–6"),
    handoff_row("Pricing by stock", f"BS closest in {K2['stocks_bs_best']} of 15 stocks", "stocks", "Measured", TABP, "Best, Best ML vs BS (₹; + = ML closer)",
                "Count of rows where Best = Black-Scholes", "M8-16", "No stock where ML pricing is worth using (the two exceptions are within ₹0.17: noise)"),
    handoff_row("Biggest risk in the book", f"Volatility −5 points: ₹{hs[(hs['Stocks move'] == '+0%') & (hs['Volatility change (points)'] == '-5')]['A. No hedge'].iloc[0]:+,.0f}; stocks −5%: ₹{hs[(hs['Stocks move'] == '-5%') & (hs['Volatility change (points)'] == '+0')]['A. No hedge'].iloc[0]:+,.0f}",
                "₹", "Measured (exact BS repricing)", TABH, "A. No hedge", "Rows (+0%, −5 points) and (−5%, +0 points)", "M8-15",
                "Volatility falling (markets calming) hurts more than a stock fall; shares can't hedge it"),
    *[handoff_row(f"Hedging choice {c}",
                  ("Flagged unreliable on this data (options on one 'stock' have different spots and volatilities): not used" if c.startswith("D.") else
                   f"1-in-100 bad day ₹{-hl.loc[c, L99]:+,.0f}; losing days {hl.loc[c, 'Chance of a losing day']:.0%}; cash tied up ₹{hu.loc[c, CASH]:,.0f}; "
                   f"day-1 charges ₹{hu.loc[c, 'Day 1: trading charges (₹)']:,.0f}; re-hedging ₹{hu.loc[c, REH]:,.0f} a year"),
                  "₹", "Simulated + Assumption (100,000 days; trading costs)", TABL, f"{L99}, Chance of a losing day; {TABU}: {CASH}, {REH}",
                  f"Row {c} in {TABL} and {TABU}", "M8-15, M8-17, M8-18",
                  "Recommended default" if c == REC else ("Not usable" if c.startswith("D.") else
                  ("Worse than no hedge on bad days: don't use" if c.startswith("B.") else "Alternative; the choice rule says when"))) for c in hc.index],
    handoff_row("Choice rule", "The Board sets the most it accepts losing on a 1-in-100 bad day; pick the hedge with the least trading within it (D excluded)", "—",
                "Conclusion", TABR, "Board's limit…, Choice with the least trading within it", "Each limit's row", "M8-15",
                "2% of the book → none of A–C reaches it; 3%–5% → C (4% agreed default); 6% → no hedge"),
    handoff_row("Recommended hedge (C) by stock", f"Sell {hb.filter(like='calls to sell').iloc[:, 0].sum():,.0f} calls; buy ₹{hb.filter(like='shares to buy').iloc[:, 0].sum() / 1e5:.1f} lakh of shares across 15 stocks",
                "units / ₹", "Measured", TABS, f"{REC}: calls to sell (units), {REC}: shares to buy (+) or sell (−) (₹)", "Sums of the columns", "M8-15, M8-16",
                "Shares reset daily; amounts in ₹ (share counts per stock aren't meaningful on this data)"),
    handoff_row("Written book (check)", f"1-in-100 bad day: no hedge ₹{-hw.loc['A. No hedge', L99]:+,.0f}; C ₹{-hw.loc[REC, L99]:+,.0f}", "₹",
                "Simulated + Assumption", TABW, L99, "Rows A and C", "M8-20", "If NovaFin wrote these options, every risk flips; C still cuts the bad day by 42%"),
    handoff_row("Cost of holding the options (time decay)", round(theta_day), "₹ per day", "Measured", TAB1, "Theta (₹ per day)", "Sum of the column", "M8-04",
                f"About ₹{-theta_day * 365 / 1e5:.1f} lakh a year; the hedge doesn't change it"),
    handoff_row("Volatility risk of the unhedged book", round(vega), "₹ per +1 volatility point", "Measured", TAB1, "Vega (₹ per +1 volatility point)",
                "Sum of the column", "M8-04, M8-19", "The biggest risk: volatility −5 points → −₹2.40 lakh; only option hedges (C) cover it"),
    handoff_row("Protect Module 9's equity money: 90% floor put", "Cost ₹1.81 crore a year per ₹100 crore; a 20% crash costs ₹11.8 crore instead of ₹20 crore",
                "₹ crore per ₹100 crore of equities", "Measured (BS) + Assumption (19.4% swing; 1% costs)", "T2 protect equity money", "Cost a year, Stocks −20%: result",
                "BS put price × 1.01 (Task 2 step 9e)", "M8-21", "Budget for 'Derivatives hedging' in Module 9; 100% and 80% floors in the same tab"),
    handoff_row("Assumptions behind these figures", "One unit of each option, owned (written shown as a check); one pricing day (31 Aug 2026); each option has its own spot and volatility even within a stock; no dividends; simulation: stocks correlated 0.4, volatility moves about 1 point a day and rises when stocks fall; share charges 0.1%, option charges 1% of premium, margin not modelled; "
                f"{below} market prices below the lowest logical price treated as data errors", "—", "Assumption", "—", "—", "—", "M8-05, M8-08, M8-12",
                "State these when using the figures"),
])

key_numbers = pd.DataFrame([
    key_row("Options in the data", K1["options"], "options", f"{K1['calls']:,} calls, {K1['puts']:,} puts on {K1['stocks']} stocks, one pricing day", "—", "Rows", TAB1),
    key_row("Our BS vs the file's BS", f"within ₹{K1['bs_vs_file_max_diff']:.2f}", "₹", "Check that the formula is right", "Near 0 is good", "Largest difference", "Task 1"),
    key_row("BS average gap from market (MAE)", f"₹{K1['mae']:.2f} (95% range ₹{K1['mae_range'][0]:.2f}–₹{K1['mae_range'][1]:.2f})", "₹ per option",
            "How far BS is from the market on average", "Lower is better", "All 10,000 options", TAB1),
    key_row("BS bias", f"₹{K1['bias']:+.2f} (range ₹{K1['bias_range'][0]:+.2f} to ₹{K1['bias_range'][1]:+.2f})", "₹ per option",
            "Is BS too cheap (+) or too dear (−) on average?", "Range including 0 = no bias", "Average gap", TAB1),
    key_row("Typical gap as % of price", f"{K1['median_abs_pct']:.1%}", "%", "Median |gap| ÷ BS, options worth ₹1 or more", "Lower is better", "Median", TAB1),
    key_row("Pattern in the gap", f"None: direction differs in no group; learned correction R² {K1['task2_review']['gap_r2']:+.2f}", "—",
            "Could a model learn where BS misses?", "R² ≤ 0 = nothing to learn", "Task 1 tests", "Task 1"),
    key_row("Impossible market prices", below, "options", "Below the lowest logical price: data errors", "—", "Market price below floor? = Yes", TAB1),
    key_row("Test: average gap BS / direct ML / hybrid ML", f"₹{mae['BS']:.2f} / ₹{mae['Direct']:.2f} / ₹{mae['Hybrid']:.2f}", "₹ per option",
            f"On 2,000 unseen options; direct = {DN}, hybrid = BS + {HN}", "Lower is better", "Average |gap|", TAB2),
    key_row("Groups where BS is best", f"{K2['segments_bs_best']} of {K2['segments']}", "—", "By price fifth, moneyness, call/put", "—", "Test options", "Task 2"),
    key_row("Hybrid correction vs shuffled (p)", K2["luck"]["p"], "0–1", "Chance shuffled corrections do as well", "Below 0.05 = real", "20 shuffles", "Task 2"),
    key_row("Book: value / stock exposure", f"₹{book_value / 1e5:.1f} lakh / ₹{stock_eq / 1e5:.1f} lakh", "₹", "One unit of each option", "—", "Sums", TAB1),
    key_row("Book: time decay / volatility risk", f"₹{theta_day:,.0f} a day / ₹{vega:+,.0f} per point", "₹", "Theta and vega summed", "—", "Sums", TAB1),
    key_row("Worst of 21 scenarios: A / B / C / D", " / ".join(f"₹{hc.loc[c, WORST]:+,.0f}" for c in hc.index), "₹",
            "No hedge / delta / delta + half vega / delta + full vega", "Closer to 0 is safer; more trading needed", "Lowest scenario result", TABC),
    key_row("1-in-100 bad day: A / B / C", " / ".join(f"₹{-hl.loc[c, L99]:+,.0f}" for c in hc.index if not c.startswith("D.")), "₹",
            "No hedge / delta only / delta + half vega", "Closer to 0 is safer", "100,000 simulated days", TABL),
    key_row("Recommended hedge", REC, "—", "Agreed default (1-in-100 bad day ≤ 4% of the book)", "—", "Choice rule", TABR),
])

board_actions = pd.DataFrame([
    action_row(1, "Keep pricing options with Black-Scholes; don't deploy ML pricing",
               f"ML would add ₹{(mae['Hybrid'] - mae['BS']) * 10000:,.0f}–₹{(mae['Direct'] - mae['BS']) * 10000:,.0f} of mispricing per 10,000 options",
               "ML was worse than BS on unseen options, in all 12 groups and 13 of 15 stocks; the market here is BS plus random noise", TAB2),
    action_row(2, f"Hedge with {REC}: sell 1-year at-the-money calls and buy shares; reset the shares daily",
               f"1-in-100 bad day ₹{-hl.loc['A. No hedge', L99]:+,.0f} → ₹{-hl.loc[REC, L99]:+,.0f}; ≈ ₹{hu.loc[REC, CASH] / 1e5:.1f} lakh cash tied up; ₹{hu.loc[REC, 'Day 1: trading charges (₹)']:,.0f} day 1 + ₹{hu.loc[REC, REH]:,.0f} a year",
               "Covers stock moves and half the volatility risk, the book's biggest risk (shares alone can't); the shares bought are a holding, not a cost", TABL),
    action_row(3, "Don't use a delta-only (shares-only) hedge",
               f"1-in-100 bad day ₹{-hl.loc['B. Delta hedge', L99]:+,.0f}, worse than no hedge; ₹{hu.loc['B. Delta hedge', REH]:,.0f} a year to run",
               "It removes the natural protection (volatility rises when stocks fall) and leaves volatility risk bare", TABL),
    action_row(4, "Set the 1-in-100 bad-day limit; the choice rule picks the hedge",
               "3%–5% of the book → C (4% agreed default); 6% → no hedge; 2% → needs a fuller vega hedge (not reliable on this data)",
               "A tighter limit needs more hedging; the Board decides the trade-off", TABR),
    action_row(5, "Revisit ML pricing when real market data is available", "—",
               "Real markets have volatility smiles and estimated volatility, where ML can help; this data has neither", "Report limitations"),
])

read_me = {
    "question": "NovaFin has exposure to equity options. Management wants to know: Can ML improve option pricing and help manage derivatives exposure?",
    "answer": [f"Pricing: no, not on this data. Black-Scholes is on average ₹{K1['mae']:.2f} (about 3%) from the market with no pattern; ML was worse on unseen options (₹{mae['Direct']:.2f} direct, ₹{mae['Hybrid']:.2f} hybrid vs ₹{mae['BS']:.2f}).",
               f"Exposure: yes, through BS's Greeks. The book behaves like ₹{stock_eq / 1e5:.1f} lakh of shares and gains or loses ₹{vega:,.0f} per volatility point; volatility is its biggest risk.",
               f"Recommended hedge: {REC} — 1-in-100 bad day ₹{-hl.loc['A. No hedge', L99]:+,.0f} → ₹{-hl.loc[REC, L99]:+,.0f}. The choice rule in '{TABR}' gives the hedge for any limit the Board sets. Delta-only is worse than no hedge."],
    "tasks": [("Task 1 — Black-Scholes benchmark", "FINAL_M8_T1_bs_benchmark.csv", "every option: BS vs market, gap in ₹ and %, flags, Greeks, why in words"),
              ("Task 2 — ML pricing", "FINAL_M8_T2_ml_pricing.csv", "every test option: BS, direct ML and hybrid ML prices vs market, closest pricer, why in words")],
    "how_to_read": ["Money is in ₹ for one unit of each option (position sizes are not in the data).",
                    "Full explanation: reports/module_8_report.md."],
}
task_tabs = [(TAB1, T1, "Task 1: every option, BS vs market, Greeks and why"),
             (TAB2, T2, "Task 2: every test option, BS vs ML prices vs market and why"),
             (TABP, TP, "Task 2: pricing on the test options, one row per stock"),
             (TABC, TC, "Task 2: the four hedging choices compared (worst case, trading, cost, time decay)"),
             (TABH, TH, "Task 2: the book's ₹ change in 21 stock × volatility scenarios, for each hedging choice"),
             (TABL, TL, "Task 2: how often and how badly each hedging choice loses (100,000 simulated days, owned book)"),
             (TABW, TW, "Task 2: the same if NovaFin had written (sold) the options: a check"),
             (TABU, TU, "Task 2: running each hedge: day-1 trades, cash tied up, daily re-hedging and its yearly charges"),
             (TABR, TR, "Task 2: which hedge to pick for each 1-in-100 bad-day limit the Board might set"),
             ("T2 protect equity money", OUT / "task2" / "protect_equity_money.csv", "Task 2: the cost of protecting Module 9's equity money with a 1-year put, and the result in crashes"),
             (TABS, TS, "Task 2: each stock's risk, and what each hedge trades in it")]

# Every column of every task tab, in one plain sentence (shown in the Read me tab)
COLUMN_GUIDE = {
    "Option ID": "The option's ID in nova_options.csv", "Stock": "The stock the option is on", "Type": "Call (right to buy) or Put (right to sell)",
    "Strike (₹)": "The fixed price written in the option", "Spot (₹)": "The stock's price today",
    "Expiry": "The option's last day", "Time to maturity (years)": "Time left until expiry, in years", "Volatility": "How much the stock swings in a year (0.25 = 25%)",
    "Interest rate": "Return on safe money, a year", "In the money by": "How much using the option today would pay, as a share (negative = out of the money)",
    "Moneyness band": "In-the-money group: far out, out, at, in, far in",
    "BS price (₹, ours)": "Black-Scholes price we calculated", "BS price (₹, file)": "Black-Scholes price given in the file (check)",
    "BS price (₹)": "Black-Scholes price we calculated", "Market price (₹)": "What the option actually trades for",
    "Gap: market − BS (₹)": "Market price − BS price (+ = market dearer than BS)",
    "Gap (% of BS; options ≥ ₹1)": "The gap as a share of the BS price; blank for options worth under ₹1",
    "No-arbitrage floor (₹)": "The lowest price the option can logically have",
    "Market price below floor?": "Yes = the market price is below the floor: likely a data error",
    "Delta": "₹ change in the option for a ₹1 rise in the stock", "Gamma": "How much delta changes for a ₹1 rise in the stock",
    "Vega (₹ per +1 volatility point)": "₹ change if volatility rises by 1 point (e.g. 25% → 26%)",
    "Theta (₹ per day)": "₹ change from one day passing (negative = loses value)",
    "Stock-equivalent exposure (₹)": "Delta × spot: the option moves like this much ₹ of the stock",
    "Why, in words": "What BS says, what the market pays, any flag, and how the option reacts",
    DCOL: f"Price from the direct ML model ({DN}), learned from the inputs without the BS formula",
    HCOL: f"BS price + a correction learned by {HN}",
    "Gap: market − direct ML (₹)": "Market price − direct ML price", "Gap: market − hybrid ML (₹)": "Market price − hybrid ML price",
    "Closest to market": "Which of the three prices was nearest the market for this option",
    "Test options": "How many test options this stock has",
    "MAE (₹): Black-Scholes": "Average gap from the market, BS", f"MAE (₹): Direct ML ({DN})": "Average gap from the market, direct ML",
    f"MAE (₹): Hybrid ML ({HN})": "Average gap from the market, hybrid ML", "Best": "Which pricer had the smallest average gap",
    "Best ML vs BS (₹; + = ML closer)": "BS's average gap − the better ML's; + means ML was closer",
    "Choice": "Hedging choice: A none, B delta (shares), C delta + half vega (shares + selling calls), D delta + full vega",
    "Worst result (₹)": "The book's (with hedge) lowest change across the 21 scenarios",
    "Worst scenario": "Which stock and volatility move gives that worst result", "Best result (₹)": "The highest change across the 21 scenarios",
    "Typical swing (₹, average size of change)": "Average size of the change across scenarios: how much the value moves around",
    "Scenarios that lose": "Of 21 scenarios, how many lose money", "Shares to trade (₹)": "₹ of shares bought or sold for the hedge",
    "Calls to sell (units)": "1-year at-the-money calls sold to offset volatility risk",
    "Premium received for calls sold (₹)": "Cash received for those calls", "Total trading (₹: shares + calls sold)": "Shares traded + premium of calls sold: the size of the hedge",
    "Total trading ÷ book value": "Hedge size as a multiple of the option book's value (₹19.4 lakh)",
    "Upfront trading cost (₹)": "Charges: 0.1% on shares, 1% of premium on options (assumptions)",
    "Time decay (₹ a day)": "Daily change from time passing, book + hedge (negative = cost)",
    "Volatility sensitivity left (₹ per point)": "₹ the book + hedge still gains or loses per volatility point",
    "Stocks move": "The same % move applied to every stock at once", "Volatility change (points)": "Volatility change for every option, in points (e.g. −5: 24% → 19%)",
    "A. No hedge": "₹ change of the book alone", "B. Delta hedge": "₹ change of book + shares sold",
    "C. Delta + half vega hedge": "₹ change of book + calls sold (half the volatility risk) + shares", "D. Delta + full vega hedge": "₹ change of book + calls sold (all the volatility risk) + shares",
    "Floor": "The put's floor: the share of today's value the holding can't fall below (before the put's cost)",
    "Priced at": "The yearly swing used to price the put: Module 6's real-market estimate, or a dearer check",
    "Cost a year (₹ crore per ₹100 crore)": "What the put costs for a year, including 1% trading costs",
    "Normal year: equity return after the cost (% a year)": "Module 6's 15.6% a year minus the put's cost",
    "Stocks -10%: result (₹ crore per ₹100 crore)": "Result with the put if equities fall 10% (unprotected: −₹10 crore)",
    "Stocks -20%: result (₹ crore per ₹100 crore)": "Result with the put if equities fall 20% (unprotected: −₹20 crore)",
    "Stocks -30%: result (₹ crore per ₹100 crore)": "Result with the put if equities fall 30% (unprotected: −₹30 crore)",
    "Board's limit: most it accepts losing on a 1-in-100 bad day": "The limit the Board might set, as a share of the book and in ₹",
    "Choice with the least trading within it": "The hedge to use under that limit",
    "Chance of a losing day": "Share of simulated days that lose money", "Average day (₹)": "Average one-day change in value",
    "1-in-20 bad day: loss (₹)": "Loss exceeded on only 1 day in 20", "1-in-100 bad day: loss (₹)": "Loss exceeded on only 1 day in 100 (Value at Risk)",
    "Chance of a losing month": "Share of simulated 21-day months that lose money", "1-in-20 bad month: loss (₹)": "Loss exceeded in only 1 month in 20",
    "Day 1: shares bought (₹)": "Shares bought on day 1 (a holding, not a cost)", "Day 1: shares sold (₹)": "Shares sold on day 1 (needs margin if not owned)",
    "Day 1: calls sold (units)": "1-year at-the-money calls sold on day 1", "Day 1: premium received (₹)": "Cash received for the calls sold",
    CASH: "Cash the hedge ties up on day 1 (negative = cash received from a short sale; margin not included)",
    "Day 1: trading charges (₹)": "Charges on day 1's trades", "How often reset": "How often the hedge is adjusted",
    "Shares traded on a typical day to re-hedge (₹)": "Shares bought or sold on a typical day to keep the hedge right", REH: "Charges for that daily re-hedging over a year",
    "Options": "How many options on this stock", "Book value (₹)": "Market value of this stock's options",
    "Volatility sensitivity (₹ per point)": "₹ gained or lost per 1-point volatility change", "Unhedged: stocks −5% (₹)": "Loss if this stock falls 5%",
    "Unhedged: volatility −5 points (₹)": "Loss if volatility falls 5 points",
    f"{REC}: calls to sell (units)": "Recommended hedge: calls to sell on this stock",
    f"{REC}: shares to buy (+) or sell (−) (₹)": "Recommended hedge: shares to buy (+) or sell (−) in this stock",
    f"{REC}: worst of the 21 scenarios (₹)": "This stock's worst case across the 21 scenarios with the recommended hedge",
}

if __name__ == "__main__" or "get_ipython" in globals():
    path = build_workbook(MODULE_DIR, 8, read_me, key_numbers, board_actions, task_tabs, handoff, column_guide=COLUMN_GUIDE, receiver="Module 9",
                          m9_inputs=pd.read_csv(MODULE_DIR / "outputs" / 'task2/module9_inputs.csv'))
    print("Saved:", path.name)
    print(handoff[["Figure", "Value", "Unit"]].to_string(index=False))

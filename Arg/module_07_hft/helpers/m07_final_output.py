"""
Module 7 — final output workbook
================================

WHAT THIS FILE DOES
    Builds outputs/FINAL_M7_module_output.xlsx: the one file where Module 9, the Board, the presenter and the
    evaluator see everything Module 7 produced (project decision P-21). Tabs: Read me (with a column guide),
    Key numbers, Board actions, the Task 1 and Task 2 final files (plus Test 1's cut-off table), Hand-off to
    Module 9, Decisions, Evidence index. Hand-off figures are computed here from the task tabs' rows.

HOW TO USE
    Run after Tasks 1–2: runner cell "Final output workbook", or python helpers/m07_final_output.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

here = Path(__file__).resolve() if "__file__" in globals() else Path.cwd() / "helpers" / "m07_final_output.py"
MODULE_DIR = here.parents[1]
sys.path.insert(0, str(MODULE_DIR.parent / "scripts"))
from final_workbook import build_workbook, handoff_row, key_row, action_row   # noqa: E402

OUT = MODULE_DIR / "outputs"
K1 = json.loads((OUT / "task1" / "key_numbers.json").read_text(encoding="utf-8"))
K2 = json.loads((OUT / "task2" / "key_numbers.json").read_text(encoding="utf-8"))
T1 = OUT / "task1" / "FINAL_M7_T1_direction_predictions.csv"
T2 = OUT / "task2" / "FINAL_M7_T2_trade_decisions.csv"
TC = OUT / "task2" / "test1_rules.csv"
TAB1, TAB2, TABC = "T1 direction predictions", "T2 trade decisions", "T2 Test 1 rules"
p1, d2 = pd.read_csv(T1), pd.read_csv(T2)
test1 = p1[p1.Set == "Test day"]
accuracy = float((test1.Predicted == test1.Actual).mean())
traded = d2[d2["Test 1: trade"] != "No trade"]
net_trade = float(traded["Test 1: after spread and charges (₹ per ₹1 crore)"].mean())
net_total_lakh = float(traded["Test 1: after spread and charges (₹ per ₹1 crore)"].sum() / 1e5)
saving = float((d2["Test 2: saving on the buy (₹ per ₹1 crore)"] + d2["Test 2: saving on the sell (₹ per ₹1 crore)"]).mean() / 2)
per_day_lakh = saving * 100 / 1e5                     # ₹100 crore of orders a day = 100 × ₹1 crore
per_year_crore = per_day_lakh * 1e5 * 261 / 1e7
SENS = K2["test1"]["charges_sensitivity_total_lakh"]     # cost per round trip → [rule knows it, rule assumes 3.5]
T2_SAVING = "Test 2: saving on the buy (₹ per ₹1 crore), Test 2: saving on the sell (₹ per ₹1 crore)"

handoff = pd.DataFrame([
    handoff_row("Can the order book predict the next 0.1-second move?", f"Yes: right {accuracy:.1%} of the time vs {K1['base_accuracy_test']:.1%} by guessing",
                "share of test-day moments", "Measured (17,876 test moments)", TAB1, "Set, Predicted, Actual",
                "Rows where Set = Test day: share where Predicted = Actual", "M7-09, M7-10", "ML has real short-horizon skill on this data"),
    handoff_row("Recommended use", "Time the desk's own orders now; run the cost-aware trading rule as a measured pilot", "—", "Conclusion",
                TAB2, "Test 1: …, Test 2: …", "From the two tests below", "M7-12", "How the HFT capability earns its keep"),
    handoff_row("Order timing: saving per ₹1 crore of orders", round(saving), "₹ per ₹1 crore of orders", "Measured", TAB2, T2_SAVING,
                "Average of (saving on the buy + saving on the sell) ÷ 2 over all test rows", "M7-14",
                f"Price improvement on orders the desk places anyway; 95% range ₹{K2['test2']['range'][0]:,.0f}–₹{K2['test2']['range'][1]:,.0f}"),
    handoff_row("Order timing: per ₹100 crore of orders a day", f"₹{per_day_lakh:.2f} lakh a day; ₹{per_year_crore:.2f} crore a year", "₹",
                "Measured + Assumption (illustrative volume, 261 trading days)", TAB2, T2_SAVING, "Saving per ₹1 crore × 100; a year = × 261",
                "M7-14", "Scale to NovaFin's real order volume"),
    handoff_row("Trading on the signal: net per trade after all costs", round(net_trade), "₹ per ₹1 crore traded", f"Measured ({len(traded):,} trades)", TAB2,
                "Test 1: trade, Test 1: after spread and charges (₹ per ₹1 crore)", "Average of the after-charges column where Test 1: trade ≠ No trade",
                "M7-13, M7-15", "Modest profit (86% of the gross gain goes on costs): a measured pilot, not a capital line"),
    handoff_row("Trading on the signal: total over the 3 test days", round(net_total_lakh, 1), "₹ lakh (₹1 crore a trade)", "Measured", TAB2,
                "Test 1: after spread and charges (₹ per ₹1 crore)", "Sum of the column ÷ 1 lakh", "M7-15", "Size of the gain at ₹1 crore a trade"),
    handoff_row("Trading on the signal: 95% range of the total", f"₹{K2['test1']['total_range_lakh'][0]:+.1f} to ₹{K2['test1']['total_range_lakh'][1]:+.1f} lakh",
                "₹ lakh (₹1 crore a trade)", "Measured", TAB2, "Test 1: after spread and charges (₹ per ₹1 crore)",
                "Resample the traded rows 1,000 times; 2.5th–97.5th percentile of the sum", "M7-15", "Entirely above zero"),
    handoff_row("Trading on the signal if real costs are higher than assumed", f"0.5 bp higher: ₹{SENS['4.0'][1]:+.1f} lakh; 1 bp higher: ₹{SENS['4.5'][1]:+.1f} lakh (rule told the real cost: ₹{SENS['4.5'][0]:+.1f} lakh)",
                "₹ lakh over 3 test days", "Stress estimate", TAB2, "Test 1: after spread (₹ per ₹1 crore), Test 1: this moment's cost (₹ per ₹1 crore)",
                "After-spread result of the traded rows − the higher cost; and the rule rerun with that cost", "M7-06, M7-15",
                "Measure real brokerage and slippage first; feed the real cost into the rule"),
    handoff_row("Share of moments traded", round(100 * len(traded) / len(d2), 1), "% of test moments", "Measured", TAB2, "Test 1: trade",
                "Rows where Test 1: trade ≠ No trade ÷ all rows", "M7-13", "Traded only when the expected gain beats that moment's cost (cost-aware rule)"),
    handoff_row("Order timing on Module 9's equity money", "0.010% a year of the equity money (≈ ₹1 lakh per ₹100 crore)", "% a year", "Measured + Module 6 turnover",
                "Module 9 inputs", "Return per ₹ deployed (% a year)", "Module 6 equal-weight turnover (≈ 0.8× a year) × Test 2 saving per ₹ of orders (step 5b)", "M7-18",
                "Real but small; no capital needed"),
    handoff_row("Assumptions behind these figures", "Spread paid both ways + 3.5 bps Indian intraday charges per round trip; zero brokerage; orders filled at the quoted price and too small to move it; 0.1-second horizon only; 3 test days; data looks simulated (trade size has no effect)",
                "—", "Assumption", "—", "—", "—", "M7-06, M7-14", "State these when using the figures"),
])

t = K1["test"]
key_numbers = pd.DataFrame([
    key_row("Moments in the data", K1["events"], "order-book events", "20 trading days, 10 stocks", "—", "Rows", "Data"),
    key_row("Right-class rate, logistic regression (test days)", f"{100 * accuracy:.1f}%", "% of moments", "How often the predicted move was the actual one",
            f"Higher is better; guessing gives {100 * K1['base_accuracy_test']:.1f}%", "Predicted = Actual", TAB1),
    key_row("AUC, rises vs falls", " / ".join(f"{n.split()[0]} {t[n]['auc']:.3f}" for n in t), "0.5 = coin flip, 1 = perfect",
            "How well each model's lean separates real rises from real falls", "Higher is better", "Test days", "Task 1"),
    key_row("Beat OBI alone?", "Yes, all three models (p < 0.0001)", "—", "Gain over the simple buyer/seller balance rule: +0.008 to +0.010 AUC",
            "Small but real", "DeLong test, line 0.017", "Task 1"),
    key_row("Test 1 rule", f"Trade when {K2['slope_bps_per_lean']:.2f} bps × lean > this moment's spread + 3.5 bps (margin {K2['margin_bps']:+.2f})", "—",
            "Expected gain vs this moment's own cost (revised after Task 1's review)", "—", "Slope from Task 1; margin with most profit on the tuning days", TABC),
    key_row("Old fixed cut-off rule, for comparison", f"₹{K2['old_rule_test']['per_trade_rupees']:+,.0f} a trade; ₹{K2['old_rule_test']['total_lakh']:+.1f} lakh", "₹ per ₹1 crore",
            "Trading whenever the lean is beyond 0.70", "Lower than the cost-aware rule", "Test days", TABC),
    key_row("Test 1 net per trade", round(net_trade), "₹ per ₹1 crore", "After the bid–ask spread and 3.5 bps of charges", "Higher is better",
            f"Average over {len(traded):,} test-day trades", TAB2),
    key_row("Test 1: gross gain lost to costs", f"{100 * (1 - net_trade / K2['test1']['per_trade_rupees']['Before costs (move captured)']):.0f}%", "%",
            "Share of the price move caught that goes on the spread and charges", "Lower is better", "1 − net ÷ gross", TAB2),
    key_row("Test 1 luck check (p)", K2["test1"]["p_luck"], "0–1", "Chance random trading does as well", "Below 0.05 = real", "1,000 random runs", "Task 2"),
    key_row("Test 2 saving", round(saving), "₹ per ₹1 crore of orders", "Price improvement from waiting 0.1 s when the model expects an adverse move",
            "Higher is better", "Average over buy and sell orders, all test moments", TAB2),
    key_row("Test 2 luck check (p)", K2["test2"]["p_luck"], "0–1", "Chance random waiting does as well", "Below 0.05 = real", "1,000 random runs", "Task 2"),
])

board_actions = pd.DataFrame([
    action_row(1, "Time the desk's own orders now: when buying, wait a tenth of a second if the model expects a dip (the reverse for sales)",
               f"About ₹{saving:,.0f} saved per ₹1 crore of orders; ₹{per_day_lakh:.1f} lakh a day, ₹{per_year_crore:.1f} crore a year per ₹100 crore of orders a day",
               "No extra cost (the order and its taxes happen anyway); works on buys and sells, in all 10 stocks, far beyond luck; low risk: changes only when an order goes in", TAB2),
    action_row(2, "Run the cost-aware trading rule as a measured pilot", f"+₹{net_trade:,.0f} per ₹1 crore trade; +₹{net_total_lakh:.1f} lakh over 3 test days, every day positive",
               "86% of the gross gain goes on costs; costs were assumed, not measured: 1 bp more turns ₹10.3 lakh into a ₹4.4 lakh loss if the rule isn't told", TAB2),
    action_row("2a", "Pilot step 1: start small, in the narrow-spread stocks", "Most profit came from them (NOVA09 +₹4.7 lakh)", "Wide-spread stocks were rarely worth trading", TAB2),
    action_row("2b", "Pilot step 2: record real brokerage, fill prices and slippage", "Each 0.5 bp of hidden cost ≈ ₹500 per ₹1 crore trade", "The backtest assumes zero brokerage and fills at the quoted price", "Report §3b"),
    action_row("2c", "Pilot step 3: feed the real cost into the rule", "Told the true cost, it stayed profitable even at 1 bp more (+₹0.7 lakh)", "The rule then trades less, only where it still pays", "Report §3b"),
    action_row("2d", "Pilot step 4: stop if profit after costs turns negative", "Caps the downside", "A thin-margin activity needs a stop rule", "Report §5"),
    action_row(3, "Collect longer-horizon prices and order-fill data", "—", "To test longer waits and limit orders, which this data can't show", "Report limitations"),
])

read_me = {
    "question": "NovaFin's trading desk executes large equity orders in the market. The Head of Trading asks: Can ML use limit-order-book information to predict short-horizon price movements and improve order execution?",
    "answer": [f"Yes, it predicts: right {accuracy:.1%} of the time on unseen days, against {K1['base_accuracy_test']:.1%} by guessing, mostly from the balance of waiting buyers and sellers.",
               f"It improves execution: timing the desk's own orders saves about ₹{saving:,.0f} per ₹1 crore of orders.",
               f"Trading on the signal with the cost-aware rule makes +₹{net_trade:,.0f} per ₹1 crore trade after all costs, every test day; modest and cost-sensitive, so a measured pilot."],
    "tasks": [("Task 1 — Direction prediction", "FINAL_M7_T1_direction_predictions.csv", "every tuning- and test-day moment: chances of up / down / no move, prediction, outcome, why in words"),
              ("Task 2 — Signal and backtest", "FINAL_M7_T2_trade_decisions.csv", "every test-day moment: Test 1 trade and ₹ result, Test 2 wait-or-go and ₹ saving, reasons in words")],
    "how_to_read": ["Money is per ₹1 crore traded (1 bp = ₹1,000); ₹1 crore is a measuring unit, not a trade size.",
                    "Full explanation: reports/module_7_report.md."],
}
task_tabs = [(TAB1, T1, "Task 1: every tuning- and test-day moment, the model's chances, prediction, outcome and why"),
             (TAB2, T2, "Task 2: every test-day moment, what Test 1 and Test 2 did, the ₹ result and why"),
             (TABC, TC, "Task 2: Test 1's cut-off chosen on the tuning days")]

# Every column of every task tab, in one plain sentence (shown in the Read me tab)
COLUMN_GUIDE = {
    "Set": "Tuning day (15–17: used to choose) or Test day (18–20: used once, to judge)",
    "Trading day": "The date", "Time": "The minute of the day (file order gives the exact sequence)", "Stock": "The stock",
    "Mid price (₹)": "Midpoint of the best buying and selling prices",
    "Spread (bps)": "Gap between the best selling and buying prices, as a share of the price (1 bp = 0.01%)",
    "Spread (₹ per ₹1 crore)": "The same gap in ₹ on ₹1 crore",
    "Imbalance at best price (OBI)": "(shares waiting to buy − shares waiting to sell) ÷ both, at the best price; +1 = only buyers, −1 = only sellers",
    "Last trade": "Whether the last trade was a purchase (BUY) or a sale (SELL)",
    "Chance of UP": "The model's chance the price rises more than 0.012% in the next tenth of a second",
    "Chance of DOWN": "The model's chance it falls more than 0.012%",
    "Chance of NO_MOVE": "The model's chance it stays within ±0.012%",
    "Predicted": "The most likely of the three (never NO_MOVE: the data can't tell when no-moves happen)",
    "Lean (chance of UP − chance of DOWN)": "The trading signal: positive = expects a rise, negative = a fall, near 0 = unsure",
    "Actual": "What actually happened in the next tenth of a second",
    "Actual move (bps)": "The actual price change in basis points (used only to score, never to decide)",
    "Actual move (₹ per ₹1 crore)": "The same change in ₹ on ₹1 crore",
    "Model used": "The model passed from Task 1 (logistic regression)",
    "Lean: OBI alone": "The lean of the simple buyer/seller-balance rule (the benchmark)",
    "Lean: Logistic regression": "Logistic regression's lean", "Lean: Random forest": "Random forest's lean", "Lean: LightGBM": "LightGBM's lean",
    "Why, in words": "What the order book showed, what the model said, and what happened",
    "Test 1: expected gain (₹ per ₹1 crore)": "What the model's lean suggests the trade would catch: 7.1 bps × the lean, in ₹",
    "Test 1: this moment's cost (₹ per ₹1 crore)": "This moment's bid–ask spread plus ₹3,500 of charges",
    "Test 1: trade": "Buy or Sell if the expected gain beats this moment's cost; otherwise No trade",
    "Test 1: move captured (₹ per ₹1 crore)": "The price move caught by the trade, before costs",
    "Test 1: after spread (₹ per ₹1 crore)": "After paying the bid–ask gap on the way in and out",
    "Test 1: after spread and charges (₹ per ₹1 crore)": "After also paying ₹3,500 of Indian trading charges: the trade's net result",
    "Test 2: a buy order would": "If the desk had to buy now: wait 0.1 s (a fall is expected) or buy now",
    "Test 2: saving on the buy (₹ per ₹1 crore)": "How much cheaper the purchase was for waiting (0 if bought now)",
    "Test 2: a sell order would": "If the desk had to sell now: wait 0.1 s (a rise is expected) or sell now",
    "Test 2: saving on the sell (₹ per ₹1 crore)": "How much better the sale was for waiting (0 if sold now)",
    "Test 1: reason in words": "Why Test 1 traded or not, and the ₹ result after each cost",
    "Test 2: reason in words": "Why each order would wait or go now, and what waiting saved",
    "Rule": "Which rule and setting: the cost-aware rule at each margin, or the old fixed cut-off", "Trades": "How many trades it makes on the tuning days",
    "Share of moments": "Those trades as a share of all tuning-day moments",
    "Net per trade (₹ per ₹1 crore)": "Average result per trade after all costs",
    "Net total (₹ lakh, ₹1 crore a trade)": "Total result over the 3 tuning days",
    "Average spread paid (₹)": "The average bid–ask spread those trades paid, per ₹1 crore",
}

if __name__ == "__main__" or "get_ipython" in globals():
    path = build_workbook(MODULE_DIR, 7, read_me, key_numbers, board_actions, task_tabs, handoff, column_guide=COLUMN_GUIDE, receiver="Module 9",
                          m9_inputs=pd.read_csv(MODULE_DIR / "outputs" / 'task2/module9_inputs.csv'))
    print("Saved:", path.name)
    print(handoff[["Figure", "Value", "Unit"]].to_string(index=False))

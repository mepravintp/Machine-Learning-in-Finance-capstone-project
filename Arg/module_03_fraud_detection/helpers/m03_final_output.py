"""
Module 3 — final output workbook
================================

WHAT THIS FILE DOES
    Builds outputs/FINAL_M3_module_output.xlsx: the one file where Module 9, the Board, the presenter and the
    evaluator see everything Module 3 produced (project decision P-21). Tabs: Read me, Key numbers,
    Board actions, one tab per task's final file, Hand-off to Module 9, Decisions, Evidence index.
    Hand-off figures (cost of fraud risk as a share of money moved) are computed here from the
    6,000 test transactions in the decision file.

HOW TO USE
    Run after Tasks 1–4: runner cell "Final output workbook", or python helpers/m03_final_output.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

here = Path(__file__).resolve() if "__file__" in globals() else Path.cwd() / "helpers" / "m03_final_output.py"
MODULE_DIR = here.parents[1]
sys.path.insert(0, str(MODULE_DIR.parent / "scripts"))
from final_workbook import build_workbook, handoff_row, key_row, action_row   # noqa: E402

OUT = MODULE_DIR / "outputs"
K = {t: json.loads((OUT / t / "key_numbers.json").read_text(encoding="utf-8")) for t in ("task1", "task2", "task3", "task4")}
T1 = OUT / "task1" / "FINAL_M3_T1_fraud_evidence.csv"
T2 = OUT / "task2" / "FINAL_M3_T2_fraud_scores.csv"
T3 = OUT / "task3" / "FINAL_M3_T3_anomaly_scores.csv"
T4 = OUT / "task4" / "FINAL_M3_T4_transaction_decisions.csv"
TAB1, TAB2, TAB3, TAB4 = "T1 fraud evidence", "T2 fraud scores", "T3 anomaly scores", "T4 transaction decisions"
CHECK_COST = 500        # the brief's cost of checking an honest transaction (a false alarm), ₹ — Module 3's cost model

D = pd.read_csv(T4)
test = D[D.Set == "test"]
AMT, DEC, FRAUD = "Amount (₹)", "Decision (brief's costs)", "Actually fraud"
moved = test[AMT].sum()
lost_none = test.loc[test[FRAUD] == "Yes", AMT].sum()
lost_rule = test.loc[(test[FRAUD] == "Yes") & (test[DEC] == "Let through"), AMT].sum()
checks = int((test[DEC] == "Investigate").sum())
honest_checked = int(((test[DEC] == "Investigate") & (test[FRAUD] == "No")).sum())
check_cost = CHECK_COST * honest_checked                     # checking a real fraud is not a wasted cost: it stops the loss
per_1000 = 1000 / len(test)
COND = "rows where Set = test"

handoff = pd.DataFrame([
    handoff_row("Money moved per 1,000 transactions", round(moved * per_1000 / 1e5, 2), "₹ lakh", "Measured (6,000 test transactions)", TAB4, AMT,
                f"Sum of {AMT} over {COND} × 1,000 ÷ 6,000 ÷ 1 lakh", "M3 Task 4", "Scale: rates below apply to money moved"),
    handoff_row("Cost of fraud risk, no screening", round(100 * lost_none / moved, 2), "% of money moved", "Measured", TAB4, f"{AMT}, {FRAUD}",
                f"Sum of {AMT} where {FRAUD} = Yes ÷ sum of {AMT}, {COND}", "M3 Task 4", "What fraud costs Digital banking with no screening"),
    handoff_row("Fraud lost with the 4.76% rule", round(100 * lost_rule / moved, 2), "% of money moved", "Measured", TAB4, f"{AMT}, {FRAUD}, {DEC}",
                f"Sum of {AMT} where {FRAUD} = Yes and {DEC} = Let through ÷ sum of {AMT}, {COND}", "M3 Task 4", "Part of the total below"),
    handoff_row("Investigation cost with the 4.76% rule (honest transactions checked)", round(100 * check_cost / moved, 2), "% of money moved",
                "Assumption (₹500 per false alarm) + Measured", TAB4, f"{DEC}, {FRAUD}",
                f"₹500 × count where {DEC} = Investigate and {FRAUD} = No ÷ sum of {AMT}, {COND}", "M3 Task 4 (brief's costs)", "Part of the total below"),
    handoff_row("Total cost of fraud risk with the rule", round(100 * (lost_rule + check_cost) / moved, 2), "% of money moved", "Measured + Assumption",
                TAB4, f"{AMT}, {FRAUD}, {DEC}", "Fraud lost + investigation cost, as above", "M3 Task 4",
                "Set against Digital banking's return in the allocation"),
    handoff_row("Investigations needed", round(checks * per_1000, 1), "per 1,000 transactions", "Measured", TAB4, DEC,
                f"Count of {DEC} = Investigate, {COND}, × 1,000 ÷ 6,000", "M3 Task 4", "Workload / staffing of the fraud team"),
    handoff_row("Module 9 inputs: Digital banking: cost of fraud risk", "-1.55 (bad year -4.03)", "% a year per ₹",
                "Measured + Assumption", "Module 9 inputs", "Return per ₹ deployed, Bad-year result per ₹", "Final notebook step 'What goes to Module 9'", "M3-21",
                "Standard fields for Module 9; gaps marked as assumptions"),
    handoff_row("Assumptions behind these figures",
                "Brief's costs: ₹10,000 per missed fraud, ₹500 per honest transaction checked (false alarm); missed frauds lost at their actual amount here; a 20-month sample (about 49 transactions a day) — rates carry over, daily totals must be scaled",
                "—", "Assumption", "—", "—", "—", "Module 3 decisions", "State these when using the figures"),
])

k1, k2, k3, k4 = K["task1"], K["task2"], K["task3"], K["task4"]
line = "The line: P(fraud) > 4.76%"
key_numbers = pd.DataFrame([
    key_row("Transactions", k1["transactions"], "transactions", "Size of the file (20 months)", "—", "Rows", "Data"),
    key_row("Fraud rate", round(100 * k1["fraud_rate"], 2), "% of transactions", f"{k1['frauds']} frauds", "Lower is better", "Mean of Fraud_Flag", "Task 1"),
    key_row("Fraud by money", round(100 * k1["fraud_rate_by_money"], 2), "% of money moved", f"₹{k1['fraud_crore']} crore lost to fraud", "Lower is better",
            "Fraud ₹ ÷ all ₹", "Task 1"),
    key_row("Columns that separate fraud", "2 of 16 (Amount, Amount_Ratio)", "—", "Only the amount and amount vs the customer's usual carry signal",
            "—", "Significant after adjusting for 16 tests and single-column ROC-AUC ≥ 0.60", TAB1),
    key_row("Supervised model PR-AUC (test)", f"{k2['test']['Chosen']['PR_AUC']:.3f} vs {k2['test']['Amount alone']['PR_AUC']:.3f} (amount alone)",
            "0–1 (fraud base rate 0.024)", "How well it ranks frauds first", "Higher is better", "Time-ordered test set (6,000)", TAB2),
    key_row("Supervised model ROC-AUC (test)", round(k2["test"]["Chosen"]["ROC_AUC"], 3), "0.5 = coin flip", "Ranking quality", "Higher is better", "Test set", TAB2),
    key_row("Isolation Forest PR-AUC (test)", round(k3["test"]["Isolation Forest (a)"]["PR-AUC"], 3), "0–1", "Anomaly detection, no labels", "Higher is better; worse than both",
            "Test set", TAB3),
    key_row("The line", "P(fraud) > 4.76%", "—", "Investigate above it", "—", "₹500 ÷ (₹10,000 + ₹500)", TAB4),
    key_row("Investigations per 1,000", k4["test"][line]["Investigated per 1,000"], "per 1,000", "Workload", "—", "Test set", TAB4),
    key_row("Frauds caught / fraud ₹ caught", f"{100 * k4['test'][line]['Frauds caught']:.0f}% / {100 * k4['test'][line]['Fraud ₹ caught']:.0f}%", "%",
            "Share caught by the rule", "Higher is better", "Test set", TAB4),
    key_row("Saving vs no screening", f"{100 * k4['test'][line]['Saving %']:.0f}% (brief's costs); 75% (real money)", "%", "Cost reduction", "Higher is better",
            "Cost per 1,000 vs investigate nothing", TAB4),
    key_row("Cost of fraud risk with the rule (to Module 9)", round(100 * (lost_rule + check_cost) / moved, 2), "% of money moved", "Fraud lost + checking",
            "Lower is better (6.13% with no screening)", "Hand-off recipe", "Hand-off"),
])

board_actions = pd.DataFrame([
    action_row(1, "Adopt the rule: investigate when the chance of fraud is above 4.76%", "Real saving ₹4.98 lakh per 1,000 transactions",
               "About 79 checks per 1,000; catches 52% of frauds and 80% of fraud money", TAB4),
    action_row(2, "Settle the two cost assumptions before staffing the team", "If a missed fraud costs 40× a check (not 20×), checks nearly triple to 223 per 1,000",
               "The line moves with the cost ratio", "Report §6"),
    action_row(3, "Consider the finance-view rule if investigators can be added", "₹26,000 more saved per 1,000; checks double to 157", "Ranks by chance × amount", f"{TAB4} (Decision (finance view))"),
    action_row(4, "Don't run anomaly detection as the main screen", "It saves only 13%", "Adds just 3–6 frauds the model misses", TAB3),
    action_row(5, "Collect real device fingerprints, login and location history, payee details", "—", "To find the ordinary-looking third of frauds", "Report §10"),
    action_row(6, "Re-check the model and the line every quarter", "—", "Fraud patterns change", "Report §6"),
])

read_me = {
    "question": "NovaFin processes thousands of transactions every day. Management wants to identify suspicious transactions while minimizing unnecessary investigation.",
    "answer": ["Investigate a transaction when the fraud model's chance of fraud is above 4.76%: about 79 checks per 1,000 transactions, catching 52% of frauds and 80% of fraud money.",
               f"The cost of fraud risk falls from {100 * lost_none / moved:.2f}% of money moved with no screening to {100 * (lost_rule + check_cost) / moved:.2f}% with the rule.",
               "Amount carries almost all the signal; anomaly detection does worse than the supervised model."],
    "tasks": [("Task 1 — Explore", "FINAL_M3_T1_fraud_evidence.csv", "every column's evidence and verdict"),
              ("Task 2 — Supervised model", "FINAL_M3_T2_fraud_scores.csv", "every transaction's P(fraud) and the amount benchmark"),
              ("Task 3 — Anomaly detection", "FINAL_M3_T3_anomaly_scores.csv", "every transaction's anomaly score and Unusual flag"),
              ("Task 4 — Threshold", "FINAL_M3_T4_transaction_decisions.csv", "every transaction's expected costs and decision, two views")],
    "how_to_read": ["Set = train (first 24,000, model learned from) or test (last 6,000, never seen): business figures use test.",
                    "Full explanation: reports/module_3_report.md."],
}
task_tabs = [(TAB1, T1, "Task 1: every column tested, with p, effect size, ROC-AUC and verdict"),
             (TAB2, T2, "Task 2: every transaction's P(fraud) and benchmark score"),
             (TAB3, T3, "Task 3: every transaction's anomaly score and Unusual flag"),
             (TAB4, T4, "Task 4: every transaction's expected cost each way and decision")]

# Every column of every task tab, in one plain sentence (shown in the Read me tab)
COLUMN_GUIDE = {'Column': 'The data column tested for a link to fraud', 'Kind': 'Number or category', 'Groups': 'How many groups the column was split into for the test', 'Test': 'The statistical test used', 'p': 'Chance the link is luck (0 to 1); must be below 0.0031 (0.05 ÷ 16 tests) to count', "Cramér's V": 'Strength of the link for categories: 0 = none, 1 = perfect', 'ROC-AUC': 'How well the column alone separates fraud: 0.5 = no better than a coin flip, 1 = perfect', 'Direction': 'Whether higher values mean more or less fraud', 'Lowest group rate': 'Fraud rate in the group with the least fraud', 'Highest group rate': 'Fraud rate in the group with the most fraud', 'Verdict': 'Strong, Weak or Not informative, using the agreed rule', 'Verdict at plain 0.05': 'The verdict if the stricter adjustment for 16 tests were not applied', 'Transaction_ID': "The transaction's reference number", 'Set': 'train = first 24,000 transactions (model learned from them); test = last 6,000 (never seen)', 'Fraud_Flag': '1 if the transaction was fraud', 'Amount': 'Transaction amount in ₹', 'P_fraud': "The model's chance (0 to 1) that the transaction is fraud", 'P_benchmark': "The chance from 'amount alone', the simple rule the model must beat", 'Anomaly_Score': 'How unusual the transaction looks without using fraud labels; near 1 = very unusual', 'Anomaly_Score_Side': 'The same score from a second, side-check version of the method', 'Unusual': 'Yes if flagged as unusual', 'Amount (₹)': 'Transaction amount', 'P(fraud)': "The model's chance that it is fraud", 'Expected cost if let through (₹)': "P(fraud) × ₹10,000 (the brief's cost of a missed fraud)", 'Expected cost if investigated (₹)': "(1 − P(fraud)) × ₹500 (the brief's cost of checking an honest transaction)", "Decision (brief's costs)": 'Investigate if letting it through is expected to cost more than checking (chance above 4.76%)', 'Expected ₹ lost if let through (P × amount)': 'Finance view: the chance of fraud × the actual amount at stake', 'Decision (finance view)': 'Investigate if that expected loss beats the cost of checking', 'Actually fraud': 'What it turned out to be: Yes or No'}

if __name__ == "__main__" or "get_ipython" in globals():
    path = build_workbook(MODULE_DIR, 3, read_me, key_numbers, board_actions, task_tabs, handoff, column_guide=COLUMN_GUIDE, receiver="Module 9",
                          m9_inputs=pd.read_csv(MODULE_DIR / "outputs" / 'task4/module9_inputs.csv'))
    print("Saved:", path.name)
    print(handoff[["Figure", "Value", "Unit"]].to_string(index=False))

"""
Module 4 — final output workbook
================================

WHAT THIS FILE DOES
    Builds outputs/FINAL_M4_module_output.xlsx: the one file where Module 9, the Board, the presenter and the
    evaluator see everything Module 4 produced (project decision P-21). Tabs: Read me, Key numbers,
    Board actions, one tab per task's final file, Hand-off to Module 9, Decisions, Evidence index.

    The hand-off figures are computed here from the task files' rows, exactly as each row's
    "How it comes from the rows" says, so anyone can rebuild them from the workbook.

HOW TO USE
    Run after Tasks 1–3: runner cell "Final output workbook", or python helpers/m04_final_output.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

here = Path(__file__).resolve() if "__file__" in globals() else Path.cwd() / "helpers" / "m04_final_output.py"
MODULE_DIR = here.parents[1]
sys.path.insert(0, str(MODULE_DIR.parent / "scripts"))
from final_workbook import build_workbook, handoff_row, key_row, action_row   # noqa: E402

OUT = MODULE_DIR / "outputs"
K = {t: json.loads((OUT / t / "key_numbers.json").read_text(encoding="utf-8")) for t in ("task1", "task2", "task3")}
T1 = OUT / "task1" / "FINAL_M4_T1_churn_scores.csv"
T2 = OUT / "task2" / "FINAL_M4_T2_customer_value.csv"
T3 = OUT / "task3" / "FINAL_M4_T3_contact_list.csv"
TAB1, TAB2, TAB3 = "T1 churn scores", "T2 customer value", "T3 contact list"
s1, s2, s3 = pd.read_csv(T1), pd.read_csv(T2), pd.read_csv(T3)

# ---- Figures computed from the rows (the hand-off recipes) ----
fees = s2["From investments (1.8%)"]
balances_crore = fees.sum() / 0.018 / 1e7                                  # fee ÷ 1.8% = investment balance
joined = s2.merge(s1[["Customer_ID", "Churn_Flag"]], on="Customer_ID")
churn_loss = joined.loc[joined.Churn_Flag == 1, "From investments (1.8%)"].sum() / fees.sum()
net_yield = 0.018 * (1 - churn_loss)
list_value_crore = s3["CLV (₹)"].sum() / 1e7
churn_rate = s1.Churn_Flag.mean()
expected_loss_lakh = churn_rate * s3["CLV (₹)"].sum() / 1e5
ceiling = {cost: expected_loss_lakh - 1000 * cost / 1e5 for cost in (250, 500)}

handoff = pd.DataFrame([
    handoff_row("Fee yield on investment balances", round(1.8, 2), "% of balances a year", "Measured (+ our reading that it is fee income)",
                TAB2, "From investments (1.8%)", "The CLV rule's weight on Investment_Balance (Task 2 fits all 5,000 customers within ₹0.01 (one paisa))",
                "M4-19", "Return per ₹ of wealth-management balances, before churn"),
    handoff_row("Investment balances in the customer file", round(balances_crore, 2), "₹ crore", "Measured", TAB2,
                "From investments (1.8%)", "Sum of the column ÷ 1.8% ÷ 1 crore", "M4-19", "Size of the sample book (a sample, not NovaFin's whole book)"),
    handoff_row("Churn loss: share of balances held by leavers", round(100 * churn_loss, 2), "% of balances", "Measured", f"{TAB1} + {TAB2}",
                "Churn_Flag (T1), From investments (1.8%) (T2)", "Join on Customer_ID; sum of the T2 column where Churn_Flag = 1 ÷ sum of the T2 column",
                "M4-19", "Share of balances (and their fees) lost to leavers"),
    handoff_row("Net fee yield after churn", round(100 * net_yield, 2), "% of balances a year", "Measured", f"{TAB1} + {TAB2}",
                "as above", "1.80% × (1 − churn loss share)", "M4-19", "Use as Wealth management's return per ₹ deployed"),
    handoff_row("Value of the 1,000-customer contact list", round(list_value_crore, 2), "₹ crore", "Measured", TAB3, "CLV (₹)",
                "Sum of the column over all 1,000 rows ÷ 1 crore", "M4-18", "The value retention protects"),
    handoff_row("Expected loss on the list if nobody is called", round(expected_loss_lakh, 1), "₹ lakh", "Measured", f"{TAB1} + {TAB3}",
                "Churn_Flag (T1), CLV (₹) (T3)", "Churn rate (mean of Churn_Flag) × sum of CLV on the list ÷ 1 lakh", "M4-18",
                "The most retention could save before call costs"),
    handoff_row("Break-even call success rate at ₹250 / ₹500 a call",
                f"{100 * 2.5 / expected_loss_lakh:.0f}% / {100 * 5 / expected_loss_lakh:.0f}%", "% of would-be leavers kept",
                "Assumption (call cost) + Measured", TAB3, "CLV (₹)", "Cost of 1,000 calls (₹2.5 / ₹5 lakh) ÷ expected loss on the list",
                "M4-18, M4-19", "The floor: calls pay off only above this success rate"),
    handoff_row("Ceiling: value retention could protect (every call works)",
                f"₹{ceiling[250]:.1f} lakh ({100 * ceiling[250] / (list_value_crore * 100):.2f}%) / ₹{ceiling[500]:.1f} lakh ({100 * ceiling[500] / (list_value_crore * 100):.2f}%)",
                "at ₹250 / ₹500 a call (share of value contacted)", "Assumption (100% success, a ceiling only)", TAB3, "CLV (₹)",
                "Expected loss on the list − cost of 1,000 calls", "M4-19", "Upper bound only; too small to change the allocation"),
    handoff_row("Can churn be predicted from this data?", "No", "—", "Conclusion", TAB1, "Churn predictable",
                "Every row carries the verdict (no model or rule beats chance)", "M4-16", "Fund no model-driven retention programme until a randomised test"),
    handoff_row("Module 9 inputs: Wealth management: fees on client balances", "1.77 (bad year 1.39)", "% a year per ₹",
                "Measured + Assumption", "Module 9 inputs", "Return per ₹ deployed, Bad-year result per ₹", "Final notebook step 'What goes to Module 9'", "M4-20",
                "Standard fields for Module 9; gaps marked as assumptions"),
    handoff_row("Assumptions behind these figures",
                "New money earns like this customer book; CLV and churn period not stated in the data; call success rate unknown", "—",
                "Assumption", "—", "—", "—", "M4-19", "State these when using the figures"),
])

key_numbers = pd.DataFrame([
    key_row("Customers", len(s1), "customers", "Size of the customer file", "—", "Rows in the file", "Data"),
    key_row("Churn rate", round(100 * churn_rate, 2), "%", "Share of customers who left (89 of 5,000)", "Lower is better",
            "Mean of Churn_Flag", f"{TAB1}"),
    key_row("Chosen churn model's ROC-AUC (logistic regression)", round(K["task1"]["setups"]["Logistic regression"]["roc_auc"], 3), "0.5 = coin flip, 1 = perfect",
            "How well the model ranks leavers above stayers", "Higher is better; here no better than chance",
            "Out-of-fold scores, 5-fold cross-validation", "Task 1 key numbers"),
    key_row("Shuffled-label p (logistic regression)", round(K["task1"]["setups"]["Logistic regression"]["shuffle_p"], 2), "0–1",
            "Chance a model trained on shuffled labels does as well", "Small (below 0.01) would mean real signal; here large",
            "Refit on shuffled Churn_Flag 100 times", "Task 1 key numbers"),
    key_row("Total customer value (CLV)", K["task2"]["total_clv_crore"], "₹ crore", "What all 5,000 customers are worth to the bank",
            "—", "Sum of Estimated_CLV", TAB2),
    key_row("CLV rule: largest gap to the file's CLV", K["task2"]["rule_max_gap"], "₹", "How exactly the rule reproduces CLV",
            "Smaller is better; under ₹0.01 (one paisa) is exact", "4% × income + 3% × account + 1.2% × loan + 1.8% × investment − ₹5,000 × complaints", TAB2),
    key_row("Cost of complaints", K["task2"]["complaints_cost_crore"], "₹ crore", "Customer value lost to complaints (₹5,000 each)",
            "Lower is better", "₹5,000 × complaints, summed", TAB2),
    key_row("Value held by the 1,000 on the contact list", round(list_value_crore, 2), "₹ crore", "Value in the top 20% of customers by CLV",
            "—", "Sum of CLV (₹) on the list", TAB3),
    key_row("Share of all value on the list", round(100 * K["task2"]["top1000_share_of_clv"], 1), "%", "How concentrated value is",
            "—", "List value ÷ total CLV", TAB3),
    key_row("Actual churn by group (p for a difference)", f"1.1%–2.0% (p {K['task3']['groups_p']:.2f})", "%", "Whether the four groups churn differently",
            "p below 0.05 would mean they do; here they don't", "Chi-square test across the four groups", "Task 3"),
    key_row("Back-test: leavers reached by the list", f"{K['task3']['backtest']['Recommended: the high-CLV groups']['Leavers reached (of 89)']:.0f} of 89",
            "customers", "Leavers on the list (not known when choosing)", "Random 1,000 reach 17.7 on average", "Count of Left = Yes on the list", TAB3),
    key_row("Back-test: value of leavers reached",
            round(K["task3"]["backtest"]["Recommended: the high-CLV groups"]["Value of leavers reached (₹ lakh)"], 1), "₹ lakh",
            "Value the list would have protected if every call worked", "Random 1,000: ₹11.2 lakh", "Sum of CLV of leavers on the list", TAB3),
    key_row("Net fee yield after churn (to Module 9)", round(100 * net_yield, 2), "% a year", "Wealth management's return per ₹ of balances",
            "Higher is better", "1.80% × (1 − churn loss share)", "Hand-off"),
])

board_actions = pd.DataFrame([
    action_row(1, "Call the 1,000 highest-value customers, in the call order given", f"₹{list_value_crore:.2f} crore of value in contact (42%)",
               "Churn can't be predicted, so value decides; the list reaches the most value of every way tested", f"{TAB3}; report §1"),
    action_row(2, "Test before scaling: call a random half of a test group and compare who leaves", "Measures the real success rate",
               "Break-even needs 10% (₹250 a call) or 20% (₹500) of would-be leavers kept", "Hand-off; report §7"),
    action_row(3, "Reduce complaints", f"₹{K['task2']['complaints_cost_crore']} crore of customer value (12% of the book)",
               "Each complaint costs ₹5,000 of CLV; the one value driver the bank controls", f"{TAB2}"),
    action_row(4, "Collect month-by-month data (balances, transactions, product closures, service calls)", "—",
               "It is what could make churn predictable", "Report §9"),
])

read_me = {
    "question": "NovaFin wants to reduce customer attrition. Management asks: Which customers should relationship managers prioritize for retention?",
    "answer": [f"Prioritise the 1,000 highest-value customers: the 278 in 'Priority retention' first, then the 722 in 'Protect', each by CLV. They hold ₹{list_value_crore:.2f} crore, 42% of all customer value.",
               "Churn can't be predicted from this data (no model or rule beats chance), so value, which is known exactly, decides the list.",
               f"Calling pays off only if it keeps at least 10–20% of would-be leavers; even if every call worked it protects at most ₹{ceiling[500]:.1f}–{ceiling[250]:.1f} lakh."],
    "tasks": [("Task 1 — Churn prediction", "FINAL_M4_T1_churn_scores.csv", "each customer's chance of churn, labelled 'no better than chance'"),
              ("Task 2 — Customer lifetime value", "FINAL_M4_T2_customer_value.csv", "each customer's CLV and its ₹ sources"),
              ("Task 3 — Prioritisation", "FINAL_M4_T3_contact_list.csv", "the 1,000 to call, in order, with the reason")],
    "how_to_read": ["Money is in rupees: 1 lakh = ₹1,00,000; 1 crore = ₹100 lakh.",
                    "Hand-off rows point to a tab and column; follow 'How it comes from the rows' to rebuild the figure.",
                    "Full explanation: reports/module_4_report.md."],
}
task_tabs = [(TAB1, T1, "Task 1: every customer's chance of churn (out-of-fold), with the verdict"),
             (TAB2, T2, "Task 2: every customer's CLV split into its ₹ sources"),
             (TAB3, T3, "Task 3: the 1,000 customers to call, in call order, with group and reason")]

# Every column of every task tab, in one plain sentence (shown in the Read me tab)
COLUMN_GUIDE = {'Customer_ID': "The customer's reference number", 'Churn_Flag': '1 if the customer left the bank', 'P_churn': "The model's chance (0 to 1) that the customer leaves; no better than chance on this data", 'Model': 'Which model produced the score', 'Churn predictable': "The verdict: churn can't be predicted from this data", 'Estimated_CLV': 'Customer lifetime value: what the customer is worth to the bank, in ₹', 'CLV_from_rule': 'The same value from the exact rule found in Task 2', 'From income (4%)': 'The part of the value that comes from income (4% of annual income)', 'From account balance (3%)': 'The part from the account balance (3%)', 'From loans (1.2%)': 'The part from loan balances (1.2%)', 'From investments (1.8%)': 'The part from investment balances (1.8%): read as the fee the bank earns on them', 'Complaints (−₹5,000 each)': 'Value lost to complaints: ₹5,000 for each', 'CLV_out_of_fold_estimate': 'The value predicted by a model that never saw this customer (a fairness check)', 'Call order': 'Position in the call list: 1 = call first', 'Group': 'Priority retention, Protect, Low-cost intervention or Maintain', 'CLV (₹)': 'What the customer is worth to the bank', 'Chance of churn (no better than chance)': "The model's chance the customer leaves; shown, but no better than a guess", 'Why contact': 'Why the customer is on the list, in plain words', 'Left (back-test only, not known when calling)': 'Whether they actually left; used only to check the list afterwards'}

if __name__ == "__main__" or "get_ipython" in globals():
    path = build_workbook(MODULE_DIR, 4, read_me, key_numbers, board_actions, task_tabs, handoff, column_guide=COLUMN_GUIDE, receiver="Module 9",
                          m9_inputs=pd.read_csv(MODULE_DIR / "outputs" / 'task3/module9_inputs.csv'))
    print("Saved:", path.name)
    pd.set_option("display.max_colwidth", 80, "display.width", 200)
    print(handoff[["Figure", "Value", "Unit", "Status"]].to_string(index=False))

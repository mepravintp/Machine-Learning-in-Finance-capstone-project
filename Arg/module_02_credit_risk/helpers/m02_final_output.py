"""
Module 2 — final output workbook
================================

WHAT THIS FILE DOES
    Builds outputs/FINAL_M2_module_output.xlsx: the one file where Module 9, the Board, the presenter and the
    evaluator see everything Module 2 produced (project decision P-21). Tabs: Read me, Key numbers,
    Board actions, one tab per task's final file, Hand-off to Module 9, Decisions, Evidence index.
    Hand-off figures (lending returns by segment) are computed here from the loan decision file's rows.

HOW TO USE
    Run after Tasks 1–3: runner cell "Final output workbook", or python helpers/m02_final_output.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

here = Path(__file__).resolve() if "__file__" in globals() else Path.cwd() / "helpers" / "m02_final_output.py"
MODULE_DIR = here.parents[1]
sys.path.insert(0, str(MODULE_DIR.parent / "scripts"))
from final_workbook import build_workbook, handoff_row, key_row, action_row   # noqa: E402

OUT = MODULE_DIR / "outputs"
K = {t: json.loads((OUT / t / "key_numbers.json").read_text(encoding="utf-8")) for t in ("task1", "task2", "task3")}
T1 = OUT / "task1" / "FINAL_M2_T1_default_predictions.csv"
T2 = OUT / "task2" / "FINAL_M2_T2_risk_categories.csv"
T3 = OUT / "task3" / "FINAL_M2_T3_loan_decisions.csv"
TAB1, TAB2, TAB3 = "T1 default predictions", "T2 risk categories", "T3 loan decisions"
L = pd.read_csv(T3)
AMT, INT, ECL = "Loan_Amount (₹)", "Interest a year (₹)", "ECL a year (₹)"


def segment(rows: pd.DataFrame) -> dict:
    """₹ crore lent, average rate (interest ÷ loans), ECL rate (ECL ÷ loans), expected return = rate − ECL rate."""
    amt = rows[AMT].sum()
    return {"crore": amt / 1e7, "rate": rows[INT].sum() / amt, "ecl": rows[ECL].sum() / amt,
            "ret": (rows[INT].sum() - rows[ECL].sum()) / amt}


appr = L[L.Decision == "Approve"]
seg = {"Retail lending, approved": segment(appr[appr.Customer_Type == "Retail"]),
       "Corporate lending, approved": segment(appr[appr.Customer_Type == "Corporate"]),
       "All lending, approved": segment(appr), "Today's whole book": segment(L)}
review_crore = L.loc[L.Decision == "Review", AMT].sum() / 1e7
reject_crore = L.loc[L.Decision == "Reject", AMT].sum() / 1e7

rows = []
for name, v in seg.items():
    cond = {"Retail lending, approved": "Decision = Approve and Customer_Type = Retail",
            "Corporate lending, approved": "Decision = Approve and Customer_Type = Corporate",
            "All lending, approved": "Decision = Approve", "Today's whole book": "all 5,000 rows"}[name]
    use = "Today's book, for comparison: what the bank earns now" if name.startswith("Today") else f"Return per ₹ lent for {name.split(',')[0]}"
    rows += [
        handoff_row(f"{name}: ₹ lent", round(v["crore"], 2), "₹ crore", "Measured", TAB3, AMT, f"Sum of {AMT} where {cond} ÷ 1 crore", "M2 rule (Task 3)", "Capacity"),
        handoff_row(f"{name}: expected return a year", round(100 * v["ret"], 2), "% of ₹ lent (before cost of funds and running costs)",
                    "Measured (LGD 40% assumed)", TAB3, f"{INT}, {ECL}, {AMT}",
                    f"(sum of interest − sum of ECL) ÷ sum of loan, where {cond}; = average rate {100 * v['rate']:.2f}% − ECL rate {100 * v['ecl']:.2f}%",
                    "M2 rule; assignment guide: return = rate − ECL rate", use),
    ]
rows += [
    handoff_row("Review queue: lendable once fixed", round(review_crore, 1), "₹ crore", "Measured", TAB3, f"{AMT}, Decision, Action",
                f"Sum of {AMT} where Decision = Review ÷ 1 crore; each row's Action says what to fix", "M2 rule",
                "Extra volume on revised terms (re-priced loans cover their expected loss, so they add volume, not margin)"),
    handoff_row("Rejected (not lendable within risk appetite)", round(reject_crore, 1), "₹ crore", "Measured", TAB3, f"{AMT}, Decision",
                f"Sum of {AMT} where Decision = Reject ÷ 1 crore", "M2 rule (PD above 30%)", "Exclude"),
    handoff_row("Approved lending after a 2% cost of funds", round(100 * seg["All lending, approved"]["ret"] - 2, 1), "% a year", "Assumption (2% cost of funds) + Measured",
                TAB3, f"{INT}, {ECL}, {AMT}", "Expected return of all approved lending − 2%", "Module 2 report §8", "A more realistic return; the data has no cost of funds"),
    handoff_row("Approved lending: bad year (every PD doubled)", "-2.15", "% of ₹ lent a year", "Stress estimate (PD × 2, LGD 40%)", "Module 9 inputs",
                "Bad-year result per ₹ (% a year)", "(interest − PD × 2 × 40% × loan) ÷ ₹ lent (Task 3 step 11b)", "M2-23",
                "Lending's bad-year loss per ₹; the severe case (LGD 60%) is -7.61%"),
    handoff_row("Review queue: return and bad year", "0.96% normal; -7.83% bad year",
                "% of ₹ lent a year", "Measured + Stress estimate", "Module 9 inputs", "module9_lending_risk.csv (Review rows)", "Same recipe, Review loans", "M2-23",
                "Volume only after re-pricing; not a source of return"),
    handoff_row("Assumptions behind these figures", "LGD 40% (no recovery data); one-year view; no cost of funds or running costs in the data; synthetic data (Retail and Corporate behave alike)",
                "—", "Assumption", "—", "—", "—", "Module 2 decisions", "State these when using the figures"),
]
handoff = pd.DataFrame(rows)

k1, k2, k3 = K["task1"], K["task2"], K["task3"]
key_numbers = pd.DataFrame([
    key_row("Loans", k1["loans"], "loans", "Loans in the book", "—", "Rows in the file", "Data"),
    key_row("Default rate", round(100 * k1["default_rate"], 2), "%", "Share of loans that defaulted", "Lower is better", "Mean of Default_Flag", "Task 1"),
    key_row("Book size", k1["book_crore"], "₹ crore", "Money lent", "—", "Sum of Loan_Amount", "Task 1"),
    key_row("Scorecard ROC-AUC (cross-validation)", k1["cv"]["Lasso"]["ROC_AUC"], "0.5 = coin flip, 1 = perfect",
            f"How well the lasso scorecard ranks defaulters; the bank's own price scores {k1['cv']['Champion: interest rate']['ROC_AUC']}",
            "Higher is better", "25 rounds of cross-validation", "Task 1"),
    key_row("Scorecard ROC-AUC (1,000 test loans)", round(k1["test"]["Lasso"]["ROC_AUC"], 3), "0–1",
            f"On untouched loans; the bank's price {k1['test']['Champion: interest rate']['ROC_AUC']:.3f}; gain not proven at 95% (DeLong p 0.065)",
            "Higher is better", "Fit on 4,000 loans, tested on 1,000", TAB1),
    key_row("Expected credit loss vs actual", f"₹{k2['expected_loss_crore']} crore vs ₹{k2['actual_loss_crore']} crore", "₹ crore",
            "Whether the PDs are right in rupees", "Closer is better: within 0.5%", "ECL = PD × 40% × loan, summed", TAB2),
    key_row("Risk bands: actual default rate", " / ".join(f"{b} {100 * k2['band_actual_rate'][b]:.1f}%" for b in k2["bands"]), "%",
            "The brief's four bands, all justified by four tests", "Should rise from Low to Very High", "Default rate per band", TAB2),
    key_row("Decisions", " / ".join(f"{d} {k3['decisions'][d]:,} (₹{k3['decision_crore'][d]} crore)" for d in ("Approve", "Review", "Reject")), "loans (₹ crore)",
            "The rule's split of the book", "—", "Decision rule (Task 3)", TAB3),
    key_row("Default rate: approved vs today's book", f"{100 * k3['decision_default_rate']['Approve']:.1f}% vs {100 * k3['decision_default_rate']["Today's book"]:.1f}%",
            "%", "How much safer the approved loans are", "Lower is better", "Mean of Default_Flag per group", TAB3),
    key_row("Interest − actual loss a year: approved vs today's book",
            f"₹{k3['earn_above_actual_loss_crore']['Approve']} crore vs ₹{k3['earn_above_actual_loss_crore']["Today's book"]} crore", "₹ crore",
            "What each earns above its credit losses", "Higher is better", "Sum of interest − actual losses", TAB3),
    key_row("Cost of funds at which today's book breaks even", round(100 * k3["book_breakeven_cost"], 2), "% a year",
            "Above this, today's book loses money", "Higher is safer", "Book's (interest − loss) ÷ ₹ lent", TAB3),
])

board_actions = pd.DataFrame([
    action_row(1, "Adopt the decision rule now: approve 2,934 loans, reject 1,021", f"Approved ₹{k3['decision_crore']['Approve']} crore earns ₹{k3['earn_above_actual_loss_crore']['Approve']} crore a year above losses",
               "Approved loans default 11.3% vs 19.9% today", TAB3),
    action_row(2, "Work the Review queue using each loan's Action", f"Up to ₹{review_crore:.1f} crore more lending", "301 need ≤ 1 point more interest; others need collateral or a committee check", f"{TAB3} (Action column)"),
    action_row(3, "Re-price the whole book by scorecard band, starting with Retail", "Today's book loses money above a 0.48% cost of funds",
               "The bank's price charges safer borrowers more than riskier ones", TAB2),
    action_row(4, "Win the 220 Low-risk borrowers with sharper rates", "Safest growth available (3.2% default)", "The bank's price can't see them", TAB2),
    action_row(5, "Keep approval below about 73% unless the scorecard is re-checked", "—", "Above that, the bank's price ranks slightly better", "Report §6.3"),
    action_row(6, "Choose the risk appetite knowingly", "Cap 4% vs 6%: ₹103.6 crore less lent, ₹2.34 crore a year less earned, defaults 8.7%",
               "Trade-off table", "Report §5.3"),
    action_row(7, "Collect recovery amounts, cost of funds, and outcomes for a sample of rejects", "—", "LGD and cost of funds are assumed today", "Report §9"),
    action_row(8, "Re-check calibration and the cap each quarter; watch the largest loans", "—", "The model under-predicts the top 2% of loan sizes", "Report §5.2"),
])

read_me = {
    "question": "NovaFin wants to increase lending while reducing defaults. Management asks: Which loans should we approve, reject or send for manual review?",
    "answer": [f"Approve 2,934 loans (₹{k3['decision_crore']['Approve']} crore), send 1,045 to Review (₹{k3['decision_crore']['Review']} crore, each with its fix), reject 1,021 (₹{k3['decision_crore']['Reject']} crore).",
               "Approved loans default 11.3% against 19.9% today and earn more than three times what today's whole book earns above its losses.",
               "The bank's pricing is the core problem: today's book breaks even at a 0.48% cost of funds."],
    "tasks": [("Task 1 — PD model", "FINAL_M2_T1_default_predictions.csv", "each loan's PD from the scorecard and the bank's price"),
              ("Task 2 — Risk categories", "FINAL_M2_T2_risk_categories.csv", "each loan's calibrated PD and risk band"),
              ("Task 3 — Decision", "FINAL_M2_T3_loan_decisions.csv", "every loan: ECL, return, each check, decision, action, full reason")],
    "how_to_read": ["Money columns are in rupees; ₹ crore figures divide by 1,00,00,000.", "Full explanation: reports/module_2_report.md."],
}
task_tabs = [(TAB1, T1, "Task 1: every loan's predicted PD (scorecard and bank's price), train/test set"),
             (TAB2, T2, "Task 2: every loan's PD and risk category"),
             (TAB3, T3, "Task 3: the decision file, one row per loan")]

# Every column of every task tab, in one plain sentence (shown in the Read me tab)
COLUMN_GUIDE = {'Loan_ID': "The loan's reference number", 'Set': 'train = used to build the model; test = 1,000 loans kept aside to check it fairly', 'Default_Flag': '1 if the borrower failed to repay, 0 if they repaid', 'PD_champion': "Chance of default implied by the bank's own interest rate (the method used today)", 'PD_challenger': 'Chance of default from the new scorecard model', 'Predicted_PD': "The scorecard's chance (0 to 1) that the borrower fails to repay within a year", 'Risk_Category': "The brief's risk band from that chance: Low, Medium, High or Very High", 'Champion_Category': "The band the bank's own price would give, for comparison", 'Customer_Type': 'Retail (individuals) or Corporate (companies)', 'Loan_Amount (₹)': 'Money lent', 'Collateral_Value (₹)': 'Value of the security the borrower pledged', 'ECL a year (₹)': 'Expected credit loss: the loss to expect in a year = chance of default × 40% lost if they default × amount', 'Interest a year (₹)': 'Interest the loan earns in a year at the rate charged', 'Rate charged (%)': 'The interest rate the bank charges', 'Expected loss rate (%)': 'ECL as a share of the loan', 'Expected return (%)': 'Rate charged − expected loss rate: what the loan earns after expected losses, before funding and running costs', 'Required rate (%)': "The lowest rate that would cover the loan's expected loss", 'Decision': 'Approve, Review (fix the price, security or size first) or Reject', 'Check: PD': 'Is the chance of default within the 30% limit?', 'Check: interest covers expected loss': 'Does the rate charged cover the expected loss?', 'Check: loan size': 'Is the loan small enough not to need a credit committee?', 'Check: collateral': 'Does the security cover enough of the loan?', 'Check: risk appetite': "Does it fit the bank's 6% limit on expected losses?", 'Decision path': 'Which route through the rule produced the decision', 'Action': 'What to do for a Review loan: re-price, add collateral, or committee check', 'Full reason': 'The decision and every check, in plain sentences'}

if __name__ == "__main__" or "get_ipython" in globals():
    path = build_workbook(MODULE_DIR, 2, read_me, key_numbers, board_actions, task_tabs, handoff, column_guide=COLUMN_GUIDE, receiver="Module 9",
                          m9_inputs=pd.read_csv(MODULE_DIR / "outputs" / "task3/module9_inputs.csv"))
    print("Saved:", path.name)
    print(handoff[["Figure", "Value", "Unit"]].to_string(index=False))

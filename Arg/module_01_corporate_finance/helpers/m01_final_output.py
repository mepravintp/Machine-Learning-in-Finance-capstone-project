"""
Module 1 — final output workbook
================================

WHAT THIS FILE DOES
    Builds outputs/FINAL_M1_module_output.xlsx: the one file where Module 9, the Board, the presenter and the
    evaluator see everything Module 1 produced (project decision P-21). Tabs: Read me, Key numbers,
    Board actions, one tab per task's final file, Hand-off to Module 9, Decisions, Evidence index.
    Hand-off figures are computed here from the decision file's rows, as each row's recipe says.

HOW TO USE
    Run after Tasks 1–3: runner cell "Final output workbook", or python helpers/m01_final_output.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

here = Path(__file__).resolve() if "__file__" in globals() else Path.cwd() / "helpers" / "m01_final_output.py"
MODULE_DIR = here.parents[1]
sys.path.insert(0, str(MODULE_DIR.parent / "scripts"))
from final_workbook import build_workbook, handoff_row, key_row, action_row   # noqa: E402

OUT = MODULE_DIR / "outputs"
K = {t: json.loads((OUT / t / "key_numbers.json").read_text(encoding="utf-8")) for t in ("task1", "task2", "task3")}
T1 = OUT / "task1" / "FINAL_M1_T1_business_unit_view.csv"
T2 = OUT / "task2" / "FINAL_M1_T2_success_probability.csv"
T3 = OUT / "task3" / "FINAL_M1_T3_initiative_decisions.csv"
TAB1, TAB2, TAB3 = "T1 business unit view", "T2 success probability", "T3 initiative decisions"
d = pd.read_csv(T3)

# ---- Figures computed from the decision file's rows ----
inv = d.groupby("Decision")["Investment (₹ lakh)"].sum() / 100            # ₹ crore
enpv = d.groupby("Decision")["Expected NPV (₹ lakh)"].sum()                # ₹ lakh
count = d.Decision.value_counts()
fund = d[d.Decision == "Fund"]
ceiling = inv["Fund"] + inv["Review"]
cb_review = d[(d.Decision == "Review") & (d.Business_Unit == "Corporate Banking")]["Investment (₹ lakh)"].sum() / 100
cb_count = int(((d.Decision == "Review") & (d.Business_Unit == "Corporate Banking")).sum())

_dep = pd.read_csv(MODULE_DIR / "outputs" / "task3" / "10c_business_unit_returns.csv")
_dep = _dep[_dep.Scope.str.startswith("Fund")].set_index("Business unit")
handoff = pd.DataFrame([
    handoff_row("Ready to fund now", round(inv["Fund"], 2), "₹ crore", "Measured", TAB3, "Investment (₹ lakh), Decision",
                "Sum of Investment where Decision = Fund ÷ 100", "M1 decision rule (Task 3)", "Commit now"),
    handoff_row("The initiatives to fund now", "; ".join(f"{r.Initiative_ID} ({r['Funding condition']})" for _, r in fund.iterrows()),
                "—", "Conclusion", TAB3, "Initiative_ID, Funding condition", "Rows where Decision = Fund", "M1 decision rule",
                "Fund in stages = release money at milestones"),
    handoff_row("Possible after review (upper bound)", round(inv["Review"], 2), "₹ crore", "Measured", TAB3, "Investment (₹ lakh), Decision",
                "Sum of Investment where Decision = Review ÷ 100", "M1 decision rule", "Money flows only if a review approves; in the Priority order given"),
    handoff_row("Ceiling for strategic initiatives", round(ceiling, 1), "₹ crore", "Measured", TAB3, "Investment (₹ lakh), Decision",
                "Fund + Review totals", "M1 decision rule", "Most this business can absorb"),
    handoff_row("Ceiling as a share of the ₹1,000 crore", round(ceiling / 10, 1), "% of ₹1,000 crore", "Measured", TAB3, "as above",
                "Ceiling ÷ ₹1,000 crore", "M1 decision rule", "The rest of the capital must go to other businesses"),
    handoff_row("Largest Review exposure: Corporate Banking", round(cb_review, 1), f"₹ crore ({cb_count} initiatives)", "Measured", TAB3,
                "Investment (₹ lakh), Decision, Business_Unit", "Sum of Investment where Decision = Review and Business_Unit = Corporate Banking ÷ 100",
                "M1 decision rule", "Ask why past Corporate Banking initiatives failed before approving"),
    handoff_row("Not to be funded", round(inv["Reject"], 1), f"₹ crore ({count['Reject']} initiatives)", "Measured", TAB3,
                "Investment (₹ lakh), Decision", "Sum of Investment where Decision = Reject ÷ 100", "M1 decision rule", "Exclude from the allocation"),
    handoff_row("Expected NPV of the Fund group", round(enpv["Fund"], 1), "₹ lakh", "Measured", TAB3, "Expected NPV (₹ lakh), Decision",
                "Sum of Expected NPV where Decision = Fund", "M1 decision rule", "Value created by the money committed now"),
    handoff_row("Assumptions behind these figures",
                "3 years of cash flow in the data (year 3 repeated for payback beyond); 5-year payback limit; cost of money 6%; P(Success) from a weak model (ROC-AUC 0.58)",
                "—", "Assumption", "—", "—", "—", "Module 1 decisions", "State these when using the figures"),
    handoff_row("Return per ₹ of deployable initiatives (Fund + Review)", f"{_dep.loc['All units', 'Expected return (% a year)']:.1f}% a year (1-in-20 bad case {_dep.loc['All units', '1-in-20 bad case (% a year)']:.1f}%)",
                "% a year", "Measured + Assumption (years 4–5 = year 3; a failure returns no cash)", "Module 9 inputs", "Return per ₹ deployed, Bad-year result per ₹",
                "IRR over 5 years of the units' cash × P(Success) (Task 3 step 10c)", "M1-24", "Return for strategic initiatives; small, staged, locked in about 5 years"),
    handoff_row("Return per ₹ by business unit", "; ".join(f"{u} {r['Expected return (% a year)']:.1f}%" for u, r in _dep.drop(index="All units").iterrows()),
                "% a year", "Measured + Assumption", "Module 9 inputs", "Category, Return per ₹ deployed (% a year)", "One row per unit", "M1-24",
                "Gives Digital banking, Payments and Wealth a return per ₹ of capital (no other file has one)"),
])

k2, k3 = K["task2"], K["task3"]
key_numbers = pd.DataFrame([
    key_row("Initiatives", K["task1"]["rows"], "initiatives", "Strategic initiatives assessed", "—", "Rows in the file", "Data"),
    key_row("Historical success rate", round(100 * K["task1"]["success_rate"], 1), "%", "Share that succeeded", "Higher is better",
            "Mean of Historical_Success", "Task 1"),
    key_row("Capital requested", K["task1"]["total_investment_crore"], "₹ crore", "Total investment asked for", "—", "Sum of Initial_Investment", "Task 1"),
    key_row("Risk rating vs success (p)", K["task1"]["risk_chi_square_p"], "0–1", "Whether success differs by risk rating (Low 89% vs Medium/High 69–70%)",
            "Below 0.05 = real difference; here yes", "Chi-square test", "Task 1"),
    key_row("Initiatives with a positive 3-year NPV", K["task1"]["npv_3yr_positive"], "of 180", "How many repay their investment within the data's 3 years",
            "—", "NPV of 3 years' cash at the cost of money", "Task 1"),
    key_row("Chosen model", k2["chosen_model"], "—", "Model that turns inputs into P(Success)", "—", "Lowest Brier score, simplest when tied", "Task 2"),
    key_row("Chosen model's ROC-AUC", f"{k2['chosen_roc_auc']} ± {k2['chosen_roc_auc_std']}", "0.5 = coin flip, 1 = perfect",
            "How well it ranks successes above failures", "Higher is better; weak here", "Repeated 5-fold cross-validation", "Task 2"),
    key_row("Shuffled-label p (lasso)", k2["shuffled_label_p"]["Lasso"], "0–1", "Chance shuffled labels do as well", "Below 0.05 = real signal; not here",
            "Refit on shuffled labels", "Task 2"),
    key_row("Flagged at risk", k2["at_risk_count"], "of 180", f"P(Success) below 0.767; they failed {100 * k2['at_risk_actual_failure_rate']:.0f}% of the time vs {100 * k2['not_at_risk_actual_failure_rate']:.0f}%",
            "—", "Cut-off = the historical success rate", TAB2),
    key_row("Fund", f"{count['Fund']} initiatives, ₹{inv['Fund']:.2f} crore", "—", "Fund now", "—", "Decision rule (Task 3)", TAB3),
    key_row("Review", f"{count['Review']} initiatives, ₹{inv['Review']:.2f} crore", "—", "Attractive but uncertain; examine in priority order", "—", "Decision rule", TAB3),
    key_row("Reject", f"{count['Reject']} initiatives, ₹{inv['Reject']:.1f} crore", "—", "Pay back too late or never, fail the hurdle, or flagged at risk",
            "—", "Decision rule", TAB3),
])

board_actions = pd.DataFrame([
    action_row(1, "Fund now: 1075 in full; 1062 in stages, releasing money at milestones", f"₹{inv['Fund']:.2f} crore; Expected NPV +₹{enpv['Fund']:.1f} lakh",
               "Only initiatives passing value, risk, payback, hurdle, model and loss tolerance", TAB3),
    action_row(2, "Review the 38 in the order given: the 6 value-creating Medium/High-risk projects first, then the 32 slow payers", f"Up to ₹{inv['Review']:.1f} crore",
               "Value arrives after year 3 or risk is above Low", f"{TAB3} (Priority column)"),
    action_row(3, "Look hardest at Corporate Banking's Review projects", f"₹{cb_review:.1f} crore, {cb_count} initiatives",
               "Largest Review exposure of any unit", TAB3),
    action_row(4, "Screen every future initiative on risk first; pilot Medium/High-risk proposals", "—",
               "Low risk is the one reliable signal of success (89% vs 69–70%)", TAB1),
    action_row(5, "Decide how patient to be: the payback limit sets the Review list", "5 years: 38 in Review; 6 years: 47",
               "Each extra year rests on cash flows the data doesn't cover", "Report §5.3b"),
    action_row(6, "Don't use business-case numbers to predict success; use them to value", "—", "NPV, cash return and revenue plans don't predict success", "Report §4"),
    action_row(7, "Collect sponsor track record, milestones and post-launch results", "—", "The model can't separate projects of the same risk rating", "Report §9"),
])

read_me = {
    "question": "NovaFin has several strategic initiatives competing for limited capital. Management wants to know: Which initiatives should receive funding?",
    "answer": [f"Fund 2 initiatives now (₹{inv['Fund']:.2f} crore): 1075 in full, 1062 in stages. Review 38 (up to ₹{inv['Review']:.1f} crore) in the priority order given. Reject 140.",
               "The bank's risk rating is the one reliable signal of success; machine learning confirmed it but found nothing beyond it.",
               f"Strategic initiatives can absorb at most about ₹{ceiling:.0f} crore ({ceiling / 10:.1f}% of ₹1,000 crore)."],
    "tasks": [("Task 1 — Explore", "FINAL_M1_T1_business_unit_view.csv", "capital, success and failed capital by business unit"),
              ("Task 2 — Predict success", "FINAL_M1_T2_success_probability.csv", "each initiative's P(Success) and at-risk flag"),
              ("Task 3 — Decide", "FINAL_M1_T3_initiative_decisions.csv", "the Board decision file: every check, decision, path, condition, priority, reason")],
    "how_to_read": ["Money: ₹ lakh in the decision file (1 crore = 100 lakh).", "Full explanation and column guide: reports/module_1_report.md §8."],
}
task_tabs = [(TAB1, T1, "Task 1: capital, success rate and failed capital by business unit"),
             (TAB2, T2, "Task 2: every initiative's out-of-fold P(Success) and at-risk flag"),
             (TAB3, T3, "Task 3: the Board decision file, one row per initiative")]

# Every column of every task tab, in one plain sentence (shown in the Read me tab)
COLUMN_GUIDE = {'Business_Unit': 'The part of NovaFin that proposed the initiative', 'Initiatives': 'How many initiatives the unit proposed', 'Capital (₹ crore)': "Total money the unit's initiatives asked for", 'Share of capital': "That unit's share of all money requested (0.25 = 25%)", 'Success rate': "Share of the unit's past initiatives that succeeded (0.80 = 80%)", 'Failed capital (₹ crore)': 'Money that went into initiatives that failed', 'Failed share of its capital': "Share of the unit's own money that went into failures", 'Share of all failed capital': "The unit's share of all money lost to failures across NovaFin", 'Median Expected_ROI (%)': "The middle promised return (return on investment) of the unit's initiatives", 'Passes hurdle': "Whether that typical promised return beats NovaFin's 6% cost of money", 'Initiative_ID': "The initiative's reference number", 'P_Success': "The model's chance (0 to 1) that the initiative succeeds, scored by a model that never saw it", 'At_Risk': 'Yes if the chance of success is below 0.767, the historical success rate', 'Model': 'Which model produced the score', 'Risk_Rating': "The bank's own risk label for the initiative: Low, Medium or High", 'Investment (₹ lakh)': 'Money the initiative asks for (1 crore = 100 lakh)', 'NPV 3 years (₹ lakh)': "Today's value of its next 3 years of cash, minus the investment; positive = it pays back within 3 years", 'P(Success)': "The model's chance (0 to 1) that it succeeds", 'Expected NPV (₹ lakh)': 'P(Success) × NPV: the value we can expect, allowing for the chance of failure', 'Check: value': 'Is its NPV positive?', 'Check: risk': 'Is its risk rating acceptable for funding now (Low only)?', 'Check: payback': 'In which year its cash pays back the investment, against the 5-year limit', 'Check: hurdle': 'Does its promised return beat the 6% cost of money?', 'Check: model': 'Does the model flag it as at risk?', 'Check: loss tolerance': 'How much could be lost on failure before its value turns negative (only for positive NPV)', 'Decision': 'Fund, Review (a person decides) or Reject', 'Decision path': 'Which route through the rule produced the decision, in words', 'Funding condition': "Fund in full, fund in stages (money released at milestones), or why it doesn't apply", 'Priority': 'Its place in the queue within its decision group', 'Full reason': 'The deciding factor first, then the other checks, in plain sentences'}

if __name__ == "__main__" or "get_ipython" in globals():
    path = build_workbook(MODULE_DIR, 1, read_me, key_numbers, board_actions, task_tabs, handoff, column_guide=COLUMN_GUIDE, receiver="Module 9",
                          m9_inputs=pd.read_csv(MODULE_DIR / "outputs" / "task3" / "module9_inputs.csv"))
    print("Saved:", path.name)
    print(handoff[["Figure", "Value", "Unit"]].to_string(index=False))

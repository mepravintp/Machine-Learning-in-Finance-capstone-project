"""
Module 9 — final output workbook
================================

WHAT THIS FILE DOES
    Builds outputs/FINAL_M9_module_output.xlsx: the one file where the Board, the presenter and the evaluator
    see the ₹1,000 crore allocation and everything behind it (decisions M9-14, M9-20). Tabs: Read me (with a
    column guide), Key numbers, Board actions, Allocation, Use now, Reserve release plan, Capital plan stages,
    Plan vs alternatives, What the ML adds, Growth path,
    Financial decision framework, Integration map, ML scorecard, Evidence (all modules), Optimiser comparison,
    Stress tests, Lending leverage, Governance, Actions, Hand-off (to the final report and Board deck),
    Decisions, Evidence index. Every figure is read from the notebook's saved tables.

HOW TO USE
    Run after the Module 9 notebook: runner cell "Final output workbook", or python helpers/m09_final_output.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

here = Path(__file__).resolve() if "__file__" in globals() else Path.cwd() / "helpers" / "m09_final_output.py"
MODULE_DIR = here.parents[1]
sys.path.insert(0, str(MODULE_DIR.parent / "scripts"))
from final_workbook import build_workbook, handoff_row, key_row, action_row   # noqa: E402

OUT = MODULE_DIR / "outputs"
K = json.loads((OUT / "key_numbers.json").read_text(encoding="utf-8"))
F = OUT / "FINAL_M9_allocation.csv"
alloc = pd.read_csv(F).set_index("Category")
TABS = [("Allocation", F, "The ₹1,000 crore by category: amount, return, bad year, evidence, liquidity, controls, owner, reason"),
        ("Use now", OUT / "capital_plan_use_now.csv", "The capital plan, part 1: what we put to work now, what it earns, its bad year, owner, first action, how we know it works"),
        ("Reserve release plan", OUT / "reserve_release_plan.csv", "The capital plan, part 2: how the ₹638 crore reserve is released: test, timing, owner, if it fails, cost of releasing early"),
        ("Capital plan stages", OUT / "capital_plan_stages.csv", "The capital plan, part 3: what each release stage changes: reserve, growth, profit, bad year, vs the bank's way"),
        ("Plan vs alternatives", OUT / "plan_vs_alternatives.csv", "Profit, growth and safety: the plan vs the bank's way, all safe, all equities"),
        ("What the ML adds", OUT / "ml_value_by_module.csv", "Each module's decision without and with the ML work, and the ₹ difference"),
        ("Growth path", OUT / "growth_path.csv", "Year 1 now; Year 2 after re-pricing releases lending (₹1 = ₹1 and bank views)"),
        ("Decision framework", OUT / "financial_decision_framework.csv", "The six-step financial decision framework, one row per module"),
        ("Integration map", OUT / "integration_map.csv", "How the modules feed each other and the allocation, with ₹ effects"),
        ("ML scorecard", OUT / "ml_scorecard.csv", "Each module's models: benchmark, unseen-data result, validation, explanation, used or not"),
        ("Evidence (all modules)", OUT / "evidence_all_modules.csv", "Every module's Module 9 inputs in the standard fields"),
        ("Optimiser comparison", OUT / "optimiser_comparison.csv", "Method B (optimiser) vs method A (chosen)"),
        ("Stress tests", OUT / "stress_tests.csv", "The allocation's year in each stress scenario, against the ₹100 crore budget"),
        ("Lending leverage", OUT / "lending_leverage_sensitivity.csv", "Lending as a leveraged bank business: return on capital by cost of funds"),
        ("Governance", OUT / "governance.csv", "Owner, watch, trigger → action and explanation for each model or control"),
        ("Actions", OUT / "actions.csv", "Phased action plan: phase, owner, timing, ₹ effect and how we know it worked")]

TOT = K["expected_crore_a_year"]; SQ = K["status_quo"]; G2 = K["growth"]["Year 2, ₹1 = ₹1 view"]; G2b = K["growth"]["Year 2, bank view (12% capital, 5% cost of funds)"]
ST = K["stress"]
CP = K["capital_plan"]; CPS = list(CP["stages"].values())
ALL8 = ST["8. All at once: 1 + 3 + 4 + 7"]
handoff = pd.DataFrame([
    handoff_row("Expected profit of the allocation", round(TOT, 1), "₹ crore a year", "Measured inputs + agreed rules", "Allocation", "Expected ₹ crore a year",
                "Sum of the column", "M9-09, M9-10", f"{TOT / 10:.1f}% a year on ₹1,000 crore vs 6.8% risk-free"),
    handoff_row("The bank's way (status quo), same ₹1,000 crore", round(SQ["profit"], 1), "₹ crore a year", "Measured", "Plan vs alternatives",
                "Profit a year (₹ crore)", "Row 'The bank's way'", "M9-16", f"Bad year {SQ['bad']:+.1f} crore vs the plan's {ALL8:+.1f}"),
    handoff_row("Equities", round(alloc.loc["Equity investments", "₹ crore"], 1), "₹ crore", "Agreed rules", "Allocation", "₹ crore", "Row Equity investments", "M9-10",
                "All 15 stocks, equal weight, with a 1-year 90% put"),
    handoff_row("Liquidity reserve (incl. lending pool)", f"{alloc.loc['Liquidity reserve', '₹ crore']:.1f} (of which {K['lending_earmark_crore']:.1f} earmarked for re-priced lending)",
                "₹ crore", "Agreed rules", "Allocation", "₹ crore", "Row Liquidity reserve", "M9-11", "Released to lending when re-priced loans earn ≥ 6.8% after expected loss"),
    handoff_row("Growth in Year 2", f"Loan book +₹{G2['lending']:.0f} crore; profit ₹{G2['profit']:.1f} crore (bank view ₹{G2b['profit']:.1f} crore)", "₹ crore",
                "Measured + Assumption (re-priced at the hurdle)", "Growth path", "Lending, Profit a year", "Year 2 rows", "M9-18", "Growth comes from scorecard re-pricing"),
    handoff_row("Reserve release plan", f"Step 1 ₹{CP['step_crore']['1 approved loans']:.0f} crore (approved loans), step 2 ₹{CP['step_crore']['2 review loans']:.0f} crore (Review loans), step 3 up to ₹{CP['step_crore']['3 future initiatives']:.0f} crore (future initiatives); floor ₹{CP['floor_crore']:.0f} crore never released",
                "₹ crore", "Agreed rules + Measured", "Reserve release plan", "₹ crore, Released when (the test)", "One row per step", "M9-21",
                f"Each step released only when its test passes; the reserve earns ₹{CP['reserve_earns_crore']:.1f} crore a year while it waits"),
    handoff_row("Growth as the reserve is released", f"Money working in NovaFin's businesses ₹{CPS[0]['working']:.0f} → ₹{CPS[2]['working']:.0f} crore (₹{CPS[3]['working']:.0f} crore with step 3); profit ₹{CPS[0]['profit']:.1f} → ₹{CPS[3]['profit']:.1f} crore",
                "₹ crore", "Measured + Assumption (re-priced at the hurdle; step 3 like today's initiatives)", "Capital plan stages", "Money working…, Profit a year, Bad year", "One row per stage", "M9-21",
                f"Bad year stays inside the ₹100 crore budget at every stage (worst {CPS[3]['bad']:.1f} crore; {CPS[3]['bad_lgd60']:.1f} crore if collateral also fetches less)"),
    handoff_row("Worst stress (all at once)", round(ALL8, 1), "₹ crore in the year", "Stress estimate", "Stress tests", "Year's result (₹ crore)", "Row 8", "M9-12",
                f"Within the ₹100 crore budget (a loss limit, 10% of ₹1,000 crore); the allocation rule, which counts no interest, left ₹{K['budget_left_crore']:.1f} crore of it"),
    handoff_row("What the ML adds (measurable)", round(K["ml_value_measurable_crore"], 1), "₹ crore a year", "Measured", "What the ML adds",
                "₹ crore a year (where measurable)", "Sum of the column", "M9-17", "Plus fraud and order-timing savings that scale with volumes"),
    handoff_row("Assumptions behind these figures", "Risk-free 6.8%; ₹1 of capital = ₹1 deployed (bank view as sensitivity); no data links the businesses (scenarios set by hand); HFT pilot planned at 0%; synthetic data in every module",
                "—", "Assumption", "—", "—", "—", "M9-07 to M9-20", "State these when presenting"),
])

key_numbers = pd.DataFrame([
    key_row("Expected profit", f"₹{TOT:.1f} crore ({TOT / 10:.2f}%)", "a year", "What the allocation is expected to earn", "Higher is better; 6.8% risk-free = ₹68 crore", "Sum of expected ₹ by category", "Allocation"),
    key_row("The bank's way (status quo)", f"₹{SQ['profit']:.1f} crore", "a year", "Every loan at today's prices + all 180 initiatives + rest in securities", "Lower than the plan", "Plan vs alternatives", "Plan vs alternatives"),
    key_row("Worst stress (all at once)", f"₹{ALL8:.1f} crore", "in the year", "Crash + initiatives' bad case + rates down + HFT costs up", "Above −₹100 crore = within budget", "Stress tests", "Stress tests"),
    key_row("Equities", f"₹{K['equities_crore']:.0f} crore + put costing ₹{K['put_cost_crore']:.1f} crore a year", "₹ crore", "30% cap; crash loss capped at ₹35 crore", "—", "Allocation", "Allocation"),
    key_row("Initiatives", f"₹{K['initiatives_crore']:.1f} crore", "₹ crore", "Units clearing 6.8% (Fund now, Review after review) and one approved Corporate Banking project (₹1.0 crore); includes ₹11.5 crore of Risk Analytics, shown under Derivatives hedging", "—", "Allocation", "Allocation"),
    key_row("Liquidity reserve", f"₹{K['reserve_crore']:.1f} crore (₹{K['lending_earmark_crore']:.0f} crore earmarked for lending)", "₹ crore", "Safe; released to lending once re-priced", "—", "Allocation", "Allocation"),
    key_row("Re-pricing needed", f"Approved loans {K['reprice_needed'][0]:.2f}%, Review loans {K['reprice_needed'][1]:.2f}% a year", "% interest", "To earn 6.8% after expected loss", "—", "Growth path", "Growth path"),
    key_row("Reserve release plan", f"₹{CP['step_crore']['1 approved loans']:.0f} + ₹{CP['step_crore']['2 review loans']:.0f} + up to ₹{CP['step_crore']['3 future initiatives']:.0f} crore released in tested steps; ₹{CP['floor_crore']:.0f} crore floor", "₹ crore",
            "How the ₹638 crore reserve goes to work", "Each step only when its test passes", "Reserve release plan", "Reserve release plan"),
    key_row("Money working in NovaFin's businesses", f"₹{CPS[0]['working']:.0f} crore now → ₹{CPS[2]['working']:.0f} crore after the lending steps", "₹ crore",
            "Growth of the core businesses", "Higher is better, if each test passes", "Capital plan stages", "Capital plan stages"),
    key_row("ML value (measurable)", f"₹{K['ml_value_measurable_crore']:.1f} crore a year", "₹", "Lending, initiatives, not following failed stock picks", "Higher is better", "What the ML adds", "What the ML adds"),
])

board_actions = pd.read_csv(OUT / "actions.csv").rename(columns={"#": "Number", "₹ effect": "Effect"})
board_actions = pd.DataFrame([action_row(r.Number, f"{r.Phase}: {r.Action}", r.Effect, f"Owner: {r.Owner}; when: {r.When}; success: {r['How we know it worked']}", "Actions")
                              for _, r in board_actions.iterrows()])

read_me = {
    "question": "The Board gives NovaFin ₹1,000 crore. Students must allocate this capital … and give explanation (Module 9); Where should NovaFin deploy its capital, what risks will it take, and how should those risks be controlled? (Section 2)",
    "answer": [f"Equities ₹{K['equities_crore']:.0f} crore (protected by a put), initiatives ₹{K['initiatives_crore']:.0f} crore (all but ₹1 crore in units that clear the 6.8% hurdle), HFT pilot ₹5 crore, hedging ₹6 crore, liquidity reserve ₹{K['reserve_crore']:.0f} crore (₹{K['lending_earmark_crore']:.0f} crore earmarked for re-priced lending).",
               f"Expected ₹{TOT:.1f} crore a year ({TOT / 10:.1f}%) vs ₹{SQ['profit']:.1f} crore the bank's way; worst stress ₹{ALL8:.1f} crore, inside the ₹100 crore budget.",
               f"Growth: once loans are re-priced with the scorecard, ₹{G2['lending']:.0f} crore moves into lending (Year 2).",
               f"The reserve is released in tested steps (tabs Use now, Reserve release plan, Capital plan stages): money working in NovaFin's businesses grows from ₹{CPS[0]['working']:.0f} crore to ₹{CPS[2]['working']:.0f} crore; only a ₹{CP['floor_crore']:.0f} crore floor stays."],
    "tasks": [("Allocation", "FINAL_M9_allocation.csv", "one row per category with amount, return, bad year, evidence, liquidity, controls, owner and reason")],
    "how_to_read": ["Money in ₹ crore; returns % a year. Inputs come from Modules 1–8's 'Module 9 inputs' tabs.", "Full explanation: reports/module_9_report.md."],
}

COLUMN_GUIDE = {
    "Category": "The business category (brief's seven + liquidity reserve)", "₹ crore": "Money allocated", "Share of ₹1,000 crore": "Share of the Board's money",
    "What the money buys": "What the ₹ is spent on", "Expected return (% a year)": "Expected yearly return on the money", "Expected ₹ crore a year": "Expected yearly profit in ₹ crore",
    "Bad-year result (₹ crore)": "The category's result in its own bad year", "Evidence strength": "How strong the evidence is", "How fast money comes back": "How quickly the money could be returned",
    "Controls": "The controls on this money", "Owner": "Who is accountable", "Why, in words": "The reason for the amount, in plain words",
    "Module": "The module (1–9) the row comes from", "What NovaFin would put money into": "What a ₹ deployed buys", "Return per ₹ deployed (% a year)": "Return per ₹ deployed",
    "Return range (% a year)": "Range of that return", "Bad-year result per ₹ (% a year)": "Result per ₹ in a bad year", "How the bad year is defined": "Which bad year is meant",
    "Capacity (₹ crore)": "How much can go in", "How fast the money can come back": "Liquidity", "Data gap or assumption": "What the data lacks and what was assumed",
    "Detail tab": "Tab in that module's workbook", "Detail column(s)": "Columns behind the figure", "Decision": "Decision ID",
    "1 Data": "Step 1: the data used", "2 ML prediction": "Step 2: the model and its verdict", "3 Financial metric in ₹": "Step 3: the money measure",
    "4 Risk": "Step 4: the risk test", "5 Decision rule": "Step 5: the rule that decides", "6 Control and owner": "Step 6: who controls it and how",
    "Way to deploy ₹1,000 crore": "The alternative compared", "Profit a year (₹ crore)": "Expected yearly profit", "Money put into NovaFin's businesses (₹ crore)": "₹ going into NovaFin's own businesses (growth)",
    "Bad year, all at once (₹ crore)": "The year's result if the main shocks hit together", "Profit (% a year)": "Profit as % of ₹1,000 crore",
    "Within the ₹100 crore bad-year budget?": "Yes if the bad year loses less than ₹100 crore", "Without the ML work": "The decision without the ML", "With it": "The decision with the ML",
    "₹ difference": "The ₹ value of the difference", "₹ crore a year (where measurable)": "The difference in ₹ crore a year against the same decision without this work, where it can be measured",
    "Stage": "The stage of the plan: Year 1 now, or after each release step", "Lending (₹ crore)": "Money in re-priced lending", "Liquidity reserve (₹ crore)": "Money in the reserve (in the Optimiser comparison, method A's row also holds the ₹5 crore pilot and the ₹5.6 crore of hedging)",
    "Profit (% a year on ₹1,000 crore)": "Profit as % of ₹1,000 crore", "Link": "From module → to module", "What passes": "The result passed on",
    "How it is used": "How the receiving decision uses it", "₹ effect": "The ₹ effect of the link", "Predicts": "What the model predicts",
    "Models compared (and benchmark)": "Models tried and the simple benchmark", "Result on unseen data": "The result on data the models never saw",
    "Verdict": "Whether a model beats its benchmark beyond luck", "Validation": "How it was validated", "Explained by": "How a decision is explained",
    "Used in the allocation?": "Whether the model is used", "Caution (λ)": "The optimiser's caution (higher = safer); or method A",
    "Initiatives (₹ crore)": "Money to initiatives", "Equities with put (₹ crore)": "Money to equities", "Lending (approved) (₹ crore)": "Money to lending",
    "Yearly swing (%)": "Assumed yearly swing of the whole allocation", "Scenario": "The stress scenario", "Year's result (₹ crore)": "The allocation's result for the year",
    "Against plan (₹ crore)": "Difference from the plan", "Within the ₹100 crore budget?": "Yes if the year loses less than ₹100 crore", "Note": "Extra explanation",
    "Cost of funds (% a year)": "What depositors are paid", "Return on capital, normal year (%)": "Return on the 12% capital in a normal year",
    "Return on capital, recession year (%)": "Return on the capital if default rates double", "Model or control": "The model or control",
    "Used for": "What it is used for", "What is watched": "What is monitored", "Trigger → action": "The trigger and the action", "How it is explained": "How its decisions are explained",
    "#": "Action number", "Action": "What to do", "When": "Timing",
    "Use": "What the money is put into now", "Why": "Why it gets money now, in plain words", "First action and when": "The first step to take and its timing",
    "How we know it is working": "The measure that shows it is on track",
    "Step": "Release step (1, 2, 3) or the floor that is never released", "Release": "What is released", "What it funds": "What the released money goes into",
    "Released when (the test)": "The measurable test that must pass before the money moves", "Checked": "How often the test is checked",
    "If the test fails": "What happens to the money if the test fails", "Cost of releasing it now at today's prices (₹ crore a year)": "Profit lost a year if it were released today, at today's prices, instead of waiting in the reserve",
    "Loan book (₹ crore)": "Money in re-priced loans", "Initiatives and pilot (₹ crore)": "Money in initiatives and the HFT pilot",
    "Money working in NovaFin's businesses (₹ crore)": "All money in NovaFin's own businesses (growth)", "Profit a year, bank view (₹ crore)": "Profit if deposits fund 88% of each loan at 5%",
    "Bad year if collateral also fetches less, LGD 60% (₹ crore)": "The same combined bad year if a defaulted loan also loses 60% instead of 40%",
    "Share of the ₹100 crore bad-year budget used": "How much of the ₹100 crore bad-year budget the combined bad year uses",
    "Profit above the bank's way (₹ crore a year)": "Profit minus what the bank's current way earns", "Bad year smaller than the bank's way by (₹ crore)": "How much less the plan loses in a bad year than the bank's way",
    "Phase": "When in the plan: Now, Month 1, Quarter 1, Quarters 1–2, Every quarter, Ongoing", "How we know it worked": "The measure that shows the action worked",
}

if __name__ == "__main__" or "get_ipython" in globals():
    path = build_workbook(MODULE_DIR, 9, read_me, key_numbers, board_actions, TABS, handoff, column_guide=COLUMN_GUIDE, receiver="the final report and Board deck")
    print("Saved:", path.name)
    print(handoff[["Figure", "Value", "Unit"]].to_string(index=False))

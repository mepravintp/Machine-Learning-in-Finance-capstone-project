# Module 9 — Solution design (as built, 22 Nov 2026)

**Final output:** `outputs/FINAL_M9_module_output.xlsx`, built by `helpers/m09_final_output.py` from `notebooks/m09_allocation.ipynb`.

Chain: Modules 1–8 'Module 9 inputs' (same fields) → hurdle 6.8% → method A (best uses first, within limits) → optimiser comparison → stress tests → plan vs alternatives → growth path → governance → actions. Decisions M9-07 to M9-20.

## The capital plan (decision M9-21, 23 Nov 2026)

The money not deployed now is never left as a total. Three tables (step 7g):
1. **Use now:** each use's ₹, expected ₹ a year, bad year, owner, first action, success measure.
2. **Reserve release plan:** step 1 approved loans re-priced (₹ = the earmark), step 2 Review loans fixed, step 3 future initiatives = reserve − steps 1–2 − floor; floor = 10% of ₹1,000 crore. Each step: the measurable test, how often, owner, if it fails, cost of releasing now = ₹ × (6.8% − today's return per ₹).
3. **Stages:** for each step released, reserve, loan book, money working in the businesses, profit (re-priced loans planned at exactly 6.8%; bank view adds 88% deposit funding × (6.8% − 5%)), combined bad year = crash + initiatives' bad case + rates 5% + HFT stop, with released money losing its 5% reserve return and earning 6.8% − expected loss in a recession (expected loss doubles); step 3 initiatives assumed like today's.

Step 9 is a phased action plan with a success measure per action.

## Reusable code

- `helpers/m09_data.py` (reads every module's inputs), `helpers/m09_style.py` (charts), `helpers/m09_final_output.py` (workbook), `notebooks/m09_allocation.ipynb` (the method). No code from the first plan is needed.

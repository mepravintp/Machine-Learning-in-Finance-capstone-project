# Module 4 — Approach

**The chain:** **churn prediction** (Task 1) → **customer lifetime value** (Task 2) → **the four groups and the 1,000 customers to contact** (Task 3).

**Business problem (brief):** NovaFin wants to reduce customer attrition. Which customers should relationship managers prioritize for retention?

**Order of work:** each task is built and its evidence reviewed before the next task's rules are fixed. Each decision is tested on this module's data before it is agreed, and every number in a decision carries its derivation (what it is, how it is worked out, why that value, what was checked).

| Task | Decisions | Status |
| --- | --- | --- |
| Task 1 | M4-07 to M4-11 (M4-02, M4-03 confirmed here) | Agreed; built |
| Task 2 | M4-12, M4-14 (M4-01 closed) | Agreed; built |
| Task 3 | M4-16 (how the churn side is formed), M4-17 (cut-offs; closes M4-04), M4-18 (the 1,000 list; no assumed success rate or cost, break-even instead; closes M4-05) | Agreed 21–22 Nov 2026 |

## Data

- `nova_customers.csv`: 5,000 customers, 13 columns, no missing values or duplicates. **89 churners (1.78%).**
- `helpers/m04_data.py`: `load_customers()`; `add_features()` builds the 5 business-based features (M4-11):

```text
Complaints_Per_Year = Complaints ÷ Relationship_Length_Years
Total_Balances      = Account_Balance + Loan_Balance + Investment_Balance
Balance_Per_Product = Total_Balances ÷ Products_Held
Loan_To_Income      = Loan_Balance ÷ Annual_Income
Savings_To_Income   = (Account_Balance + Investment_Balance) ÷ Annual_Income
```

- **First-look findings** (21 Nov): no single column separates churners (every p > 0.09); `Estimated_CLV` is an exact formula of the financial columns (R² = 1.0).

## Task 1 — Churn prediction

- **No separate test set (M4-09):** a 20% test would hold about 18 churners (1 churner = 5.6 points). Instead, 25 rounds of repeated stratified 5-fold cross-validation on all 5,000; each customer is scored by models that never saw them.
- **Each column (M4-11):** churn rate by fifth with 95% ranges, chi-square, single-column ROC-AUC. Significant only if p < 0.05 ÷ 15 = 0.0033 (Bonferroni over 15 columns: a plain 0.05 would give 15 × 0.05 = 0.75 chance "findings").
- **Models (M4-11):** logistic regression, decision tree, random forest, LightGBM on the 15 inputs; LightGBM on a broad 115-input search as a feature-engineering check. Settings fixed and light (89 churners can't support deep models; tuning inside 100 shuffles would mostly fit luck).
- **Shuffled-label test (M4-08, M4-11):** each set-up against 100 runs of itself on shuffled labels. Useful only if p < 0.05 ÷ 5 = 0.01. 100 shuffles because the smallest possible p is 1 ÷ (shuffles + 1) = 0.0099, just below the line; 50 shuffles could never pass (1 ÷ 51 = 0.0196).
- **Business check (M4-11):** churners in the top 1,000 against random picking. 20% = 1,000 ÷ 5,000 contacts. One-sided binomial test, p < 0.05.
- **No rebalancing (M4-11):** class weights, SMOTE and undersampling leave the ranking at coin-flip while inflating the average chance from 1.8% to 17–48%, which would inflate Task 3's value at risk 10–27×.
- **If nothing passes (M4-10):** conclude churn isn't predictable from this data; hand the simplest model's (logistic) out-of-fold scores to Task 3, labelled no better than chance.

## Task 2 — Customer lifetime value (built)

- **What "estimate" means here (M4-12):** estimate `Estimated_CLV` from the financial variables, to get a rule for any customer, its drivers in ₹, and what it leaves out. Our own textbook CLV (assumed margins, stay length, discount rate) dropped: nothing to check its assumptions against.
- **Models and measures (M4-14):** linear regression, lasso, decision tree, random forest, LightGBM; 25 rounds of 5-fold CV; RMSE in ₹ decides; simplest within chance of the best wins.
- **The rule:** CLV = max(0, 4% × income + 3% × account + 1.2% × loan + 1.8% × investment − ₹5,000 × complaints), found by least squares; banking meanings labelled as our interpretation.

## Hand-offs to Task 3

| From | File | What it holds | How Task 3 must treat it |
| --- | --- | --- | --- |
| Task 1 | `outputs/task1/FINAL_M4_T1_churn_scores.csv` | Each customer's out-of-fold chance of churn from logistic regression (average 1.78%; middle 80% 1.1–2.4%), labelled "Churn predictable: No: scores no better than chance" | No model or bank rule beat random (M4-10, M4-13), so differences between customers' churn chances are noise; Task 3 decides how the "High / Low Churn" axis handles this |
| Task 2 | `outputs/task2/FINAL_M4_T2_customer_value.csv` | Each customer's CLV (`Estimated_CLV`, identical to the rule found), and the ₹ from income, account, loans, investments and complaints | A reliable value for every customer; the top 1,000 hold 42% of all CLV (₹13.79 crore). It has no churn or time horizon in it |

## Task 3 — Customer prioritisation (built)

- **Groups formed only from what the bank knows in advance (M4-16):** Task 1's chance of churn and Task 2's CLV. The actual churn flag is used only afterwards, as a back-test. Every way tested of calling customers "High churn" (model top 20%, 3+ complaints, low digital usage, short relationship) churns about the same as the rest (p 0.07–0.67).
- **Cut-offs (M4-17):** High CLV = top 20% (CLV ≥ ₹92,963), from 1,000 contacts ÷ 5,000 customers; High churn = chance above the actual average 1.78% (89 ÷ 5,000).
- **The 1,000 (M4-18):** the 278 "Priority retention" then the 722 "Protect", each by CLV: the 1,000 highest-value customers, ₹13.79 crore (42% of value). Back-tested against chance × CLV, churn score only and 500 random lists: no list reaches more leavers than random, but this one reaches the most value that left (₹18.7 lakh of ₹56.0 lakh).
- **No assumed success rate or call cost (M4-18):** the data has no record of past calls. The break-even gives the share of would-be leavers a call must keep: success rate needed = cost of the call ÷ (1.78% × CLV). Whole list: ₹24.5 lakh expected loss; at ₹500 a call, calls must keep at least 20%. Recommend a randomised test to measure the real rate.
- **Hand-off:** `outputs/task3/FINAL_M4_T3_contact_list.csv`, the answer to the executive question.

## Shared code

- `helpers/m04_data.py`: load, check, `add_features()`, `MODEL_INPUTS`, `data_report()`.
- `helpers/m04_style.py`: chart style shared by all three tasks.
- Results pass between tasks as files in `outputs/taskN/` (P-15).

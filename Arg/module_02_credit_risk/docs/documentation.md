# Module 2 — Credit Risk: Corporate & Retail Lending

## 1. What the brief says (verbatim)

> **Business problem**
> NovaFin wants to increase lending while reducing defaults.
> Management asks:
> **Which loans should we approve, reject or send for manual review?**
>
> **Dataset**
> nova_loans.csv
>
> Important variables: Annual_Income · Employment_Length · Debt_to_Income · Credit_Score · Existing_Loan · Loan_Amount · Loan_Term_Months · Interest_Rate · Collateral_Value · Past_Default · Sector_Risk · Default_Flag
>
> **Task 1: Predict Probability of Default**
> Target: Default_Flag
> Build models, evaluate performance
>
> **Task 2: Estimate PD**
> For every borrower: PD = P(Default = 1 ∣ X)
> Generate: Loan_ID · Predicted_PD · Risk_Category
> Suggested categories:
>
> | PD | Category |
> | --- | --- |
> | <5% | Low |
> | 5–15% | Medium |
> | 15–30% | High |
> | >30% | Very High |
>
> These thresholds are illustrative and should be justified rather than blindly adopted.
>
> **Task 3: Expected Credit Loss**
> Assume: ECL = PD × LGD × EAD
> For example, students may assume: LGD = 40% and: EAD = Loan Amount
> Then calculate: ECLᵢ = PDᵢ × 0.40 × LoanAmountᵢ
>
> **Final decision**
> Recommend: Approve / Review / Reject based on:
> - PD
> - ECL
> - borrower characteristics
> - loan size
> - collateral
> - risk appetite

Instructor clarification 6: "Treat Customer_ID as the loan identifier for the credit-risk output. It is unique per row in nova_loans.csv, so no separate Loan_ID field is needed."

## 2. The task in plain words

NovaFin lends money. Some borrowers default (fail to repay as promised). We want to lend more but lose less.

- **Task 1 — predict default.** Train classification models (models predicting a yes/no outcome) on Default_Flag (1 = defaulted) and measure how well they separate good and bad borrowers.
- **Task 2 — PD per borrower.** PD = Probability of Default = the chance, from 0 to 1, that this borrower will not repay, given their details X. Output Customer_ID, Predicted_PD and a Risk_Category. The brief's bands are only a starting point; we must justify the cut-offs we use.
- **Task 3 — ECL.** Expected Credit Loss = the average loss the bank should expect on a loan:
  - PD = probability of default;
  - LGD = Loss Given Default = share of the loan lost if the borrower defaults (after selling collateral); brief suggests 40%;
  - EAD = Exposure at Default = amount owed when default happens; brief suggests the full Loan_Amount.
- **Final decision.** Approve, Review (send to a human credit officer) or Reject each loan, using PD, ECL, borrower details, loan size, collateral (an asset pledged that the bank can sell if the loan is not repaid) and risk appetite (how much loss the bank accepts in exchange for more lending).

Worked example: loan ₹10,00,000, PD 12%:

```text
ECL = PD × LGD × EAD = 0.12 × 0.40 × ₹10,00,000 = ₹48,000
```

## 3. Data

| Item | Value |
| --- | --- |
| File | data/nova_loans.csv |
| Rows | 5,000 loans; Customer_ID unique per row, renamed to Loan_ID at load (decision M2-01; the raw file is never edited) |
| Extra columns not in the brief's list | Customer_ID, Customer_Type (Retail 3,694; Corporate 1,306) |
| Target | Default_Flag: 19.9% = 1 |
| Units | Plain rupees (decision P-02). Total Loan_Amount = ₹640 crore (Retail ₹466 crore, Corporate ₹173 crore) |
| Rough ECL if every loan had the average PD | 0.199 × 0.40 × ₹640 crore ≈ ₹51 crore |

## 4. Required outputs (from the brief)

- [x] Task 1: several models built and evaluated (champion vs challenger; `reports/task1_report.md`)
- [x] Task 2: table Loan_ID · Predicted_PD · Risk_Category for every borrower, with justified bands
- [x] Task 3: ECL per loan (PD × 0.40 × Loan_Amount) and in total
- [x] Final decision: Approve / Review / Reject per loan, with the rule explained using PD, ECL, borrower characteristics, loan size, collateral, risk appetite

## 5. Learning objectives shown here

Clean data · EDA · Engineer financial features · Classification · Compare algorithms · Validation · SHAP · Estimate credit risk · Calculate expected credit loss · Business recommendations.

## 6. Link to other modules

Approved loan volume, expected return after ECL, and ECL rate for Retail and Corporate feed the "Retail lending" and "Corporate lending" buckets in Module 9.

## 7. Results

**Task 1 (built 19 Nov 2026).**
- A 7-input lasso scorecard on borrower fundamentals beats the bank's own pricing (interest rate as champion) in cross-validation: Brier 0.1411 vs 0.1444, ROC-AUC 0.731 vs 0.702, all 25 rounds.
- On the 1,000 test loans it points the same way (ROC-AUC 0.741 vs 0.719), but the gain is not proven at 95% (DeLong p = 0.065).
- In ₹: 37 fewer defaults and ₹2.1 crore less loss when approving the safest half of 4,000 applicants; ₹60 crore more lending at the same default rate; 95 good loans (₹8.2 crore) overcharged.
- Random forest and LightGBM overfit and were ruled out.
- Details: `reports/task1_report.md`.

**Task 2 (built 19 Nov 2026).**
- The lasso PDs pass all four calibration checks on all 5,000 and on the 1,000 test loans (predicted loss ₹63.0 vs actual ₹62.7 crore), so no Platt scaling is needed.
- The brief's four bands pass all four tests with no merges: actual default 3.2% / 9.3% / 20.5% / 42.7%; margin (interest − PD × 40%) +6.0 / +4.1 / +1.1 / −4.3% a year.
- Very High loans carry 52% of the expected loss and lose ₹8.25 crore a year. The bank's price never signals Low risk, while the scorecard finds 220 Low-risk loans (3.2% default).
- Output: `outputs/task2/loan_pd.csv`. Details: `reports/task2_report.md`.

**Task 3 (built 21 Nov 2026).**
- ECL = Predicted_PD × 40% × Loan_Amount for every loan: ₹63.04 crore a year in total, against ₹62.72 crore actually lost at 40%. Very High loans carry 52% of it.
- The rule (M2-20): PD > 30% → Reject; interest ≤ PD × 40% → Review with a required rate; largest 5% of loans (₹33.3 lakh or more) → Review; interest ≤ PD × collateral-aware LGD (50% recovery) → Review; approved book's expected loss capped at 6% (M2-06). Borrower characteristics act through the PD (no gap bigger than chance in 24 groups).
- Result: Approve 2,934 loans (₹285.9 crore) default 11.3% and earn +₹10.45 crore a year above actual loss; Review 1,045 (₹163.9 crore, 21.8%); Reject 1,021 (₹189.8 crore, 42.7%, −₹7.96 crore). Today's book: 19.9%, +₹3.07 crore. Holds on the 1,000 test loans.
- Robust: Reject never changes under cost 0–3% or LGD 30–60% / recovery 50–70%, and the approved book stays profitable in every case. Today's book breaks even at a cost of funds of only 0.48%.
- The same rule on the bank's own price (champion) earns ₹3.09 crore a year less at 14.0% default. The rule approves 58.7%, well below Task 1's 73% turning point.
- Segments (M2-22): Retail and Corporate default alike (19.9% vs 20.0%); one model is calibrated in each and beats a model per segment; the scorecard's ranking gain is mostly in Retail. Every segment earns thinly today and ₹3.15–₹3.95 per ₹100 under the rule.
- Output: `outputs/task3/FINAL_M2_T3_loan_decisions.csv`, the decision file (numbers incl. Customer_Type and loan amount, every check in words, an action for each Review loan, full reason). Details and column guide: `reports/task3_report.md`.

## 8. Risks and limitations

- Corporate and retail borrowers have similar income and loan sizes (about ₹13 lakh average loan) and identical default rates (20.0% vs 19.9%), which is unrealistic for companies: a synthetic-data limitation.
- LGD = 40% flat ignores collateral; we show a collateral-aware LGD as a sensitivity.
- No dates in the file, so no out-of-time test; random stratified split only.

## Module 9 inputs: lending return and risk per ₹ (22 Nov 2026)

| Group | Loan type | ₹ lent (crore) | Interest rate | Expected loss | **Return per ₹ lent** | What it really earned | **Bad year (PD × 2)** | Severe (PD × 2, LGD 60%) | 1-in-100 year, luck alone |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Approve | Retail | 210.5 | 8.73% | 5.44% | **3.30%** | 3.64% | **-2.14%** | -7.58% | 2.45% |
| Approve | Corporate | 75.4 | 8.81% | 5.50% | **3.31%** | 3.70% | **-2.19%** | -7.68% | 1.80% |
| Approve | All | 285.9 | 8.75% | 5.45% | **3.30%** | 3.66% | **-2.15%** | -7.61% | 2.60% |
| Review | Retail | 120.3 | 9.80% | 8.84% | **0.96%** | 0.08% | **-7.88%** | -16.73% | -0.81% |
| Review | Corporate | 43.6 | 9.63% | 8.65% | **0.97%** | 1.12% | **-7.68%** | -16.34% | -2.05% |
| Review | All | 163.9 | 9.76% | 8.79% | **0.96%** | 0.36% | **-7.83%** | -16.62% | -0.51% |

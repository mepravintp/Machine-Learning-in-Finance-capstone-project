# Module 2 — Solution design

**The chain:** Data → **PD model** (Task 1) → **PD per loan and risk bands** (Task 2) → **Expected Credit Loss and the Approve / Review / Reject decision** (Task 3).

**The business question (brief):** *"NovaFin wants to increase lending while reducing defaults. Which loans should we approve, reject or send for manual review?"*

**Overall approach: champion vs challenger** (decision M2-09).
- The bank already judges risk: the **interest rate** it charges is its risk view. That is the **champion**.
- Our models, the **challengers**, use only borrower fundamentals.
- A challenger is worth using only if it beats the champion **in ML terms and in rupees** on loans it has never seen. If none does, the report says so.

**Order of work:** Task 1 is built first, then Task 2, then Task 3. Task 3's money rules are settled with real PDs from Task 2 (see the status column below), so that cost and appetite assumptions are tested on evidence before they are fixed.

| Part | Decision | Status |
| --- | --- | --- |
| Identifier | M2-01 | Agreed |
| Layout | M2-08 | Agreed |
| Task 1 | M2-07, M2-09 to M2-13 | Agreed; built |
| Task 2 | M2-04, M2-14, M2-16 to M2-18 | Agreed; built |
| Task 3 | M2-03, M2-05, M2-06, M2-19, M2-20 | Agreed with Task 2 PDs; built |

---

## Data (all tasks)

- **Loader:** `helpers/m02_data.py` (M2-01).
  - Reads `data/nova_loans.csv` and never edits it.
  - Uses `Loan_ID` if the file has it; otherwise renames `Customer_ID` → `Loan_ID`.
  - Checks columns and uniqueness.
- **Money** is in plain rupees (P-02). Reports show ₹ lakh (1,00,000) and ₹ crore (1,00,00,000).
- **First look** (M2-10, Task 1 step 1):
  - quality and plausibility checks;
  - default rate across each input;
  - the loan book in ₹ (Retail / Corporate, default rate by count and by money, loss at 40% LGD);
  - collateral cover;
  - default rate by loan term.

  This look is for understanding only; the inputs are fixed from credit reasoning.

## Task 1 — Predict the Probability of Default

**Inputs: 15, fixed before modelling (M2-11).**
- Given (11): Annual_Income, Employment_Length, Debt_to_Income, Credit_Score, Existing_Loan, Loan_Amount, Loan_Term_Months, Collateral_Value, Past_Default, Sector_Risk, Customer_Type.
- Derived (4), in `helpers/m02_data.py`:

```text
Loan_to_Value        = Loan_Amount ÷ Collateral_Value
Loan_to_Income       = Loan_Amount ÷ Annual_Income
Total_Debt_to_Income = (Existing_Loan + Loan_Amount) ÷ Annual_Income
Principal_to_Income  = (Loan_Amount ÷ (Loan_Term_Months ÷ 12)) ÷ Annual_Income
```

- **Interest_Rate is not a challenger input.** It is:
  - circular (the bank's own risk view);
  - no gain in accuracy;
  - hides mispricing;
  - possible leakage through penalty pricing.

  It is used as the champion, and as loan income in Task 3. An EMI (monthly instalment) ratio was dropped because it needs the rate.

**Testing (M2-07).**
- **Split:** 80/20, stratified on Default_Flag × Customer_Type, seed 42. That gives 4,000 training loans and 1,000 test loans.
- **Training set:** repeated stratified 5-fold cross-validation, 5 repeats = 25 rounds. It is used to tune, compare, run paired comparisons and check overfitting. Every data step is fitted inside each round.
- **Test set:** used once at the end, with bootstrap 95% ranges (1,000 resamples) and the DeLong test for ROC-AUC.

**No rebalancing (M2-12).** Class weights leave ranking unchanged but distort PDs (average PD 20% → 45%) and would double the implied expected loss.

**Models (M2-13).**

| Role | Model |
| --- | --- |
| Champion | Interest_Rate alone (one-input logistic regression → PD) |
| Reference | Credit_Score alone |
| Challengers | Lasso logistic, logistic regression, decision tree (depth tuned), random forest, LightGBM (tree size tuned) |

**Measures.**
- **ML:** Brier score (primary), ROC-AUC and Gini, KS, log loss, average PD against the actual rate, calibration slope, and precision / recall / F1 at 30% PD. Accuracy is not used.
- **Finance (₹, out-of-fold):**
  - defaults and loss at 40% LGD when approving the safest 50–90%;
  - extra ₹ lendable at the champion's default rate;
  - mispriced loans.

**Selection rule, fixed before results (M2-13):**
1. Rule out models whose training-vs-CV ROC-AUC gap is above 0.05 (M2-15: justified from the round-to-round spread; any limit 0.05–0.10 gives the same result).
2. Best mean Brier.
3. The simplest model wins when the paired 95% range against the best includes 0.
4. The ₹ check, reported as a finding (M2-15): losses compared with the champion at every approval level from 30% to 100%. The turning point (about 73%) is carried to Task 3.
5. Test set used once.

**Explaining the model:**
- weights and odds ratios (logistic-type models);
- SHAP on the test loans;
- three example loans with expected loss in ₹.

**Hand-off to Task 2:**
- `outputs/task1/FINAL_M2_T1_default_predictions.csv`: per Loan_ID, the set, the outcome, and the champion and challenger PDs (out-of-fold for training loans, test PD for test loans);
- `chosen_model.joblib` and `chosen_model.json`.

## Task 2 — PD per loan and risk bands

**Calibration (M2-14):**
- Checks: average PD against the actual rate, a 10-group calibration chart, calibration slope, and predicted against actual ₹ loss per group.
- If the checks fail, **Platt scaling**: a one-input logistic regression on the model's log-odds, fitted inside each training round, shown before and after. Isotonic regression is shown only as a comparison.

**Bands (M2-04).** The brief's cut-offs are kept (Low < 5%, Medium 5–15%, High 15–30%, Very High > 30%) provided four tests pass:
1. each band's actual default rate falls inside its range;
2. rates rise clearly from band to band (chi-square test, plus a 95% range per band);
3. each band has enough loans;
4. the economics line up:

```text
Expected loss per ₹ a year = PD × 40%  →  2% at PD 5%, 6% at 15%, 12% at 30%
Above 30%, the expected loss alone uses up the interest even the riskiest loans pay
```

A cut-off changes only if a test fails, with the reason recorded.

**Which PD (M2-16):** Task 1's honest PDs (out-of-fold for training loans, test PD for test loans); the champion's PD carried forward.

**Pass lines agreed before building:** calibration (M2-17): intercept range includes 0, slope range includes 1, Hosmer–Lemeshow p > 0.05, ₹ predicted − actual loss range includes 0, on all 5,000 and on the test loans. Bands (M2-18): the four tests decide on all 5,000; the test loans are a consistency check; a failing band is merged with its neighbour.

**Also shown:** the bands in ₹ (interest, expected loss, margin per band) and a cross-table of the scorecard's band against the band from the bank's own price.

**Output:** `outputs/task2/loan_pd.csv` (Loan_ID, Predicted_PD, Risk_Category) for every loan; `FINAL_M2_T2_risk_categories.csv` for Task 3.

## Task 3 — Expected Credit Loss and the decision

```text
ECL = PD × LGD × EAD      base: PD = Predicted_PD (Task 2), LGD = 40%, EAD = Loan_Amount (M2-03); one-year view
```

**Agreed (all decisions settled after Task 2, each tested on the data first):**
- **LGD (M2-03):** the data has no recovery amounts, so LGD cannot be measured. The flat 40% is the brief's assumption and the Basel III supervisory value for senior unsecured loans. Sensitivity: collateral-aware LGD at 50/60/70% recovery, and flat 30/50/60%.
- **Decision test and cost (M2-05):** interest > ECL on a one-year view (from the assignment guide). Cost of lending 1/2/3% shown as a sensitivity.
- **Risk appetite (M2-06):** approved book's expected loss rate ≤ 6% (= median interest 9.1% − 3%, the top of the cost range); if exceeded, highest PD to Review. Trade-off table at today / no cap / 6 / 5 / 4 / 3%.
- **Which PD (M2-19):** Predicted_PD for every decision; the champion runs the same rule as a comparison; the 73% turning point reported.
- **The rule (M2-20), in order:**
  1. PD > 30% → Reject.
  2. Interest rate ≤ PD × 40% → Review, with a required rate.
  3. Loan in the largest 5% (₹33.3 lakh or more) → Review; interest ≤ PD × collateral-aware LGD (50% recovery) → Review. Borrower characteristics act through the PD (evidence shown).
  4. Portfolio cap 6%.
  Otherwise Approve. Each loan carries its reasons and required rate.

**Also shown:** decisions in ₹ against today's book; test-loan consistency; the evidence for each flag; concentration (Customer_Type, Sector_Risk), reported not capped; example loans.

**Output:** `outputs/task3/FINAL_M2_T3_loan_decisions.csv`, the decision file (M2-21): numbers for every loan (incl. Customer_Type and loan amount, for Module 9), every check in words, the decision, an action for each Review loan, and the full reason.

## Shared code

- `helpers/m02_data.py`: load and check, `add_ratios()`, `MODEL_INPUTS`, `data_report()`.
- `helpers/m02_style.py`: chart style shared by all three tasks.
- Results pass between tasks as files in `outputs/taskN/` (P-15).

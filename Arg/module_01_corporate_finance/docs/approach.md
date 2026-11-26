# Module 1 — Solution design

Chain for this module: **Data → P(Success) model → NPV and Expected NPV → risk (Risk_Rating, hurdle, break-even life) → Fund / Review / Reject.**

## Task 1 — Exploratory analysis (one item per bullet in the brief)

| Brief item | What we produce |
| --- | --- |
| Investment distribution | Histogram + box plot of Initial_Investment (₹ lakh), by Business_Unit |
| ROI distribution | Histogram of Expected_ROI (%); median by unit and by Risk_Rating |
| Risk categories | Counts of Low / Medium / High; success rate and median ROI per category |
| Business-unit performance | Table per unit: count, total investment, success rate, median ROI, median 3-year NPV |
| Relationship between growth and ROI | Scatter of Expected_ROI against each of three growth measures (Business_Growth, GDP_Growth, revenue growth Year 1 → Year 3), with Pearson and Spearman correlations (M1-09) |
| Relationship between investment and success | Success rate by investment third (M1-12) with 95% range; box plot of investment by outcome; Mann–Whitney test |

Data cleaning checks first: missing values, duplicates, negative values, unusual values, category spelling (M1-10).

Every success rate carries a 95% Wilson range, and group differences are tested (chi-square), because groups are small (M1-11). There is no model and no split in Task 1 (M1-08).

**Board view in ₹ (step 9):** capital, success rate and failed capital by risk level and by business unit. It shows where the money sits and where it was lost, so the Board sees the findings in money as well as in rates. **Step 10** sets each data finding next to its finance meaning.

Built: `notebooks/m01_task1_eda.ipynb` (all Task 1 code, one section per row above; it uses the shared `helpers/m01_data.py` and `helpers/m01_finance.py`). Outputs are in `outputs/task1/`, and the write-up with the charts is in `reports/task1_report.md`.

## Task 2 — Predict initiative success

Notebook: `notebooks/m01_task2_model.ipynb`.

- **Target:** Historical_Success: 138 successes, 42 failures, so a base rate of 77% (mildly imbalanced).
- **Inputs: 26 columns, fixed before modelling** (M1-17):
  - 10 given numbers: Initial_Investment, Revenue_Year1, Revenue_Year2, Revenue_Year3, Operating_Cost, Expected_ROI, Business_Growth, GDP_Growth, Interest_Rate, Competition_Index;
  - 7 derived numbers from `DERIVED_COLUMNS` in `helpers/m01_data.py`: CF1, CF2, CF3, NPV_3yr, Revenue_Growth_Y1_Y3, Cash_Return_Pct, ROI_Spread;
  - Business_Unit as 6 columns and Risk_Rating as 3 columns, each a 0/1 column per category (one-hot encoding).

  Left out: Initiative_ID (a label) and the target itself.
- **Models compared:** seven in total.
  - a baseline that always predicts the base rate;
  - logistic regression (ridge);
  - **lasso** logistic regression, which picks its own inputs (M1-17);
  - decision tree;
  - random forest;
  - XGBoost and LightGBM (gradient boosting).
- **Class imbalance:** no balancing. No class weights and no SMOTE, so the probabilities stay true to the 77% base rate. An initiative is flagged "at risk" when P(Success) is below the training base rate (M1-15).
- **Settings:** fixed, no tuning (M1-14). The exception is lasso's penalty, chosen by nested cross-validation (see below).
- **Validation:** repeated stratified 5-fold cross-validation: 25 rounds, identical for every model (M1-07, M1-18). See the next section.
- **Measures, all reported:**
  - accuracy, precision, recall and F1 for the failure class, at the "at risk" cut-off;
  - ROC-AUC;
  - Brier score;
  - log-loss.

  Formulas are in the Task 2 notebook, step 4.
- **Choosing the model for Task 3** (M1-16):
  1. Lowest Brier score, provided ROC-AUC is not clearly worse.
  2. It must pass the finance checks: explainable to the Board, input directions make financial sense, stable across rounds, proportionate in complexity.
  3. Prefer the simpler model when scores are within the round-to-round spread.
- **ML and finance scorecard (step 8b):** every model against the ML factors (Brier, ROC-AUC and its stability, failure recall) and the finance factors:
  - bias of the average P against the real 77%, and its effect on Expected NPV;
  - number of inputs used;
  - whether the Board can read it.

  Each verdict is written from the numbers.
- **Rupee replay (step 8c, M1-21):** replay each model's out-of-fold "at risk" flag and measure, in ₹:
  - capital sent to review;
  - failed capital caught;
  - capital lift (caught ÷ reviewed);
  - failure rate among flagged vs not flagged.

  This is evidence for the Board, not a selection rule.
- **Better than luck?** A shuffled-label check, 100 shuffles.
- **Explainability:**
  - logistic regression weights as odds ratios;
  - the inputs lasso keeps, and how often across the 25 rounds;
  - SHAP for the chosen model and the best tree model: an overall summary chart, plus a breakdown for one high-P(Success) and one low-P(Success) initiative;
  - **how lasso works on our data (step 10b-ii):** what it minimises, why the inputs are scaled, coordinate descent, the lasso path with each input's order of entry, and which penalty won in each round;
  - **ranked drivers (step 10e):** one table combining lasso, logistic regression and SHAP, with a stability label, a finance-direction check and the business reasoning for the Board.
- **Probability check:** a reliability chart for the chosen model (do initiatives given about 80% succeed about 80% of the time?). Calibrate only if it is clearly off.
- **Output:**
  - out-of-fold P(Success) for every initiative (each probability comes from a model that did not see that initiative), saved to `outputs/task2/FINAL_M1_T2_success_probability.csv` (Initiative_ID, P_Success);
  - Task 3 reads this file (P-15).

### How each model is trained and tested (decision M1-18)

Still **repeated stratified 5-fold cross-validation** (M1-07), the same for every model. What changed after the prototype is only:
- no class weights (M1-15);
- lasso added as a 7th model (M1-17).

**The 25 rounds**, identical for every model (fixed random seed 42), so all models face exactly the same train/test splits:

```text
5 repeats × 5 folds = 25 rounds
each round: train on 144 initiatives (4 folds), test on the other 36 (1 fold)
stratified: every fold keeps the 77/23 success/failure mix (about 28 successes, 8 failures)
```

**In each round, for each model:**
1. Fit the Pipeline on the 144 training rows only: preparation steps (scaling, 0/1 columns) and then the model.
2. Predict P(Success) for the 36 test rows.
3. Score those 36 predictions:
   - ROC-AUC and Brier score;
   - log-loss;
   - accuracy, precision, recall and F1 for failures, using the "at risk" cut-off = the training rows' success rate (about 0.77).

| Model | What it learns in each training round (144 rows) | Settings (fixed, M1-14) | Fits per round | Fits in total (25 rounds) |
| --- | --- | --- | --- | --- |
| Baseline ("always the base rate") | Only the success rate of the 144 training rows (about 0.77); it gives that number to every test initiative | — | 1 | 25 |
| Logistic regression (ridge / L2) | Scales the numbers and turns categories into 0/1 columns (learned on the 144 rows), then one weight per input | Penalty C = 1 (scikit-learn default) | 1 | 25 |
| Lasso logistic regression (L1) | Same preparation; then an **inner** 5-fold cross-validation on the 144 rows tries 10 penalty strengths and keeps the one with the best Brier score; refits on all 144 rows with it | 10 penalty values tried, inner 5 folds | 10 × 5 + 1 = 51 | 1,275 |
| Decision tree | Categories as 0/1 columns (no scaling needed for trees); the yes/no questions | Depth ≤ 3; at least 10 rows per leaf | 1 | 25 |
| Random forest | Same preparation; 300 trees, each on a random resample of rows | Depth ≤ 4; at least 5 rows per leaf; 300 trees | 1 (300 trees) | 25 |
| XGBoost | Same preparation; 200 small trees built one after another, each correcting the last | Depth 2; learning rate 0.05; 80% of rows and inputs per tree | 1 (200 trees) | 25 |
| LightGBM | As XGBoost (a different implementation of gradient boosting) | Depth 2, 4 leaves; learning rate 0.05; at least 10 rows per leaf; 80% of rows and inputs per tree | 1 (200 trees) | 25 |

All models are trained **unweighted** (M1-15).

**Extra runs, clearly separated from the comparison:**

| Run | Purpose | Used for the decision? |
| --- | --- | --- |
| Same 25 rounds with "balanced" class weights | Show the effect of balancing (M1-15) | No: comparison only |
| Shuffled-label check: 100 shuffles × 5 folds, for the chosen model and plain logistic regression | Is the score better than luck? | Evidence only |
| One final fit of each explained model on all 180 rows | Explanation: odds ratios, which inputs lasso keeps, SHAP charts | No: never scored. Scores always come from the 25 test rounds |

**Out-of-fold P(Success) for Task 3:**
- in each repeat, every initiative is predicted once, by the round where it was a test row;
- the 5 repeats give 5 predictions per initiative, and we average them;
- saved to `outputs/task2/FINAL_M1_T2_success_probability.csv`.

## Task 3 — Financial decision

Built: `notebooks/m01_task3_decision.ipynb` (reads `outputs/task2/FINAL_M1_T2_success_probability.csv`; writes `outputs/task3/`, main file `FINAL_M1_T3_initiative_decisions.csv`); report `reports/task3_report.md`.

- **Money measures:**
  - NPV over 3 years at the row's Interest_Rate (M1-02, M1-03);
  - Expected NPV = P(Success) × NPV (brief);
  - break-even life (M1-04);
  - hurdle (M1-05).
- **Rule (M1-06, agreed point by point):**
  - **A:** a gate rule.
  - **B:** Fund needs NPV > 0 and Low risk.
  - **C:** slow payers reach Review if break-even ≤ 5 years, they pass the hurdle and P ≥ 0.767 (not flagged at risk).
  - **D:** the cut-off is 5 years.
  - **E:** loss tolerance L* = P × NPV ÷ ((1 − P) × Investment) sets "fund in full" (L* ≥ 100%) or "in stages".
  - **F:** Fund is ordered by Expected NPV; Review group 1 by loss tolerance; Review group 2 by break-even, then P; every initiative gets a reason code.
- **The rule lives in the notebook** (`decide()`), not in a helper, because only Task 3 uses it (P-15).
- **Sensitivity:**
  - P(Success) from lasso, from 0.767 for all, and from the risk level's rate (M1-20, M1-23);
  - break-even cut-off at 4, 5 and 6 years.
- **Hand-off to Module 9:** Fund capital, Review capital (upper bound) and the full decision table.

## Reusable code

- `helpers/m01_data.py` — load and validate the dataset; `add_features()` / `load_initiatives_with_features()` add the derived columns used by Task 1 and Task 2.
- `helpers/m01_finance.py` — cash flows, NPV, Expected NPV, break-even life, hurdle check, decision rule.
- One notebook per task in `notebooks/`, holding that task's full code (decision P-10): `m01_task1_eda.ipynb` (built), `m01_task2_model.ipynb`, `m01_task3_decision.ipynb`.

# Module 1 — Corporate Finance: Strategic Capital Allocation

## 1. What the brief says (verbatim)

> **Business problem**
> NovaFin has several strategic initiatives competing for limited capital.
> Management wants to know:
> **Which initiatives should receive funding?**
>
> **Dataset**
> strategic_initiatives.csv
>
> Important variables include: Initiative_ID · Business_Unit · Initial_Investment · Revenue_Year1 · Revenue_Year2 · Revenue_Year3 · Operating_Cost · Expected_ROI · Business_Growth · GDP_Growth · Interest_Rate · Competition_Index · Risk_Rating · Historical_Success
>
> **Task 1: Exploratory analysis**
> Students should examine:
> - Investment distribution
> - ROI distribution
> - Risk categories
> - Business-unit performance
> - Relationship between growth and ROI
> - Relationship between investment and success
>
> **Task 2: Predict initiative success**
> Target: Historical_Success
> Compare models to model target variable and compare their performance detailing explainability (which characteristics make an initiative more likely to succeed).
>
> **Task 3: Financial decision**
> Students should calculate an approximate project NPV and expected NPV and final decision classifying as whether to fund (High expected value and acceptable risk), review (Potentially attractive but significant uncertainty) and reject (Low expected value or excessive risk).
> Expected NPV = P(Success) × NPV

## 2. The task in plain words

NovaFin has 180 proposed projects ("initiatives"), e.g. a new digital banking app. Money is limited, so we must say which to fund.

- **Task 1 — look at the data first.** How big are the investments? How is ROI spread (ROI = Return on Investment = yearly profit ÷ money invested, e.g. invest ₹100, earn ₹12 a year → 12%)? How many Low / Medium / High risk projects? Which business unit does best? Do faster-growing units promise higher ROI? Do bigger investments succeed more often?
- **Task 2 — predict success with ML.** Train several classification models (models that predict a yes/no outcome) on Historical_Success (1 = succeeded, 0 = failed), compare them, and explain which characteristics raise the chance of success (using SHAP, a method that shows how much each feature pushes a prediction up or down).
- **Task 3 — money decision.** Compute an approximate NPV for each project (NPV = Net Present Value = today's value of the cash the project will bring, minus the investment; money later is worth less than money now because today's money could earn interest). Multiply by the predicted success probability to get Expected NPV. Label each project Fund, Review or Reject.

Worked example (initiative 1002, ₹ lakh, discount rate = its Interest_Rate 6.63%):

```text
Cash flow each year = Revenue − Operating_Cost  →  22.5, 52.5, 60.0
NPV = −286.7 + 22.5/1.0663 + 52.5/1.0663² + 60.0/1.0663³ ≈ −170
If the model says P(Success) = 0.80:  Expected NPV = 0.80 × (−170) ≈ −136  → not fundable on 3 years of cash
Break-even life = 8 years of Year 3 cash flow (₹60 lakh a year) would be needed to pay back
```

## 3. Data

| Item | Value |
| --- | --- |
| File | data/strategic_initiatives.csv |
| Rows | 180 initiatives (one row each) |
| Target | Historical_Success: 77% = 1 |
| Business units | Payments 36, Wealth 35, Corporate Banking 35, Digital Banking 34, Risk Analytics 25, SME Lending 15 |
| Risk_Rating | Medium 72, Low 64, High 44 |
| Units | ₹ lakh (decision P-02). Total investment of all 180 = ₹283 crore |
| Time span of cash flows | 3 years only (Revenue_Year1–3); Operating_Cost is a yearly cost (decision M1-01) |

## 4. Required outputs (from the brief)

- [x] Task 1 charts/tables: investment distribution; ROI distribution; risk categories; business-unit performance; growth vs ROI; investment vs success
- [x] Task 2: several models compared on the same validation; explainability of what drives success
- [x] Task 3: NPV and Expected NPV per initiative; Fund / Review / Reject label per initiative
- [x] Module conclusion: which initiatives to fund, total capital needed, risks, how controlled (feeds Module 9)

## 5. Learning objectives shown here

Clean financial datasets · EDA · Engineer financial features · Build classification models · Compare ML algorithms · Model validation · SHAP · Evaluate investment opportunities · Business recommendations.

## 6. Link to other modules

Funded initiatives and their total investment become the "strategic initiatives / digital banking" input to Module 9's ₹1,000 crore split.

## 7. Results

**Task 1 (17 Nov 2026)**: full write-up in `reports/task1_report.md`.
- Clean data: 180 rows, nothing missing, ₹283 crore asked (28% of the ₹1,000 crore).
- Risk_Rating is the only clear success signal: Low risk 89% vs Medium 69% and High 70% (p = 0.014).
- Investment size has no link with success (77% / 78% / 75% by thirds; p = 0.90) but drives 3-year NPV (r −0.60).
- **In ₹ (step 9):** ₹65.5 crore (23%) of the capital went into initiatives that failed.
  - Medium and High risk hold 65% of the capital but 86% of the failed capital.
  - Corporate Banking holds 22% of the capital but 35% of the failed capital, and its risk rating doesn't explain it.
- Expected ROI (promised yearly profit ÷ investment) falls as risk rises (12.0% → 8.3%), so High-risk projects offer a poor trade.
- Business_Growth links strongly to Expected ROI (r 0.56); GDP_Growth and a project's own revenue growth do not.
- Unit success rates differ (63–87%) but not reliably (p = 0.36); Corporate Banking asks for the most money and has the lowest success and ROI.
- Only 8 of 180 have positive 3-year NPV (today's value of 3 years of cash minus the investment), while 135 promise ROI above their Interest_Rate.

**Task 2 (17 Nov 2026)**: full write-up in `reports/task2_report.md`.
- Seven models compared on the same 25 cross-validation rounds. **Lasso** logistic regression is best: ROC-AUC 0.578 ± 0.080 (ranking skill; 0.5 = coin toss) and Brier score 0.180 (accuracy of the probabilities; lower is better).
- That Brier score only ties "always 77%" (0.179), and a shuffled-label check gives p = 0.17. **Success is only weakly predictable from this data.**
- Tree ensembles (random forest, XGBoost, LightGBM) are at chance (0.46–0.50): 180 initiatives are too few for them.
- The "at risk" flag (P(Success) below 77%) still separates risk: 30% of flagged initiatives failed against 13.5% of the others (p = 0.015).
- **Drivers of success**, which make financial sense: Low risk (odds × 2.4, kept in every round), faster business growth, higher Expected ROI, faster revenue growth. Corporate Banking lowers it.
- **Why lasso, ML and finance** (notebook step 8b; report 5.1): best Brier among the real models, best ROC-AUC and failure recall; not over-optimistic (average P 0.748 vs real 0.767), whereas XGBoost/LightGBM (0.785/0.794) would overstate Expected NPV; about 7 inputs readable as odds ratios.
- **Rupee replay** (step 8c; report 5.2): lasso's flag would have caught 75% of the failed capital while sending 59% of the capital to review (capital lift 1.27). Random forest and boosted-tree flags point at the safer projects.
- **How lasso chose its inputs** (step 10b-ii; report 7.1): entry order Low risk → Expected_ROI → Business_Growth → revenue growth. The inner cross-validation chose C ≈ 0.36 in 24 of the 25 rounds.
- **Ranked drivers** (step 10e; report 7.5): Low risk takes a typical initiative from about 77% to 89% success. Paper NPV and cash return do not predict success; they are noise.
- Balancing the classes would have pulled average P(Success) down to 0.51–0.69 (real 0.77), which confirms the decision not to balance (M1-15).
- Lasso's out-of-fold P(Success) (0.56–0.90) is saved for Task 3 in `outputs/task2/FINAL_M1_T2_success_probability.csv`.

**Task 3 (17 Nov 2026)**: full write-up in `reports/task3_report.md`.
- Only 8 of 180 initiatives have a positive 3-year NPV.
- **Fund: 2, ₹3.2 crore.**
  - 1075 (Wealth, Low risk; Expected NPV +48.2 lakh; loss tolerance 164%) is funded in full.
  - 1062 (Corporate Banking, Low risk; +7.8 lakh; 36%) is funded in stages.
- **Review: 38, ₹62.9 crore.**
  - 6 positive-NPV Medium/High-risk projects, ordered by loss tolerance (1074 and 1115 have almost no margin).
  - 32 slow payers repaying in year 4 or 5.
  - Past success 84%, against 75% for Reject.
- **Reject: 140.** 79 break even after 5 years, 17 never, 8 fail the hurdle, 36 are flagged at risk by the model.
- **What the ML adds:** Fund is identical in all three P runs. Review would be 74 with no model and 31 with the risk rating alone, against 38 with lasso. The model's effect is essentially the bank's own rating.
- **Cut-off sensitivity:** Review is 21 at 4 years and 47 at 6 years.
- **Module 9 ceiling for strategic initiatives:** about ₹66 crore of the ₹1,000 crore.

## 8. Risks and limitations (brief: "Clearly outline Risks & Limitations")

- Only 180 rows: model results vary; we use cross-validation and report the spread.
- Cash flows stop at year 3, so NPV is a lower bound for long-lived projects; break-even life shows how much the decision depends on cash after year 3.
- Synthetic data: relationships may be simpler than real life. Signs: 11 rows sit exactly at a 2.00% Expected_ROI floor; investments are spread almost perfectly evenly.
- Small groups (SME Lending has 15 initiatives): differences between units cannot be confirmed statistically.

## Module 9 inputs by business unit (22 Nov 2026)

| Business unit (Fund + Review initiatives) | Initiatives | Capacity (₹ crore) | Expected return a year | 1-in-20 bad case | If all succeed |
| --- | --- | --- | --- | --- | --- |
| Corporate Banking | 8 | 15.8 | **6.3%** | -6.1% | 14.3% |
| Digital Banking | 7 | 9.3 | **13.2%** | -6.6% | 22.3% |
| Payments | 7 | 10.1 | **13.0%** | -2.1% | 18.8% |
| Risk Analytics | 7 | 11.5 | **10.4%** | -5.4% | 18.5% |
| SME Lending | 2 | 4.2 | **13.3%** | -1.4% | 25.9% |
| Wealth | 9 | 15.3 | **17.6%** | 3.6% | 27.7% |
| All units | 40 | 66.2 | **12.1%** | 5.9% | 20.8% |

Return = IRR over 5 years (years 4–5 = year 3), cash × P(Success), a failure returns no cash; bad case = 1-in-20 of 2,000 draws (seed 42).

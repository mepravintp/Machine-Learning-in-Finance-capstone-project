# Module 4 — Customer Analytics: Churn & Customer Lifetime Value

## 1. What the brief says (verbatim)

> **Business problem**
> NovaFin wants to reduce customer attrition.
> Management asks:
> **Which customers should relationship managers prioritize for retention?**
>
> **Dataset:** nova_customers.csv
>
> **Task 1 — Churn prediction**
> Target: Churn_Flag
> Build a classification model to predict churn
>
> **Task 2 — Customer Lifetime Value**
> Estimate: CLV using the provided customer financial variables.
>
> **Task 3 — Customer prioritization**
> Create four groups:
>
> | | Low Churn | High Churn |
> | --- | --- | --- |
> | High CLV | Protect | Priority retention |
> | Low CLV | Maintain | Low-cost intervention |
>
> **Executive question**
> If NovaFin can contact only 1,000 customers, which customers should it target?

Note: unlike other modules, the brief gives no variable list here.

## 2. The task in plain words

Attrition (also called churn) = customers closing their accounts and leaving the bank. A relationship manager (the staff member who looks after a customer) can call only so many people, so we must rank who to call.

- **Task 1 — churn model.** A classification model (predicts yes/no) giving each customer a probability of leaving.
- **Task 2 — CLV.** Customer Lifetime Value = total profit the bank expects from a customer over the whole relationship. The brief says estimate it "using the provided customer financial variables": we build a regression model (a model that predicts a number) from balances, income, products and tenure.
- **Task 3 — four groups.** Combine churn risk and value:
  - High CLV + Low churn → **Protect** (valuable and staying: keep them happy)
  - High CLV + High churn → **Priority retention** (valuable and at risk: call first)
  - Low CLV + Low churn → **Maintain** (business as usual)
  - Low CLV + High churn → **Low-cost intervention** (e.g. an automated email or app offer)
- **Executive question.** Only 1,000 calls are possible: pick the 1,000 customers where a call saves the most value.

```text
Value at risk for customer i = P(churn)ᵢ × CLVᵢ
Example: A has 30% churn chance and CLV ₹80,000 → ₹24,000 at risk
         B has 70% churn chance and CLV ₹10,000 → ₹7,000 at risk     → call A first
```

## 3. Data

| Item | Value |
| --- | --- |
| File | data/nova_customers.csv |
| Rows | 5,000 customers |
| Columns | Customer_ID, Age, Annual_Income, Account_Balance, Products_Held, Transactions_Per_Month, Digital_Usage, Complaints, Loan_Balance, Investment_Balance, Relationship_Length_Years, Churn_Flag, Estimated_CLV |
| Target (Task 1) | Churn_Flag: 1.8% = 1 (89 churners) → very imbalanced |
| Target (Task 2) | Estimated_CLV (₹): mean ₹65,600 |
| Units | Plain rupees (P-02) |

Imbalance note: with 89 churners, the 1,000-customer list is 20% of all customers but must capture as many of the few churners (and as much value) as possible.

## 4. Required outputs (from the brief)

- [x] Task 1: churn classification models with evaluation (and the finding that churn isn't predictable from this data)
- [x] Task 2: CLV estimated from customer financial variables (rule found, models compared)
- [x] Task 3: every customer placed in one of the four groups, with group sizes and value (`outputs/task3/customer_groups.csv`)
- [x] Executive answer: the list of 1,000 customers to contact and why (`outputs/task3/FINAL_M4_T3_contact_list.csv`)

## 5. Learning objectives shown here

Classification · Regression (CLV) · Compare algorithms · Evaluate imbalanced classification · Validation · SHAP · Avoid leakage · Estimate customer lifetime value · Business recommendations.

## 6. Link to other modules

**Hand-off to Module 9, "Wealth management" (M4-19):** rates per ₹ of investment balance, since our file is a sample and Module 9 works in ₹ crore:
- fee yield 1.80% (our banking reading of Task 2's CLV weight); churn loss 1.61% of balances; **net 1.77%**;
- retention: Task 3's break-even (least success calls need) and the 100% ceiling (the most it can be worth: about ₹20 lakh, 1.4–1.6% of the 1,000 list's value); no assumed success rate;
- governance: churn isn't predictable from this data, so no model-driven retention programme should be funded until better data exists; run a randomised test first.

## 7. Results

**Task 1 (built 21 Nov 2026).**
- **Churn cannot be predicted from this data.** 0 of 15 columns separate churners (Bonferroni line 0.0033; lowest p 0.086). 0 of 5 model set-ups beat 100 runs on shuffled labels (line 0.01; p 0.20–0.84). Each model's top 1,000 holds 15–22 of the 89 churners, against 17.8 by random picking. 0 of 10 drivers are significant.
- A 115-input feature-engineering search scores ROC-AUC 0.561 over 25 rounds (0.534 on the luck-test split, where shuffled labels reach 0.562 one time in 20). Rebalancing leaves the ranking at coin-flip and inflates every chance 9–27×.
- ₹55.96 lakh of lifetime value (1.7% of ₹32.80 crore) left with the churners, who are worth about the same as stayers.
- To Task 3: logistic regression's out-of-fold chances, labelled no better than chance. Details: `reports/task1_report.md`.

**Task 2 (built 21 Nov 2026).**
- Linear regression estimates CLV with a typical error of ₹36 (average CLV ₹65,602); trees do far worse (₹6,739–₹12,057). The rule, found by least squares: CLV = max(0, 4% × income + 3% × account + 1.2% × loan + 1.8% × investment − ₹5,000 × complaints), matching all 5,000 customers within ₹0.01 (one paisa). Age, products, transactions, digital usage and relationship length don't count.
- ₹32.80 crore of value: 65% from income, 35% from balances; complaints destroy ₹3.81 crore (12%). The top 1,000 customers hold 42% of the value (₹13.79 crore). CLV has no churn or time horizon in it.
- Details: `reports/task2_report.md`.

**Hand-offs to Task 3.** From Task 1, `FINAL_M4_T1_churn_scores.csv`: each customer's chance of churn (logistic regression, out-of-fold), labelled no better than chance. From Task 2, `FINAL_M4_T2_customer_value.csv`: each customer's CLV and its sources. See `docs/approach.md` for how Task 3 must treat each.

**Task 3 — Customer prioritisation (built).**
- Four groups from Task 1's chance of churn (High = above the actual 1.78%) and Task 2's CLV (High = top 20%, ≥ ₹92,963): Priority retention 278 customers (₹3.88 crore), Protect 722 (₹9.90 crore), Low-cost intervention 1,854 (₹7.76 crore), Maintain 2,146 (₹11.25 crore).
- Actual churn is about the same in every group (1.1–2.0%, p = 0.67): they differ in value, not risk.
- **Executive answer:** contact the 1,000 highest-value customers, Priority retention first then Protect, each by CLV: ₹13.79 crore, 42% of all value. Back-tested, it reaches the most value that left (₹18.7 lakh of ₹56.0 lakh; random ₹11.2 lakh), though no more leavers than random.
- No success rate or call cost assumed: at ₹500 a call, the 1,000 calls (₹5 lakh) pay off if they keep at least 20% of would-be leavers (expected loss ₹24.5 lakh). A randomised test should measure the real rate. Details: `reports/task3_report.md`.

## 8. Risks and limitations

- Only 89 churners: a weak real churn effect could hide below what the data can detect; 'not predictable' means 'not detectable here'.
- Estimated_CLV is an exact formula of income, balances and complaints (R² = 1.0); how it was set is not documented (Task 2).
- Contacting a customer does not guarantee they stay; the success rate and call cost are unknown, so Task 3 reports a break-even instead of assuming them (M4-18).

## Module 9 inputs (22 Nov 2026)

| Category | Return per ₹ (% a year) | Range | Bad year per ₹ | Bad year means | Capacity | Gap / assumption |
| --- | --- | --- | --- | --- | --- | --- |
| Wealth management: fees on client balances | 1.77 | 1.39 (bad year) to 1.80 (no churn), per ₹ of client balances | 1.39 | Market fall of 20% (balances and fees fall with it) and churn twice as high | 328.1 | Per ₹ of client balances, not of NovaFin's capital; return per ₹ of capital comes from Module 1's Wealth unit (17.6% a year) |

# Module 3 — Fraud Detection

## 1. What the brief says (verbatim)

> **Business problem**
> NovaFin processes thousands of transactions every day.
> Management wants to identify suspicious transactions while minimizing unnecessary investigation.
>
> **Dataset:** nova_transactions.csv
>
> Variables include: Amount · Transaction_Type · Merchant_Category · Location · Device_ID · Account_Age_Months · Historical_Avg_Transaction · Transaction_Frequency · Fraud_Flag
>
> **Task 1 — Exploratory analysis**
> Investigate:
> - Fraud rate
> - Fraud by transaction type
> - Fraud by amount
> - Fraud by location
> - Fraud by customer behaviour
>
> **Task 2 — Supervised fraud model**
> Target: Fraud_Flag
> Build model and compare performance
>
> **Task 3 — Unsupervised detection**
> Use: Isolation Forest
> The objective is to identify transactions that appear unusual even without relying directly on the fraud label.
> Compare: Supervised detection vs anomaly detection.
>
> **Task 4 — Cost-based threshold**
> Assume:
>
> | Missed fraud cost | ₹10,000 |
> | --- | --- |
> | False-positive investigation cost | ₹500 |
>
> Then Find a threshold that minimizes expected operational cost.

## 2. The task in plain words

Fraud = someone using an account dishonestly (e.g. a stolen card). Two goals pull against each other: catch fraud, but do not waste investigators' time on honest transactions.

- **Task 1 — explore.** Overall fraud rate; fraud % by type (Payment / Transfer / Withdrawal), by amount size, by city, and by customer behaviour (spending far above the customer's usual average, account age, how often they transact). Every other column in the file is tested the same way, so 'this doesn't matter' rests on evidence.
- **Task 2 — supervised model.** "Supervised" = the model learns from past transactions whose answer (fraud or not) is known. Build several and compare.
- **Task 3 — Isolation Forest.** "Unsupervised" = finds unusual transactions without using the fraud label. Isolation Forest builds random trees that keep splitting the data; unusual points get isolated in very few splits and receive a high anomaly score. Then compare how well each approach finds the real frauds.
- **Task 4 — cost-based threshold.** A model gives each transaction a score; above a threshold (cut-off) we investigate it. Missing a fraud (false negative) costs ₹10,000; investigating an honest transaction (false positive) costs ₹500. Pick the threshold with the lowest total cost.

```text
Total cost(threshold) = ₹10,000 × (frauds missed) + ₹500 × (honest transactions investigated)
```

Worked example: at a threshold where we miss 20 frauds and flag 500 honest ones, cost = 20 × 10,000 + 500 × 500 = ₹4,50,000.

## 3. Data

| Item | Value |
| --- | --- |
| File | data/nova_transactions.csv |
| Rows | 30,000 transactions, 1 Jan 2025 – 31 Aug 2026, 7 cities |
| Extra columns not in the brief's list | Transaction_ID, Customer_ID, Timestamp |
| Target | Fraud_Flag: 2.28% = 1 (684 frauds) → strongly imbalanced (rare class) |
| Volume | About 49 transactions a day: a sample of the 'thousands every day' in the brief |
| Amounts | Plain rupees (P-02). Mean amount ₹10,761; median fraud amount ₹26,438; total fraud ≈ ₹2 crore |
| Transaction types | Payment, Transfer, Withdrawal |

Imbalance warning: a model that says "never fraud" is 97.7% accurate and useless, so accuracy is not used.

## 4. Required outputs (from the brief)

- [x] Task 1: fraud rate; fraud by type, amount, location, customer behaviour (plus every other column, on the same evidence rule)
- [x] Task 2: supervised models built and compared (11 set-ups, benchmark, selection rule, final test, finance case)
- [x] Task 3: Isolation Forest scores; unusual transactions with reasons; comparison supervised vs anomaly detection
- [x] Task 4: threshold that minimises expected operational cost, with the cost curve

## 5. Learning objectives shown here

EDA · Engineer financial features · Classification · Compare algorithms · Evaluate imbalanced classification · Validation · SHAP · Avoid leakage (time order) · Detect fraud · Business recommendations.

## 6. Link to other modules

Expected fraud loss rate and investigation cost per transaction feed the "Digital banking" bucket risk in Module 9. Built: with the 4.76% rule, fraud lost 1.24% and investigation 0.31% of money moved (total 1.55%), against 6.13% with no screening (`reports/module_3_report.md` §9; used in Module 9, M9-08).

## 7. Results

**Task 1 (built 21 Nov 2026).**
- 684 frauds in 30,000 transactions (2.28%), worth ₹2.01 crore: 6.2% of the money, because frauds are 3–4 times larger than normal transactions. Stable over time (months don't differ, p = 0.65).
- Evidence rule (M3-10) over 16 tests: **Strong** — Amount (fraud 0.6% → 12.7% across tenths, ROC-AUC 0.788) and Amount ÷ usual amount (0.787). **Weak** — usual transaction size (0.583) and transaction type (Transfer 3.0% vs 2.1–2.2%). **Not informative** — city, merchant category, account age, frequency, hour, weekday, device and location change, device and customer history.
- Transactions of ₹25,000 and over: 9% of transactions, 55% of frauds, 84% of the ₹ lost. A third of frauds look like ordinary transactions and carry about 8% of the ₹.
- Details: `reports/task1_report.md`.

**Task 2 (built 21 Nov 2026).**
- Chosen by a rule agreed before results: LightGBM (100 trees of 4 leaves) on amount, amount ratio, usual amount and transaction type. CV PR-AUC 0.132 vs 0.116 for amount alone (+0.016, range +0.010 to +0.022). Random forest ruled out for overfitting; the extra 8 columns add nothing.
- Final test (6,000 later transactions): ROC-AUC 0.815 vs 0.787 (gain proven), Brier better (proven), PR-AUC +0.021 (range just touches 0). No leakage. 88% of the model's reliance is on amount and the amount ratio.
- Finance: the model finds more frauds but fewer fraud ₹ than amount alone at tight budgets (top 1%: −5.6 points of ₹). Ranking by P(fraud) × amount is best at 5%: 37% of frauds, 68% of fraud ₹, ₹4.53 lakh per 1,000 transactions.
- Details: `reports/task2_report.md`.

**Task 3 (built 21 Nov 2026).**
- Isolation Forest (500 trees, fitted without the fraud label on six numeric descriptors) flags 680 transactions (2.25%) as unusual: 13.8% of them fraud, against 2.0% for the rest. Each comes with its reasons (SHAP) in `outputs/task3/unusual_transactions.csv`.
- On 6,000 test transactions it ranks worse than both the supervised model and amount alone, beyond chance: PR-AUC 0.075 vs 0.124 vs 0.103; fraud ₹ caught at a 10% budget 60% vs 82% vs 85%.
- It adds only 3–6 frauds the supervised model misses; combining the two doesn't help; neither finds the ordinary-looking frauds. 9% of its flags are big spenders' ordinary payments (none fraud): "unusual" isn't "fraud".
- Details: `reports/task3_report.md`.

**Task 4 (built 21 Nov 2026).**
- The answer: investigate a transaction when the model's chance of fraud is above 4.76% (= ₹500 ÷ ₹10,500, from the brief's costs). Trying every cut-off on training finds the same cost; the model's chances are honest on both sides of the line (training and test).
- On 6,000 test transactions: 79 checks per 1,000, half the frauds and 80% of the fraud ₹ caught; cost ₹1.48 lakh vs ₹2.40 lakh investigating nothing (−38%, range ₹62,819–₹1,21,835 saved per 1,000). A threshold on the anomaly score saves only 13%.
- Counting frauds at their real amount: investigating nothing really costs ₹6.66 lakh per 1,000; the rule saves ₹4.98 lakh (75%). Ranking by P × amount saves ₹26,000 more but doubles the checks (157 per 1,000).
- Details: `reports/task4_report.md`.

## 8. Risks and limitations

- Only 684 frauds: results on a 20% test set rest on about 140 cases; we report confidence ranges.
- Device_ID behaves like a random label and the 'customer' columns change on every transaction (Task 1), so customer history can't be used here; real data would allow it.
- Fraud patterns change over time (concept drift); the model needs monitoring and retraining.
- The ₹10,000 / ₹500 costs are the brief's assumptions; we show how the best threshold moves if they change.

## Module 9 inputs (22 Nov 2026)

| Category | Return per ₹ (% a year) | Range | Bad year per ₹ | Bad year means | Capacity | Gap / assumption |
| --- | --- | --- | --- | --- | --- | --- |
| Digital banking: cost of fraud risk | -1.55 | −1.55% with the rule vs −6.13% with no screening (per ₹ of money moved) | -4.03 | Fraud three times as common (missed fraud × 3); no screening: −18.38% | Scales with the money moved | No fee revenue in the data: Digital banking's return per ₹ of capital comes from Module 1 (Digital Banking 13.2%, Payments 13.0%) |

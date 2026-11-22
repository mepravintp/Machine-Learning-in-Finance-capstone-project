# Notebook explanations (study copies)

Each file here is a copy of the matching notebook in `../notebooks/`. Every original cell is unchanged and keeps
its saved output. Above each cell is a blue-quoted **📘 Explanation — cell N** block (N is the cell number in the
original notebook) that covers:

- **What it does**: what the cell does, in plain English
- **Why this method**: why this approach was chosen over the alternatives
- **Input → Output**: what goes in and what comes out (with the actual numbers)
- **How to read the output**: what the result means and how it compares with the other models, baselines or rules

The first cell of each notebook tells the story of the whole module in one paragraph and lists the key numbers.

| Notebook | Module | One-line takeaway |
|---|---|---|
| 00_setup_and_data_audit | Setup | No missing data. Rare classes, so use PR-AUC and cost thresholds. Time splits where the data are time series. Leakage list |
| 01_strategic_initiatives | M1 | 3-driver logistic (AUC 0.63) wins. Risk-adjusted E[NPV] and PI give Fund 21 / Review 18 / Reject 141. 8 projects fit ₹1,000 cr |
| 02_credit_risk | M2 | Logistic PD (test AUC 0.75, calibrated). ECL = PD×LGD×EAD. Approve PD < 0.11 (ECL 2.8%) |
| 03_fraud | M3 | Random forest (PR-AUC 0.142, 6× random). Threshold set on the cost curve gives a 38% cost saving. Isolation Forest is weaker |
| 04_churn_clv | M4 | Churn not predictable (AUC ≈ 0.5). Lifetime CLV. EVaR list of 1,000 customers gives ROI 152% |
| 05_equity_returns | M5 | Walk-forward. Ridge IC 0.056 (t 1.2, not significant). Equal-weight has the best Sharpe |
| 06_portfolio | M6 | Markowitz fails. ML tilt is not significant. Equal-weight chosen. Crisis VaR is about 30% |
| 07_hft | M7 | Order-book imbalance signal. Macro-F1 0.44, about the same as a simple OBI rule. Profit disappears under stress, so use it for execution |
| 08_options | M8 | No ML model beats Black-Scholes. The delta hedge cuts VaR by 80%. Vega risk remains |
| 09_liquidity_stress | Extra | LCR-style historical simulation gives a ₹175 cr reserve |
| 10_allocation | M9 | Ranked by risk-adjusted return within limits: 16.5% return, stress loss 11.6% |

The notebooks run from this folder as they are (`../src` resolves the same way). There is no need to re-run them,
because the outputs are already saved.

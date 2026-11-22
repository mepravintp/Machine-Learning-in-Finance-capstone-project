# NovaFin capstone: central guide

Every module answers the same five questions: **What is it? · Where is the code? · How does the code work? ·
Where are the stats and report outputs? · What is the conclusion?** Each module also has a **model comparison table**
showing what each choice gained over the alternatives.

Module numbers follow the corrected brief (`docs/NovaFin_Group_Capstone_Project_CORRECTED.docx`). Status and resume
instructions are in [PROGRESS.md](PROGRESS.md). The final deliverables are in [deliverables/](deliverables/).

## Index

| # | Module | Notebook | Results | Figures |
|---|---|---|---|---|
| 0 | [Setup and data audit](#m0-setup-and-data-audit) | [00](notebooks/00_setup_and_data_audit.ipynb) | – | – |
| 1 | [Strategic initiatives (corporate finance)](#m1-strategic-initiatives) | [01](notebooks/01_strategic_initiatives.ipynb) | [results](results/Module_01_Strategic_Initiatives/) | [figures](figures/Module_01_Strategic_Initiatives/) |
| 2 | [Credit risk](#m2-credit-risk) | [02](notebooks/02_credit_risk.ipynb) | [results](results/Module_02_Credit_Risk/) | [figures](figures/Module_02_Credit_Risk/) |
| 3 | [Fraud detection](#m3-fraud-detection) | [03](notebooks/03_fraud.ipynb) | [results](results/Module_03_Fraud_Detection/) | [figures](figures/Module_03_Fraud_Detection/) |
| 4 | [Churn and CLV](#m4-churn-and-clv) | [04](notebooks/04_churn_clv.ipynb) | [results](results/Module_04_Churn_CLV/) | [figures](figures/Module_04_Churn_CLV/) |
| 5 | [Equity returns](#m5-equity-returns) | [05](notebooks/05_equity_returns.ipynb) | [results](results/Module_05_Equity_Returns/) | [figures](figures/Module_05_Equity_Returns/) |
| 6 | [Portfolio optimisation](#m6-portfolio-optimisation) | [06](notebooks/06_portfolio.ipynb) | [results](results/Module_06_Portfolio_Optimisation/) | [figures](figures/Module_06_Portfolio_Optimisation/) |
| 7 | [High-frequency trading](#m7-high-frequency-trading) | [07](notebooks/07_hft.ipynb) | [results](results/Module_07_HFT/) | [figures](figures/Module_07_HFT/) |
| 8 | [Derivatives](#m8-derivatives) | [08](notebooks/08_options.ipynb) | [results](results/Module_08_Derivatives/) | [figures](figures/Module_08_Derivatives/) |
| + | [Liquidity reserve (extra)](#extra-liquidity-reserve) | [09](notebooks/09_liquidity_stress.ipynb) | [results](results/Extra_Liquidity_Reserve/) | [figures](figures/Extra_Liquidity_Reserve/) |
| 9 | [Integrated capital allocation](#m9-integrated-capital-allocation) | [10](notebooks/10_allocation.ipynb) | [results](results/Module_09_Integrated_Allocation/) | [figures](figures/Module_09_Integrated_Allocation/) |
| ★ | [Final conclusion for the Board](#final-conclusion-for-the-board) | | | |
| ✓ | [Course alignment of methods](#course-alignment-of-methods) | | | |

**The common thread.** Every module follows the chain the Board asked for:
Data → ML prediction → Financial metric → Risk assessment → Business decision.
Each notebook saves its outputs in `results/<module folder>/` and `figures/<module folder>/`. Notebook 10 reads every
result file, so no number in the allocation is typed in by hand.

**Shared code.** [src/novafin.py](src/novafin.py) holds:
- the assumptions (LGD 40%, discount rate 12%, risk-free 7%, cost of funds 6%, ECL appetite 3%, fraud costs ₹10,000 and
  ₹500, ₹1,000 cr budget, 1,000 retention contacts, seed 42)
- data loaders and `use_module()` (sends outputs to the module's folders)
- metrics: ROC-AUC, Gini, KS, PR-AUC and the calibration gap
- `compare_models()`, which builds the "what did we gain by choosing this model" tables
- the SHAP helper and `save_result()` / `load_result()`

---

## M0. Setup and data audit
- **What.** The shared assumptions, a quality check of all eight files, the units decision, which validation split
  each file needs, and a leakage watch-list.
- **Code.** [notebooks/00_setup_and_data_audit.ipynb](notebooks/00_setup_and_data_audit.ipynb) and [src/novafin.py](src/novafin.py).
- **Conclusion.**
  - No missing values or duplicates anywhere.
  - Fraud (2.3%) and churn (1.8%) are rare, so accuracy is useless there.
  - Loans and customers are in rupees; initiatives are assumed ₹ crore; liquidity is ₹ lakh, as the README says.
  - Splits: market, transactions and liquidity are split by time; HFT by trading day; the rest are stratified.

---

## M1. Strategic initiatives
- **What.** Predict each of 180 initiatives' probability of success, convert it into a risk-adjusted expected NPV,
  and classify each one as **Fund / Review / Reject**.
- **Code.** [notebooks/01_strategic_initiatives.ipynb](notebooks/01_strategic_initiatives.ipynb)
- **How it works.**
  1. **EDA.** Six views (investment, ROI by outcome, risk rating, business unit, growth vs ROI, investment quartiles),
     with the t-statistic of each mean difference.
  2. **Features.** Revenue growth, year-1 margin and payback ratio are added; the ID is dropped.
  3. **Validation.** 5-fold stratified CV repeated 10 times (50 fits per model), because there are only 180 rows.
  4. **Models.** Four, simplest first; the simplest wins unless beaten by more than 0.005 AUC.
  5. **Scoring.** Out-of-fold P(success) for every initiative, then a calibration check and SHAP.
  6. **NPV.** Cash flow = revenue − operating cost, discounted at 12%, over a 5-year life (years 4–5 repeat year 3).
     - Risk-adjusted E[NPV] = P × NPV − (1−P) × loss-on-failure × investment.
     - PI = E[NPV] ÷ investment.
  7. **Decision rule.**
     - Fund if PI ≥ 0.10, P ≥ 0.75 and the risk rating is not High.
     - Reject if E[NPV] ≤ 0 or P < 0.60.
     - Review otherwise.
  8. **Sensitivity.** Project life, discount rate, loss on failure, and a model stress where P drops by 10 points.

**Model comparison (CV ROC-AUC, 50 folds)**

| Rank | Model | CV ROC-AUC | Gain vs no-skill | Gap to best | Chosen |
|---|---|---|---|---|---|
| 1 | Logistic, 3 drivers (risk rating, growth, ROI) | **0.625 ± 0.10** | +0.125 | 0 | ✔ |
| 2 | Logistic, all 15 features | 0.559 | +0.059 | 0.066 | |
| 3 | Gradient boosting | 0.503 | +0.003 | 0.123 | |
| 4 | No-skill (base rate) | 0.500 | 0 | 0.125 | |
| 5 | Random forest | 0.446 | −0.054 | 0.179 | |

*Benefit:* the small model beats the others in 80–96% of the folds (the t-stat of each gain is between −8 and −11).
On 42 failures, flexible models memorise noise; three features generalise best.

- **Outputs.** `initiatives.json` and `initiatives_decisions.csv` in [results](results/Module_01_Strategic_Initiatives/).
  Figures: `init_eda`, `init_model`, `init_shap`, `init_decision`.
- **Conclusion.**
  - Success is only weakly predictable. The strongest driver is a **Low risk rating** (89% success vs ~70%), then
    segment growth, then expected ROI.
  - NPV is positive for only 3% of projects over 3 years and 33% over 5 years, so project life is the key assumption.
  - Decision: **Fund 21 (₹3,004 cr), Review 18, Reject 141**. Realised success: Fund 86%, others 72–76%.

---

## M2. Credit risk
- **What.** Predict each loan's probability of default (PD), turn it into expected credit loss (ECL) and value, and
  decide **Approve / Review / Reject**.
- **Code.** [notebooks/02_credit_risk.ipynb](notebooks/02_credit_risk.ipynb)
- **How it works.**
  1. **EDA and features.** EMI, payment-to-income, loan-to-income and collateral cover.
  2. **Validation.** Stratified 80/20 split plus 5-fold CV on the training part.
  3. **Models.** Three models, plus a check that the model does not lean on the interest rate.
  4. **Calibration.** A decile calibration curve with Platt scaling as the alternative. The raw PDs are already
     calibrated (gap 0.008), so the raw model is kept.
  5. **Explain and score.** SHAP, then out-of-fold PDs for every loan.
  6. **PD bands.** A <10%, B 10–20%, C 20–35%, D >35%, compared with the brief's 5/15/30% bands.
  7. **ECL.** ECL = PD × 40% × EAD.
  8. **Value.** Net value = interest − 6% funding cost − expected loss.
  9. **Decision.** The approve cut-off is searched to stay within the 3% ECL appetite, then stress-tested
     (PD ×1.5 and ×2, LGD 50% and 60%).

**Model comparison**

| Rank | Model | CV ROC-AUC | Test ROC-AUC | Test calib. gap | Gain vs no-skill | Chosen |
|---|---|---|---|---|---|---|
| 1 | Logistic regression | **0.729** | 0.746 | 0.031 | +0.229 | ✔ |
| 2 | Random forest | 0.706 | 0.752 | 0.032 | +0.206 | |
| 3 | Gradient boosting | 0.702 | 0.745 | 0.012 | +0.202 | |
| 4 | No-skill | 0.500 | 0.500 | – | 0 | |

*Benefit:* logistic regression is the best on CV by about 2× the fold spread, and it is the most transparent.

- **Outputs.** `credit.json` and `credit_decisions.csv` in [results](results/Module_02_Credit_Risk/). Figures:
  `credit_eda`, `credit_model_curves`, `credit_shap`, `credit_bands`, `credit_value`, `credit_frontier`.
- **Conclusion.**
  - **The bands work.** Realised default rises from 7% in band A to 47% in band D.
  - **The book as a whole loses value.** ECL on the whole book is ₹63 cr (9.8%), and about two thirds of loans have
    negative value.
  - **Decision:**
    - **Approve 836** (₹68 cr, ECL 2.8%, realised default 7%).
    - **Review 815** (₹113 cr).
    - **Reject 3,349** (realised default 23%).
  - **Thin margin.** The approved book earns only about 0.5–0.6% a year after expected loss, and PD ×1.5 breaks the
    3% appetite.

---

## M3. Fraud detection
- **What.** Score every transaction for fraud with a supervised model and with Isolation Forest, then pick the alert
  threshold that minimises cost (₹10,000 per missed fraud, ₹500 per false alarm).
- **Code.** [notebooks/03_fraud.ipynb](notebooks/03_fraud.ipynb)
- **How it works.**
  1. **EDA.** Fraud rate by group, compared with the overall rate.
  2. **Leakage-safe features.** Amount ÷ customer average, plus history that uses only earlier transactions.
  3. **Time split.** Train on 2025, validate on Jan–Apr 2026, test on May–Aug 2026.
  4. **Models.** Three class-weighted models plus an unlabelled Isolation Forest.
  5. **Threshold.** The cost curve is scanned on validation and the cheapest threshold is frozen for test.
  6. **Stress.** Costs changed, and model scores degraded with noise.

**Model comparison (untouched test period; every method uses its own cost-optimal threshold)**

| Method | Test PR-AUC | Test ROC-AUC | Test cost (₹ lakh) | Saving vs no model | Chosen |
|---|---|---|---|---|---|
| Random forest | **0.142** | 0.805 | **8.98** | **37.6%** | ✔ |
| Gradient boosting | 0.127 | 0.808 | 9.10 | 36.8% | |
| Logistic regression | 0.094 | 0.775 | 9.90 | 31.2% | |
| Amount-ratio rule (no ML) | 0.094 | 0.772 | 10.48 | 27.3% | |
| Isolation Forest (no labels) | 0.044 | 0.623 | 14.31 | 0.7% | |
| No model | 0.024 | 0.500 | 14.40 | 0% | |

*Benefit:*
- **Choosing the random forest** saves ₹0.12 lakh over gradient boosting and ₹0.92 lakh over logistic regression per
  4 months of test data.
- **ML vs the best business rule:** ₹1.50 lakh saved over the amount-ratio rule.
- **Labels vs anomaly detection:** ₹5.3 lakh saved over Isolation Forest. At the same 300-alert budget the random
  forest catches 51 frauds against 15.

- **Outputs.** `fraud.json` in [results](results/Module_03_Fraud_Detection/). Figures: `fraud_eda`, `fraud_curves`,
  `fraud_shap`, `fraud_cost_curve`.
- **Conclusion.**
  - **The signal is how unusual the amount is** for that customer (the median fraud is 5× usual spend). Location,
    merchant and hour don't matter.
  - **Policy:** investigate about 7.5% of transactions. This catches 51% of fraud and costs **38% less** than having
    no model, about ₹90,000 saved per 1,000 transactions.
  - **Robust:** the saving stays at 20–50% under every stress.

---

## M4. Churn and CLV
- **What.** Predict churn, value each customer, build the 2×2 segments, and choose the 1,000 customers RMs should call.
- **Code.** [notebooks/04_churn_clv.ipynb](notebooks/04_churn_clv.ipynb)
- **How it works.**
  1. **EDA.** Churners vs stayers compared with t-statistics.
  2. **Models.** Three class-weighted models with 5-fold × 5 repeated CV. `Estimated_CLV` is excluded.
  3. **Signal check.** Each model's gain over no-skill is compared with the fold-to-fold noise.
  4. **CLV.** The supplied formula is recovered by regression; a lifetime CLV is rebuilt (10 years, 12%, churn-adjusted).
  5. **Targeting.** The 2×2 segments, then the EVaR (= churn probability × CLV) ranking.
  6. **Backtest.** Four targeting rules are scored against actual churn.
  7. **Campaign economics.** Value protected vs cost, with a sensitivity grid.

**Model comparison (CV ROC-AUC)**

| Model | CV ROC-AUC | Gain vs no-skill | Signal-to-noise |
|---|---|---|---|
| Gradient boosting | 0.510 | +0.010 | 0.18 |
| No-skill | 0.500 | 0 | – |
| Logistic regression | 0.494 | −0.006 | −0.11 |
| Random forest | 0.488 | −0.012 | −0.23 |

*Benefit of choosing a model here: none.* Every gain is far smaller than the noise. Value-led targeting is used instead.

**Targeting rule comparison (backtest on actual churners)**

| Rule for picking 1,000 | Churners reached | Lifetime value of churners reached | Chosen |
|---|---|---|---|
| EVaR (churn × CLV) | 17 | **₹0.95 cr** | ✔ |
| CLV only | 14 | ₹1.01 cr | |
| Churn score only | 17 | ₹0.48 cr | |
| Random | 13 | ₹0.31 cr | |

- **Outputs.** `churn.json` and `churn_top1000.csv` (the RM call list) in [results](results/Module_04_Churn_CLV/).
  Figures: `churn_eda`, `churn_clv`.
- **Conclusion.**
  - **Churn is not predictable** from these variables.
  - **The supplied CLV is a one-year margin:** 4% of income + 3% of deposits + 1.2% of loans + 1.8% of investments
    − ₹5,000 per complaint. The lifetime CLV totals ₹174 cr, and the top 20% of customers hold 42% of it.
  - **Value-led targeting** reaches 3× more value than a random list.
  - **The campaign nets ₹22.8 lakh** (ROI 152%), and RM capacity is the constraint.

---

## M5. Equity returns
- **What.** Test whether ML can rank 15 stocks by next-month return, and build a top-5 portfolio.
- **Code.** [notebooks/05_equity_returns.ipynb](notebooks/05_equity_returns.ipynb)
- **How it works.**
  1. **Audit.** The supplied returns and momentum contain no look-ahead; the macro columns vary by stock.
  2. **Features at each month-end.** Momentum, volatility, beta, volume trend, distance from the 6-month high.
  3. **Target.** Next-month return minus the 15-stock average.
  4. **Walk-forward.** Monthly refits over 38 test months, starting Jul 2023.
  5. **Metrics.** Rank IC (Spearman), hit rate, top-5 portfolio after 10 bps costs.

**Model comparison (out-of-sample)**

| Model | Mean rank IC | IC t-stat | Top-5 return | Top-5 Sharpe | Chosen |
|---|---|---|---|---|---|
| Ridge | **0.056** | 1.23 | 17.2% | 0.72 | ✔ (best IC) |
| Gradient boosting | 0.014 | 0.35 | 20.4% | 1.03 | |
| Random forest | 0.004 | 0.09 | 9.7% | 0.24 | |
| Momentum (no ML) | −0.024 | −0.49 | 11.3% | 0.34 | |
| Equal-weight all 15 (no view) | 0 | – | 16.2% | **1.32** | |

*Benefit:* none of these is significant (t < 2; p > 0.4 against equal-weight).

- **Outputs.** `equity.json` and `equity_predictions.csv` in [results](results/Module_05_Equity_Returns/). Figures:
  `equity_eda`, `equity_backtest`, `equity_shap`.
- **Conclusion.** ML does **not** reliably pick winners here. Concentrating on 5 stocks gives up diversification,
  which is unusually strong because the stocks are almost uncorrelated (0.004).

---

## M6. Portfolio optimisation
- **What.** Turn the forecasts into portfolios and compare equal-weight, traditional Markowitz and ML-based strategies
  after costs.
- **Code.** [notebooks/06_portfolio.ipynb](notebooks/06_portfolio.ipynb)
- **How it works.**
  1. **Common setup.** The same 38 months; monthly rebalance; long-only; 30% cap per stock; 10 bps costs.
  2. **Strategies:**
     - equal-weight
     - Markowitz max-Sharpe (sample means and covariance)
     - minimum variance (Ledoit-Wolf covariance)
     - ML mean-variance (Ridge forecasts)
     - ML tilt of equal-weight
  3. **Metrics.** Sharpe, Sortino, max drawdown, VaR, turnover, effective N, t-stat vs equal-weight.
  4. **Robustness.** Sensitivity to costs, the cap and the estimation window, then a crisis stress (correlations 0.6,
     volatility ×2).

**Strategy comparison**

| Rank | Strategy | Ann. return | Ann. vol | Sharpe | Max DD | Turnover/mo | Gain in Sharpe vs equal-weight | p-value | Chosen |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ML tilt | 18.2% | 7.0% | 1.43 | −3.0% | 31% | +0.13 | 0.16 | |
| 2 | ML mean-variance | 23.0% | 10.5% | 1.38 | −5.5% | 103% | +0.08 | 0.12 | |
| 3 | **Equal-weight** | 16.1% | 6.3% | 1.30 | −2.4% | 7% | 0 | – | ✔ |
| 4 | Minimum variance | 15.9% | 6.3% | 1.28 | −2.7% | 7% | −0.02 | 0.44 | |
| 5 | Markowitz max-Sharpe | 8.4% | 12.3% | 0.15 | −13.3% | 37% | −1.15 | 0.27 | |

*Benefit:* the rule requires +0.10 Sharpe **and** p < 0.10 before a more complex strategy is adopted. No strategy
passes, so equal-weight is kept; the ML tilt is monitored as a paper portfolio.

- **Outputs.** `portfolio.json` and the monthly backtests in [results](results/Module_06_Portfolio_Optimisation/).
  Figure: `portfolio_backtest`.
- **Conclusion.**
  - **Traditional Markowitz fails:** it chases past winners and concentrates in about 6 stocks.
  - **ML mean-variance is cost-sensitive:** it falls below equal-weight at 30 bps costs.
  - **Crisis risk:** in a crisis the monthly 99% VaR jumps from about 5% to **30%**.
  - **Equity line for the allocation:** 13.3% return (the long-run average) and a 25% stress loss.

---

## M7. High-frequency trading
- **What.** Predict the next 100 ms move (UP / DOWN / FLAT) from the order book, turn it into a trading signal, and
  test whether it survives costs.
- **Code.** [notebooks/07_hft.ipynb](notebooks/07_hft.ipynb)
- **How it works.**
  1. **Leakage control.** The two `Future_*` columns are excluded.
  2. **Features.** Order-book imbalance, microprice, spread, depth, order-flow history. The split is by trading day
     (12 train / 4 validation / 4 test).
  3. **Models.** Three models compared on macro-F1.
  4. **Trading rule.** Trade only when P(UP) or P(DOWN) exceeds a threshold chosen on validation. Net P&L = move −
     spread − 0.5 bp fees.
  5. **Stress.** Costs ×2 and ×3, and a 1- or 3-event delay. An execution-timing test is added.

**Model comparison (validation macro-F1; trading on test days at each model's own threshold)**

| Model | Macro-F1 | Net ₹ lakh/day | Net bp/trade | Chosen |
|---|---|---|---|---|
| Multinomial logistic | 0.443 | 6.30 | 1.65 | ✔ (simplest) |
| Random forest | 0.443 | 6.23 | 1.62 | |
| Gradient boosting | 0.443 | 6.32 | 1.66 | |
| Rule: sign of imbalance (no ML) | 0.441 | 4.64 | 0.78 | |
| No-skill | 0.199 | – | – | |

*Benefit:* ML adds about ₹1.7 lakh a day over the imbalance rule by trading more selectively.

- **Outputs.** `hft.json` in [results](results/Module_07_HFT/). Figures: `hft_eda`, `hft_model`, `hft_pnl`.
- **Conclusion.**
  - **Strong signal:** imbalance correlates 0.51 with the next move.
  - **Fragile profit:** costs ×2 gives −₹0.8 lakh a day; a 1-event delay gives −₹1.1 lakh a day.
  - **Execution timing is the robust use:** buying on the model's "buy now" calls avoids about 7 bp per child order.
  - **Decision:** a ₹10 cr pilot with a kill switch.

---

## M8. Derivatives
- **What.** The Black-Scholes benchmark (brief Task 1), ML pricing compared with it (Task 2), and the Greeks, delta
  hedge and VaR of the options book.
- **Code.** [notebooks/08_options.ipynb](notebooks/08_options.ipynb)
- **How it works.**
  1. **Black-Scholes.** Implemented and checked against the supplied price (max difference ₹0.27).
  2. **Error analysis.** Market vs BS error by moneyness and maturity.
  3. **ML pricing.**
     - Target: price ÷ strike.
     - Features: log-moneyness, intrinsic value, maturity, volatility, σ√T, rate, call/put.
     - Validation: 80/20 split with 5-fold CV.
  4. **The book.** NovaFin is assumed short 100 of each option. The Greeks (delta, gamma, vega, theta) come from
     Black-Scholes.
  5. **Hedge and VaR.** Delta hedge per stock, then a 1-day 99% historical-simulation VaR over 252 real days.
  6. **Stress and cost.** Crash and volatility-spike scenarios, then the hedge cost.

**Model comparison (test RMSE vs market price)**

| Rank | Method | RMSE ₹ | ₹ RMSE saved vs Black-Scholes | Chosen |
|---|---|---|---|---|
| 1 | **Black-Scholes** | **9.48** | 0 | pricing model |
| 2 | Hybrid: BS + ML correction | 10.32 | −0.84 | |
| 3 | Gradient boosting | 12.74 | −3.26 | ✔ best ML |
| 4 | Random forest | 14.64 | −5.16 | |
| 5 | Ridge (linear) | 59.53 | −50.06 | |

*Benefit:* no ML model beats Black-Scholes, because the market price is BS plus noise. Keep BS for pricing and hedging.

- **Outputs.** `options.json` in [results](results/Module_08_Derivatives/). Figures: `options_bs_error`,
  `options_ml_vs_bs`, `options_var`.
- **Conclusion.**
  - **The book:** premium ₹19.4 cr and time decay of about ₹7.5 cr a year.
  - **The delta hedge cuts VaR by 80%** (₹0.28 cr to ₹0.06 cr).
  - **Volatility risk remains:** a volatility spike costs ₹5.4 cr whatever the hedge, and a crash costs the hedged
    book ₹10 cr.
  - **Hedging line:** a **₹20 cr buffer** plus a volatility (vega) limit.

---

## Extra. Liquidity reserve
- **What.** Size the liquidity reserve that the brief lists as an allocation destination.
- **Code.** [notebooks/09_liquidity_stress.ipynb](notebooks/09_liquidity_stress.ipynb)
- **How it works.**
  1. **Identities.** Gap = outflows − inflows; buffer = cash + 80% of securities.
  2. **Early-warning forecast.** Tomorrow's gap is forecast with a time split.
  3. **30-day stress.** LCR logic, using historical simulation over every past 30-day window:
     - A: wholesale funding freeze
     - B: freeze + 10% deposit run
     - C: freeze + 20% deposit run

**Forecast comparison (test RMSE of tomorrow's gap)**

| Method | RMSE ₹ cr | Saved vs naive | Chosen |
|---|---|---|---|
| Ridge | 4.60 | 1.91 | |
| 20-day average | 4.68 | 1.82 | ✔ (simplest within 2%) |
| Gradient boosting | 4.75 | 1.75 | |
| Naive (tomorrow = today) | 6.50 | 0 | |

- **Outputs.** `liquidity.json` in [results](results/Extra_Liquidity_Reserve/). Figures: `liquidity_eda`, `liquidity_stress`.
- **Conclusion.**
  - **The gap is funded by wholesale money:** about ₹4.9 cr a day flows out net, covered by about ₹5.0 cr a day of
    wholesale funding.
  - **Under a freeze plus a 10% run,** the ₹114 cr buffer lasts about 15 days. The shortfall is ₹172 cr, so we hold
    a **₹175 cr reserve**, with a further ₹84 cr in the severe case.

---

## M9. Integrated capital allocation
- **What.** The Board's ₹1,000 crore question, answered from every module's results.
- **Code.** [notebooks/10_allocation.ipynb](notebooks/10_allocation.ipynb)
- **How it works.**
  1. **A common yardstick for every line:** expected annual return on capital, stress loss rate and capacity.
     - Initiatives: 12% + PI ÷ 5 years.
     - Lending: return on capital at a 12.5% capital ratio.
     - Equity: the long-run average.
  2. **Explicit risk-appetite limits:**
     - reserve ≥ ₹175 cr
     - hedging buffer of ₹20 cr
     - each Board category ≤ 30%
     - initiatives ≤ 50%
     - equity ≤ 25%
     - total stress loss ≤ 15%
  3. **Allocation rule.** Mandatory lines go first. The remaining candidates are ranked by **(return − 7%) ÷ stress
     loss** and filled in that order while every limit holds. Initiatives are funded whole. This is the Session-5
     capital-rationing rule (rank by profitability index), adjusted for risk.
  4. **Robustness.** The allocation is compared with naive alternatives, then sensitivities, a combined crisis test,
     an integration map and the controls.

**Allocation comparison**

| Allocation | Expected return | Stress loss | Meets every limit? | Chosen |
|---|---|---|---|---|
| Return-chasing (no limits) | 22.0% | 8.5% | **No**: no reserve, ₹971 cr in initiatives | |
| **Recommended** | **16.5% (₹165 cr/yr)** | 11.6% (₹116 cr) | Yes | ✔ |
| Equal split (₹125 cr per category) | 12.3% | 8.2% | Yes | |
| All in liquid assets | 6.5% | 0% | Yes | |

- **Outputs.** `allocation.json`, `final_allocation_board.csv`, `final_allocation_lines.csv` and
  `funded_initiatives.csv` in [results](results/Module_09_Integrated_Allocation/). Figure: `allocation`.

---

## Final conclusion for the Board

**Recommended deployment of ₹1,000 crore**

| Board category | ₹ cr | Share | What it funds |
|---|---|---|---|
| Equity investments | 250 | 25% | equal-weight 15-stock sleeve |
| Wealth management | 221 | 22% | initiative 1075 (Low risk, P(success) 0.92, PI 0.71) |
| Liquidity reserves | 175 | 18% | cash and government securities (survive a funding freeze + 10% deposit run) |
| Digital banking | 163 | 16% | initiatives 1041, 1149, 1038 (Low risk, P ≈ 0.91) |
| Corporate lending | 120 | 12% | initiative 1062 (₹103 cr) + ₹16 cr capital for approved corporate loans |
| Retail lending | 41 | 4% | capital for ≈ ₹330 cr of approved retail loans (PD < 0.11) |
| Risk management / hedging | 20 | 2% | derivatives hedging buffer |
| High-frequency trading | 10 | 1% | pilot with kill switch, mainly execution |

**Expected return ≈ 16.5% a year (₹165 cr)**. Stress loss is ₹116 cr, inside the ₹150 cr appetite. Even if every
stress hits in the same year, the group still earns about ₹49 cr. The allocation is unchanged under every sensitivity
except a severe liquidity requirement or a tighter appetite, which mainly move money from equity and retail lending
into the reserve.

**Where ML paid off, and where it did not**
- **Useful:**
  - credit (AUC 0.75, calibrated PDs)
  - fraud (38% lower cost)
  - HFT execution timing
- **Weak but usable:** initiatives (AUC 0.63, a risk adjustment on top of NPV).
- **No signal:** churn and stock picking. Use value-led targeting and diversification instead.
- **Theory wins:** option pricing, where Black-Scholes beats every ML model.

The integrated lesson: ML adds value where there is real signal and a clear cost function. Where there is no signal,
the disciplined answer is the simpler model or the theory, and the capital decision rests on finance (NPV, ECL,
diversification, stress tests).

---

## Course alignment of methods
Every method was checked against the course notes (sessions 1–19). Methods the notes do not cover were replaced:

| Replaced | Replacement used |
|---|---|
| chi-square and Mann-Whitney tests | group rates and the t-statistic of the mean difference |
| Brier score | calibration gap (average \|predicted − observed\| across deciles, from the calibration curve) |
| label-permutation test | gain over no-skill compared with the fold-to-fold noise |
| polynomial features | Ridge on engineered finance features (intrinsic value, σ√T) |
| expected shortfall, Monte Carlo VaR | historical-simulation VaR (Session 12) |
| block bootstrap | historical simulation over every past 30-day window |
| annuity factor | PI ÷ 5-year life |
| linear/integer programming | ranking by risk-adjusted return within limits (Session 5 capital rationing) |

Black-Scholes, the Greeks and delta hedging (Module 8) are covered in the course's derivatives sessions, which are
still in progress, and the project brief explicitly requires them. They are implemented and explained in notebook 08.

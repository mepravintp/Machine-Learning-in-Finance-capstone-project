"""Generate the NovaFin deliverables: report (HTML + PDF), Board deck (PDF) and deck with speaker notes (HTML)."""
import re, base64, json, subprocess, sys
from pathlib import Path
import markdown

ROOT = Path(r"C:/Users/pravi/PG IITB/Machine Learning in Finance/capstone project solution/novafin_capstone")
OUT = ROOT / "deliverables"; OUT.mkdir(exist_ok=True)
FIG = ROOT / "figures"
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

def img(rel, caption="", width="100%"):
    """Embed a figure as base64 so the HTML is self-contained."""
    data = base64.b64encode((FIG / rel).read_bytes()).decode()
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return f'<figure><img src="data:image/png;base64,{data}" style="width:{width}">{cap}</figure>'

def md(text):
    """Markdown -> HTML. Python-Markdown needs a blank line before a list, so insert one where it is missing."""
    lines, out, in_code = text.splitlines(), [], False
    for ln in lines:
        if ln.strip().startswith("```"):
            in_code = not in_code
        is_item = bool(re.match(r"^\s*([-*]|\d+\.)\s", ln))
        prev = out[-1] if out else ""
        prev_is_item = bool(re.match(r"^\s*([-*]|\d+\.)\s", prev)) or prev.startswith("   ")
        if not in_code and is_item and prev.strip() and not prev_is_item:
            out.append("")
        out.append(ln)
    return markdown.markdown(chr(10).join(out), extensions=["tables", "fenced_code", "sane_lists"])

# ------------------------------------------------------------------------------------------------------------------
# 1. REPORT
# ------------------------------------------------------------------------------------------------------------------
R = []   # list of html chunks
R.append(md("""
# NovaFin Group: ML-Driven Capital Allocation
## Detailed Report and Code Guide
**ML in Finance capstone, IIT Bombay** · Pravin · November 2026

**The Board's question:** *How should NovaFin use ML to grow its business while keeping credit, fraud, market,
liquidity and derivatives risk acceptable, and where should the ₹1,000 crore of new capital go?*
"""))
R.append('<div class="pagebreak"></div>')
R.append(md("""
## Contents
1. Executive summary
2. Business context and approach
3. Data, validation and governance principles
4. Module-wise methodology and results (Modules 1–8 and the liquidity layer)
5. Financial decision framework
6. Integrated capital allocation (Module 9)
7. Risks, limitations and controls
8. Code guide: reusable Python / Colab framework
9. Appendix: assumptions and file inventory
"""))
R.append('<div class="pagebreak"></div>')

R.append(md("""
## 1. Executive summary

**Recommendation.** Deploy the ₹1,000 crore in three layers:

1. **Grow** where the evidence is strongest: five high-value strategic initiatives (₹487 cr) and a small,
   well-priced lending book.
2. **Earn steadily** through a diversified equity sleeve (₹250 cr).
3. **Protect** the group with a liquidity reserve, a derivatives hedging buffer and a tightly capped HFT pilot (₹205 cr).

| Board category | ₹ crore | Share | Expected return | What it funds |
|---|---|---|---|---|
| Equity investments | 250 | 25% | 13.3% | equal-weight 15-stock sleeve |
| Wealth management | 221 | 22% | 26.2% | initiative 1075 (Low risk, P(success) 0.92) |
| Liquidity reserves | 175 | 18% | 6.5% | cash and government securities |
| Digital banking | 163 | 16% | 19.6% | initiatives 1041, 1149, 1038 |
| Corporate lending | 120 | 12% | 21.9% | initiative 1062 + capital for approved corporate loans |
| Retail lending | 41 | 4% | 11.3% | capital for ≈ ₹330 cr of approved retail loans |
| Risk management / hedging | 20 | 2% | −3.8% | derivatives hedging buffer (insurance cost) |
| High-frequency trading | 10 | 1% | 0% | pilot with kill switch |
| **Total** | **1,000** | 100% | **16.5% (₹165 cr / yr)** | stress loss ₹116 cr (limit ₹150 cr) |

**Risk.** The combined stress loss (₹116 cr, 11.6% of capital) is inside the 15% appetite. If every stress happens in
the same year, the group still earns about **₹49 cr**. The liquidity reserve covers a 30-day wholesale-funding freeze
plus a 10% deposit run.

**What ML delivered.** ML adds real value where there is signal and a clear cost function:

- **Credit:** calibrated PDs, AUC 0.75.
- **Fraud:** 38% lower operating cost.
- **Trade execution:** about 7 bp of timing benefit per order.

Where the data hold no signal (churn, stock picking) or where theory already explains prices (options), the
disciplined choice was the simpler model or the theory. The capital decision rests on finance: NPV, ECL,
diversification and stress tests.
"""))
R.append(img("Module_09_Integrated_Allocation/allocation.png", "Figure 1. Recommended allocation and the return / stress-loss profile of every candidate."))
R.append('<div class="pagebreak"></div>')

R.append(md("""
## 2. Business context and approach

NovaFin is a diversified financial group: banking, consumer and SME lending, wealth, equity investments, treasury and
derivatives. The Board does not want isolated models. It wants one integrated answer, built on a chain that every
module must follow:

**Data → ML prediction → Financial metric → Risk assessment → Business decision**

| Module | ML prediction | Financial metric | Decision |
|---|---|---|---|
| 1 Strategic initiatives | P(success) | NPV, expected NPV, profitability index | Fund / Review / Reject |
| 2 Credit risk | probability of default | ECL = PD × LGD × EAD, value per loan | Approve / Review / Reject |
| 3 Fraud | fraud probability, anomaly score | expected operational cost | alert threshold |
| 4 Churn & CLV | churn probability | lifetime value, value at risk | 1,000-customer RM list |
| 5–6 Equity & portfolio | next-month relative return | Sharpe, drawdown, VaR | portfolio construction |
| 7 HFT | 100 ms direction | net bp per trade after costs | trade / pilot / execution use |
| 8 Derivatives | ML option price | Black-Scholes error, Greeks, VaR | hedge and buffer |
| Liquidity (extra) | next-day gap forecast | 30-day stressed need (LCR logic) | reserve size |
| 9 Allocation | all of the above | return and stress loss per rupee | ₹1,000 cr split |

## 3. Data, validation and governance principles

**Data.** Eight synthetic files, with no missing values and no duplicates.

| File | Rows | Use |
|---|---|---|
| strategic_initiatives | 180 | Module 1 |
| nova_loans | 5,000 | Module 2 |
| nova_transactions | 30,000 | Module 3 |
| nova_customers | 5,000 | Module 4 |
| nova_market_data | 21,855 (15 stocks, 2021–26) | Modules 5–6, 8 |
| nova_hft_orderbook | 120,000 (10 stocks, 20 days) | Module 7 |
| nova_options | 10,000 | Module 8 |
| nova_liquidity | 1,216 days | liquidity reserve |

**Units.**
- Loans and customers are in rupees (read as lakh, incomes would be absurd).
- Initiatives are assumed ₹ crore.
- Liquidity is in ₹ lakh, as the README says.

**Validation rules.** The split always matches how the model would be used:

| Data type | Split | Why |
|---|---|---|
| Cross-sectional (initiatives, loans, customers, options) | stratified k-fold, repeated when small | no time order; keep class balance |
| Time series (transactions, market, liquidity) | time-based / walk-forward | avoid look-ahead bias |
| HFT | by trading day | events within a day are not independent |

**Leakage rules.**
- No future information: the HFT `Future_*` columns are excluded, and history features use earlier transactions only.
- No target proxies: `Estimated_CLV` is kept out of the churn features, and the supplied Black-Scholes price is not
  an input to the ML pricer.

**Model choice rule.** Every task compares at least three models. The **simplest model wins** unless a more complex
one is better by a clear margin (0.005 AUC, or 2% RMSE). The comparison table in each module shows the gain of each
choice over a no-skill baseline and its gap to the best model.

**Explainability.** SHAP or coefficients for every chosen model, read in plain English.

**Course alignment.** Only methods from the course were used (sessions 1–19). Untaught techniques were replaced:
- chi-square → group rates and the t-statistic
- Brier score → calibration gap
- bootstrap and Monte Carlo VaR → historical simulation
- optimisation solvers → profitability-index ranking

The exception is Black-Scholes, the Greeks and HFT direction prediction, which the brief explicitly requires.
"""))
R.append('<div class="pagebreak"></div>')

R.append(md("""
## 4. Module-wise methodology and results

### Module 1: Strategic capital allocation
**Question.** Which of 180 initiatives should be funded?

**Method.**
1. **EDA.** Investment, ROI, risk rating, business units, growth vs ROI, investment vs success.
2. **Models.** Four classifiers on `Historical_Success`, validated with 5-fold stratified CV × 10 repeats.
3. **Scoring.** Out-of-fold P(success) for every initiative, explained with SHAP.
4. **NPV.** Cash flow = revenue − operating cost, discounted at 12%, over a 5-year life.
5. **Expected NPV.** E[NPV] = P × NPV − (1 − P) × loss-on-failure × investment.
6. **Profitability index (PI).** E[NPV] ÷ investment.
7. **Rule.**
   - Fund if PI ≥ 0.10, P ≥ 0.75 and the risk rating is not High.
   - Reject if E[NPV] ≤ 0 or P < 0.60.
   - Review otherwise.

| Model (CV ROC-AUC) | AUC | Gain vs no-skill | Chosen |
|---|---|---|---|
| Logistic, 3 drivers | **0.625 ± 0.10** | +0.125 | ✔ |
| Logistic, all features | 0.559 | +0.059 | |
| Gradient boosting | 0.503 | +0.003 | |
| Random forest | 0.446 | −0.054 | |

**Results.**
- **Prediction is weak.** On 42 failures the flexible models overfit, so the smallest model is best.
- **Drivers.** A Low risk rating (89% success vs about 70%) matters most, then segment growth, then expected ROI.
- **NPV.** 3% of projects are positive over 3 years and 33% over 5 years.
- **Decision.** **Fund 21 (₹3,004 cr), Review 18, Reject 141.** Realised success is 86% in the Fund group vs 72–76%
  elsewhere.
- **Key judgement.** Project life: a 3-year view funds nothing.
"""))
R.append(img("Module_01_Strategic_Initiatives/init_decision.png", "Figure 2. Initiative decision map (bubble = investment) and the capital needed by the Fund list."))
R.append(md("""
### Module 2: Credit risk
**Question.** Which loans should NovaFin approve, review or reject?

**Method.**
1. **Features.** EMI, payment-to-income, loan-to-income and collateral cover.
2. **Validation.** Stratified 80/20 split plus 5-fold CV.
3. **Models.** Three models; a decile calibration check with Platt scaling as the alternative; SHAP.
4. **PD and bands.** Out-of-fold PD for all 5,000 loans, grouped into bands A–D relative to the 20% average default
   rate, compared with the brief's 5/15/30% bands.
5. **ECL.** ECL = PD × 40% × EAD.
6. **Net value.** Interest − 6% funding cost − expected loss.
7. **Cut-off.** The approval PD cut-off is searched so the approved book stays within the 3% ECL appetite.

| Model | CV ROC-AUC | Test ROC-AUC | Chosen |
|---|---|---|---|
| Logistic regression | **0.729** | 0.746 | ✔ |
| Random forest | 0.706 | 0.752 | |
| Gradient boosting | 0.702 | 0.745 | |

**Results.**
- **The bands work.** Realised default rises from 7% (band A) to 47% (band D), and the PDs are well calibrated
  (gap 0.008).
- **The current book loses value.** ECL is ₹63 cr (9.8%), and two thirds of loans have negative value at current pricing.
- **Decision.**
  - **Approve 836 loans** (₹68 cr, ECL 2.8%, realised default 7%).
  - **Review 815.**
  - **Reject 3,349** (realised default 23%).
- **Thin margin.** About 0.5–0.6% a year after expected loss. A PD ×1.5 stress breaks the 3% appetite.
"""))
R.append(img("Module_02_Credit_Risk/credit_bands.png", "Figure 3. Predicted vs realised default by PD band.", "70%"))
R.append('<div class="pagebreak"></div>')
R.append(md("""
### Module 3: Fraud detection
**Question.** Which transactions should be investigated?

**Method.**
1. **Leakage-safe features.** Amount ÷ customer average, plus history from earlier transactions only.
2. **Time split.** Train on 2025, validate on Jan–Apr 2026, test on May–Aug 2026.
3. **Models.** Three class-weighted classifiers, plus an Isolation Forest without labels.
4. **Threshold.** Scanned on validation to minimise 10,000 × missed + 500 × false alarms, then frozen for test.

| Method (test period) | PR-AUC | Cost ₹ lakh | Saving vs no model | Chosen |
|---|---|---|---|---|
| Random forest | **0.142** | **8.98** | **37.6%** | ✔ |
| Gradient boosting | 0.127 | 9.10 | 36.8% | |
| Logistic regression | 0.094 | 9.90 | 31.2% | |
| Amount-ratio rule (no ML) | 0.094 | 10.48 | 27.3% | |
| Isolation Forest | 0.044 | 14.31 | 0.7% | |
| No model | 0.024 | 14.40 | 0% | |

**Results.**
- **What drives fraud.** How unusual the amount is for that customer: the median fraud is 5× usual spend.
- **Policy.** Investigate 7.5% of transactions. This catches 51% of fraud at 16% precision and **saves 38%**, about
  ₹90,000 per 1,000 transactions.
- **Robust.** The saving stays at 20–50% under every cost and drift stress.
- **Anomaly detection is not enough.** "Unusual" is not "fraudulent", so it serves only as a second line.
"""))
R.append(img("Module_03_Fraud_Detection/fraud_cost_curve.png", "Figure 4. Operational cost vs alert volume (validation period).", "75%"))
R.append(md("""
### Module 4: Churn and customer lifetime value
**Question.** If NovaFin can contact only 1,000 customers, whom should it call?

**Method.**
1. **Churn models.** Three models with repeated CV; CLV is excluded.
2. **Signal check.** The gain over no-skill is compared with the fold-to-fold noise.
3. **CLV formula.** The supplied CLV formula is recovered by regression.
4. **Lifetime CLV.** Rebuilt as annual margin × Σ survival ÷ discount over 10 years at 12%.
5. **Targeting.** A 2×2 risk-value matrix, then a ranking by EVaR = P(churn) × CLV, backtested on actual churners.

**Results.**
- **No churn signal.** CV AUC is 0.49–0.51 with a signal-to-noise ratio below 1. This is an honest finding: a churn
  model here would give false precision.
- **The supplied CLV is a one-year margin:** 4% of income + 3% of deposits + 1.2% of loans + 1.8% of investments
  − ₹5,000 per complaint.
- **Lifetime value.** ₹174 cr in total, and the top 20% of customers hold 42% of it.
- **Targeting.** The value-led list reaches churners worth ₹0.95 cr, against ₹0.31 cr for a random list (3×).
- **Campaign.** 1,000 RM calls net **₹22.8 lakh** (ROI 152%). RM capacity, not budget, is the constraint.

### Modules 5 and 6: Equity returns and portfolio optimisation
**Question.** Can ML pick stocks with superior returns, and which portfolio should hold them?

**Method.**
1. **Features.** Month-end values using past data only: momentum, volatility, beta, volume trend, distance from high.
2. **Target.** Next-month return relative to the 15-stock average.
3. **Walk-forward.** 38 out-of-sample months with monthly refits (Ridge, random forest, gradient boosting) against
   a momentum benchmark.
4. **Portfolios.** Five strategies, long-only, 30% cap per stock, 10 bps costs.

| Strategy | Return | Vol | Sharpe | Turnover / month |
|---|---|---|---|---|
| ML tilt | 18.2% | 7.0% | 1.43 (p = 0.16) | 31% |
| ML mean-variance | 23.0% | 10.5% | 1.38 (p = 0.12) | 103% |
| **Equal-weight (chosen)** | 16.1% | 6.3% | 1.30 | 7% |
| Minimum variance (Ledoit-Wolf) | 15.9% | 6.3% | 1.28 | 7% |
| Markowitz max-Sharpe | 8.4% | 12.3% | 0.15 | 37% |

**Results.**
- **Forecasting.** The best rank IC is 0.056 (Ridge, t = 1.2), which is not significant.
- **Traditional Markowitz fails:** it chases past winners.
- **ML strategies look better but are not proven** (p > 0.1), and ML mean-variance is cost-sensitive.
- **Decision.** Equal-weight sleeve, with the ML tilt monitored as a paper portfolio.
- **Crisis risk.** Monthly 99% VaR rises from 5% to **30%**.
"""))
R.append(img("Module_06_Portfolio_Optimisation/portfolio_backtest.png", "Figure 5. Out-of-sample growth of ₹1 after costs, risk vs return, and Markowitz weight instability."))
R.append('<div class="pagebreak"></div>')
R.append(md("""
### Module 7: High-frequency trading
**Question.** Can order-book data predict 100 ms moves well enough to trade?

**Method.**
1. **Target.** `Price_Move_Class`: UP / DOWN / FLAT, where FLAT means a move under 1.2 bp.
2. **Leakage control.** The `Future_*` columns are excluded.
3. **Features.** Order-book imbalance, microprice, spread, depth and order-flow history.
4. **Split.** By trading day: 12 train, 4 validation, 4 test.
5. **Models.** Three, compared on macro-F1.
6. **Trading rule.** Trade only above a validation-chosen probability. Net = move − spread − 0.5 bp fees.
7. **Stress.** Costs × 2 and × 3, and a 1- or 3-event delay.

| Model | Macro-F1 | Net ₹ lakh / day (test) |
|---|---|---|
| Multinomial logistic (chosen, simplest) | 0.443 | 6.30 |
| Gradient boosting | 0.443 | 6.32 |
| Random forest | 0.443 | 6.23 |
| Rule: sign of imbalance | 0.441 | 4.64 |
| No-skill | 0.199 | – |

**Results.**
- **Strong signal.** Imbalance correlates 0.51 with the next move.
- **The edge does not survive frictions.** With costs × 2 the result is −₹0.8 lakh a day; with a 1-event delay it is
  −₹1.1 lakh a day.
- **Execution timing is the robust use.** "Buy now" calls meet a +3.4 bp next move vs −3.9 bp for "wait".
- **Decision.** A ₹10 cr pilot with a kill switch, used mainly inside execution algorithms.

### Module 8: Derivatives
**Question.** Can ML price options better than theory, and how should the exposure be hedged?

**Method.**
1. **Black-Scholes.** Implemented and checked against the supplied price (max difference ₹0.27).
2. **ML pricing.**
   - Target: price ÷ strike.
   - Features: log-moneyness, intrinsic value, maturity, volatility, σ√T, rate, call/put.
3. **The book.** Assumed short 100 of each option. Greeks (delta, gamma, vega, theta) are computed for it.
4. **Hedge and VaR.** Delta hedge per stock, then a 1-day 99% historical-simulation VaR over 252 real days.
5. **Stress.** Crash and volatility-spike scenarios.

| Method (test RMSE ₹) | RMSE | vs Black-Scholes |
|---|---|---|
| **Black-Scholes** | **9.48** | benchmark |
| Hybrid (BS + ML correction) | 10.32 | +0.84 |
| Gradient boosting (best ML) | 12.74 | +3.26 |
| Random forest | 14.64 | +5.16 |
| Ridge (linear) | 59.53 | +50.06 |

**Results.**
- **No ML model beats Black-Scholes:** market prices are BS plus noise.
- **The delta hedge cuts 1-day VaR by 80%** (₹0.28 cr → ₹0.06 cr).
- **Volatility risk remains.** A volatility spike still costs ₹5.4 cr, and a crash costs the hedged book ₹10 cr.
- **Decision.** A ₹20 cr hedging buffer plus a vega limit.
"""))
R.append(img("Module_08_Derivatives/options_var.png", "Figure 6. 1-day P&L of the options book, unhedged vs delta-hedged.", "70%"))
R.append(md("""
### Liquidity reserve (extra layer)
**Question.** How much of the ₹1,000 cr must stay liquid?

**Method.**
1. **Identities.** Gap = outflows − inflows; buffer = cash + 80% of securities.
2. **Early-warning forecast.** Tomorrow's gap (Ridge, 20-day average, gradient boosting vs naive).
3. **LCR-style stress.** 30 days, using historical simulation over every past 30-day window.

| Scenario (30 days, 99%) | Need | Shortfall vs ₹114 cr buffer | Survival |
|---|---|---|---|
| A. Wholesale funding freeze | ₹199 cr | ₹85 cr | 23 days |
| **B. Freeze + 10% deposit run (policy)** | ₹286 cr | **₹172 cr** | 15 days |
| C. Severe: freeze + 20% run | ₹372 cr | ₹259 cr | 11 days |

**Results.**
- **The daily gap is noise** (forecast R² ≈ 0), so forecasting cannot replace a reserve.
- **The gap is funded by wholesale money:** about ₹4.9 cr a day flows out net, covered by about ₹5.0 cr a day of
  wholesale funding.
- **Decision.** A **₹175 cr reserve**, with a contingency plan for a further ₹84 cr.
"""))
R.append('<div class="pagebreak"></div>')
R.append(md("""
## 5. Financial decision framework

**Step 1: one yardstick for every line.** Each line gets an expected annual return on capital, a stress loss rate
and a capacity limit.

| Line | Expected return | Stress loss | Source |
|---|---|---|---|
| Initiatives (each project) | 12% hurdle + PI ÷ 5 years | loss-on-failure × (failure prob + 10 pts) | M1 |
| Lending | 7% + (spread after expected loss) ÷ 12.5% capital ratio | extra ECL at PD ×1.5, LGD 50%, ÷ 12.5% | M2 |
| Equity | 13.3% long-run average (not the 16% backtest) | 25% (market −25%) | M5–6 |
| HFT pilot | 0% (edge fails under stress) | 50% | M7 |
| Hedging buffer | 7% − re-hedging cost | 50% | M8 |
| Liquidity reserve | 6.5% | 0% | liquidity |

**Step 2: risk appetite as explicit limits.**
- reserve ≥ ₹175 cr
- hedging buffer of ₹20 cr
- each Board category ≤ 30%
- all initiatives ≤ 50% (the success model is weak and NPV depends on project life)
- equity ≤ 25%
- total stress loss ≤ 15% of capital
- approved credit ECL ≤ 3%

**Step 3: allocation rule (capital rationing, Session 5).**
1. Fund the mandatory lines first.
2. Rank every other candidate by **excess return per unit of stress loss** = (return − 7%) ÷ stress loss. This is a
   Sharpe-style, risk-adjusted profitability index.
3. Fund down the list. An initiative is taken only whole; nothing is added if it would breach a limit, and nothing
   earning below the reserve yield is taken.
4. Leftover money stays liquid.

**Step 4: test it.**
- compare with simple alternatives
- run sensitivities
- run a combined crisis test

| Allocation | Expected return | Stress loss | Meets every limit? |
|---|---|---|---|
| Return-chasing (no limits) | 22.0% | 8.5% | No: no reserve, ₹971 cr in initiatives |
| **Recommended** | **16.5%** | 11.6% | **Yes** |
| Equal split (₹125 cr per category) | 12.3% | 8.2% | Yes |
| All in liquid assets | 6.5% | 0% | Yes |

## 6. Integrated capital allocation (Module 9)

**Sensitivity.**
- The allocation is unchanged if initiatives earn 10 points less (3-year view), equity earns 5 points less, or
  lending earns 4 points less. Only the expected return moves, to 11.6–16.2%.
- A severe liquidity requirement (₹259 cr reserve) or a tighter 10% stress limit mainly moves money out of equity
  and retail lending.

**Combined crisis test.** If every stress happens in the same year, expected earnings are ₹165 cr and stress losses
₹116 cr, leaving **+₹49 cr**. Capital is preserved, and the reserve covers the 30-day stressed funding need.

**Integration map.**

| Line | ML prediction | Financial metric | Risk assessment | Decision |
|---|---|---|---|---|
| Initiatives | P(success), AUC 0.63 | E[NPV], PI | success −10 pts; 3-year life | fund 5 projects, ₹487 cr |
| Credit | PD, AUC 0.75 | ECL, ROE | PD ×1.5 → ECL 4.2% | approve PD < 0.11; ₹58 cr capital |
| Fraud | RF, PR-AUC 0.142 | operational cost | cost and drift stress | deploy; 38% saving (opex) |
| Churn & CLV | no signal | lifetime CLV, EVaR | save-rate / cost grid | 1,000 RM calls; net ₹23 lakh |
| Equity | IC 0.056 (n.s.) | Sharpe, VaR | crisis VaR 30% | ₹250 cr equal-weight |
| HFT | macro-F1 0.44 | net bp per trade | costs × 2, latency | ₹10 cr pilot |
| Derivatives | ML < Black-Scholes | Greeks, VaR | crash, vol spike | ₹20 cr buffer, vega limit |
| Liquidity | gap forecast | 30-day stressed need | freeze + 10% run | ₹175 cr reserve |
"""))
R.append('<div class="pagebreak"></div>')
R.append(md("""
## 7. Risks, limitations and controls

**Data limitations.**
- **Synthetic data.** Several patterns are unrealistic: the stocks are uncorrelated, HFT moves exceed the spread by
  3.5×, the macro columns vary by stock, and the churn flag looks random.
- **Small samples.** Initiatives have 180 rows and 42 failures; the HFT test covers 4 days.
- **Unit assumptions.** Initiatives are treated as crore and liquidity as lakh.

**Model risk.**
- **Weak or absent signals:** initiatives, churn, equity.
- **Regime change.** Fraud and HFT patterns can shift.
- **Assumptions drive results:** the 5-year project life, loss on failure, the 12.5% capital ratio, the retention
  save rate, and the LCR run-off rates. Each is stated and stress-tested in its notebook.

| Risk | Control | Trigger | Owner |
|---|---|---|---|
| Credit | approve only PD < 0.11 with positive value; reprice the review queue | approved ECL > 3% | CRO |
| Initiatives | stage-gated tranches; re-score P(success) yearly | 2 quarters behind plan → stop next tranche | CFO |
| Equity | equal-weight, 25% cap, quarterly rebalance | drawdown > 10% → halve the sleeve | CIO |
| Derivatives | daily delta hedge; vega limit; ₹20 cr buffer | volatility exposure above limit → buy protection | Head of derivatives |
| HFT | ₹10 cr pilot, kill switch | daily loss > ₹0.5 cr or cumulative > ₹2 cr → stop | Head of trading |
| Liquidity | reserve ≥ scenario-B need | coverage < 110% → stop wholesale-funded growth | Treasurer / ALCO |
| Fraud | cost-optimal threshold; monthly PR-AUC | PR-AUC −30% or alerts ×2 → retrain | Head of fraud ops |
| Model risk | inventory, annual validation, SHAP on file | any drift alarm → revalidate | Model risk committee |

**Model governance and explainability.**
- Every model has a named owner, a monitoring metric and a retraining trigger.
- Every decision model is explained with SHAP or coefficients, so a credit refusal or a fraud alert can be justified
  to a customer or a regulator.
- Simple models were preferred whenever complexity did not pay, which keeps governance cheap and explanations honest.
"""))
R.append('<div class="pagebreak"></div>')
R.append(md("""
## 8. Code guide: reusable Python / Colab framework

### 8.1 Folder structure
```
novafin_capstone/
├── data/                    eight CSV files
├── src/novafin.py           shared assumptions, loaders, metrics, comparison and hand-off helpers
├── notebooks/               00 … 10, run in order (each saves its results)
├── results/<Module_NN_Name>/ JSON and CSV hand-off files per module
├── figures/<Module_NN_Name>/ charts per module
├── deliverables/            report, Board deck
├── CENTRAL.md               module guide with index and comparison tables
└── PROGRESS.md              status, numbers, figures
```

### 8.2 How to run
- **Locally.** `pip install pandas numpy scikit-learn matplotlib seaborn shap scipy jupyter`, then open the
  notebooks in order 00 → 10 and run all cells.
- **Colab.** Upload the whole folder to Google Drive, mount it, `cd` into `notebooks/` and run. `find_root()`
  locates the project automatically.
- **Change an assumption** (e.g. LGD, discount rate) in `ASSUMPTIONS` inside `src/novafin.py` and re-run. Every
  module picks it up.

### 8.3 The shared module (`src/novafin.py`)
```python
import sys; sys.path.insert(0, '../src')
from novafin import *                 # ASSUMPTIONS, SEED, load(), metrics, plotting, hand-off helpers
RES, FIG = use_module('03')           # outputs go to results/Module_03_Fraud_Detection/ and figures/...

tx = load('transactions')             # any of the eight datasets by short name
binary_report(y, p)                   # ROC-AUC, Gini, KS, PR-AUC, calibration gap
calibration_table(y, p)               # predicted vs observed by decile
compare_models(table, 'PR-AUC', chosen='Random forest', baseline='No-skill')   # benefit-of-choice table
save_result('fraud', payload)         # hand-off JSON for notebook 10
load_result('fraud')                  # read any module's result
```

### 8.4 Notebook template (every module follows it)
```python
# 1. Audit and EDA            -> quality checks, class balance, group rates, t-statistics
# 2. Features + leakage check -> only information known at decision time
# 3. Split                    -> stratified k-fold | time-based | walk-forward | by day
# 4. Compare >= 3 models      -> compare_models(...) with a no-skill baseline; simplest wins unless clearly beaten
# 5. Validate and explain     -> calibration, error by segment, SHAP
# 6. Financial layer          -> NPV / ECL / cost / CLV / Sharpe / VaR
# 7. Decision + stress test   -> rule, sensitivities, stress scenarios
# 8. Risks and limitations    -> written in markdown
# 9. Export                   -> save_result(...) for notebook 10
```

### 8.5 Reusable building blocks
**Walk-forward forecasting (Modules 5–6)**
```python
for i in range(MIN_TRAIN_MONTHS, len(dates)):
    t = dates[i]
    train = data[data.Date < t].dropna(subset=['Fwd_Excess'])     # only the past
    test  = data[data.Date == t]
    model.fit(train[FEATURES], train.Fwd_Excess)
    preds.append(test.assign(Pred=model.predict(test[FEATURES])))
```
**Cost-based threshold (Modules 3 and 7)**
```python
def cost_at(y, score, t):
    alert = score >= t
    return 10_000 * ((~alert) & (y == 1)).sum() + 500 * (alert & (y == 0)).sum()
thresholds = np.unique(np.quantile(val_score, np.linspace(0, 1, 801)))
best_t = min(thresholds, key=lambda t: cost_at(y_val, val_score, t))   # choose on validation, apply to test
```
**Expected credit loss (Module 2)**
```python
data['ECL'] = data.PD * ASSUMPTIONS['LGD'] * data.Loan_Amount
```
**Expected NPV and profitability index (Module 1)**
```python
npv  = -I0 + sum(cf_t / (1 + r) ** t for t, cf_t in enumerate(cash_flows, start=1))
enpv = p * npv - (1 - p) * loss_rate * I0
pi   = enpv / I0
```
**Historical-simulation VaR (Modules 8 and liquidity)**
```python
pnl = [revalue(book, shocks_on_day) - value_today for shocks_on_day in history]
var_99 = -np.quantile(pnl, 0.01)
```
**Risk-adjusted capital rationing (Module 9)**
```python
candidates.sort(key=lambda c: (c.ret - RF) / c.stress, reverse=True)
for c in candidates:              # take whole projects / as much of a line as every limit allows
    amount = room_under_all_limits(c)
    ...
```

## 9. Appendix: assumptions and outputs

| Assumption | Value | Source |
|---|---|---|
| LGD | 40% | brief |
| Fraud costs | ₹10,000 missed / ₹500 false alarm | brief |
| Budget / contacts | ₹1,000 cr / 1,000 customers | brief |
| Discount rate (hurdle) | 12% | assumption |
| Risk-free | 7% | ≈ Indian 10-year G-sec |
| Cost of funds | 6% | assumption |
| ECL appetite | 3% of approved book | assumption |
| Project life | 5 years | assumption (3 and 7 tested) |
| Loss on failure | 30 / 50 / 70% by risk rating | assumption |
| Capital ratio for lending | 12.5% | Basel-style CAR |
| Retention save rate / call cost | 30% / ₹1,500 | assumption (grid tested) |
| Equity costs | 10 bps per unit traded | assumption |
| Options book | short 100 of each option | assumption |
| Liquidity stress | freeze + 10% deposit run, 30 days, 99% | LCR logic |

**Outputs.** Every result file is in `results/<module folder>/` and every chart in `figures/<module folder>/`.
[CENTRAL.md](../CENTRAL.md) links each module's notebook, results and figures.
"""))

REPORT_CSS = """
@page { size: A4; margin: 16mm 15mm 18mm 15mm; }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.3pt; line-height: 1.45; color: #1d2a35; max-width: 900px; margin: 0 auto; padding: 20px; background:#fff; }
h1 { font-size: 26pt; color: #0f3d5c; margin: 80px 0 4px; }
h2 { font-size: 15pt; color: #0f3d5c; border-bottom: 2px solid #2a9d8f; padding-bottom: 3px; margin-top: 22px; }
h3 { font-size: 12pt; color: #2a6f97; margin: 16px 0 6px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 9pt; page-break-inside: avoid; }
th { background: #0f3d5c; color: #fff; text-align: left; padding: 4px 6px; }
td { border-bottom: 1px solid #d6dde3; padding: 3px 6px; vertical-align: top; }
tr:nth-child(even) td { background: #f4f7f9; }
figure { margin: 10px 0 14px; text-align: center; page-break-inside: avoid; }
figure img { max-width: 100%; border: 1px solid #e3e8ec; }
figcaption { font-size: 8.5pt; color: #5b6b78; margin-top: 3px; }
pre { background: #f4f7f9; border-left: 3px solid #2a9d8f; padding: 7px 9px; font-size: 8.2pt; overflow-x: auto; page-break-inside: avoid; white-space: pre-wrap; }
code { font-family: Consolas, monospace; }
.pagebreak { page-break-after: always; }
"""
report_html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>NovaFin Capstone Report</title><style>{REPORT_CSS}</style></head><body>{''.join(R)}</body></html>"""
(OUT / "NovaFin_Capstone_Report.html").write_text(report_html, encoding="utf-8")

# ------------------------------------------------------------------------------------------------------------------
# 2. BOARD DECK (slides + speaker notes)
# ------------------------------------------------------------------------------------------------------------------
SLIDES = [
 dict(title="NovaFin: deploying ₹1,000 crore with ML", kicker="Board presentation · draft for review",
      body="""<p class="big">Recommendation: grow where evidence is strongest, earn steadily, protect the group.</p>
<div class="kpis"><div><b>16.5%</b><span>expected return a year (₹165 cr)</span></div><div><b>₹116 cr</b><span>stress loss (limit ₹150 cr)</span></div>
<div><b>+₹49 cr</b><span>earned even if every stress hits at once</span></div><div><b>₹175 cr</b><span>liquidity reserve</span></div></div>""",
      notes="Open with the answer. The Board asked one question: where to put ₹1,000 crore and how to control the risks. "
            "Our answer earns about 16.5% a year, keeps the worst-case loss inside the 15% appetite, and keeps enough cash to survive a funding freeze. "
            "Everything that follows explains where these numbers come from."),
 dict(title="The answer: where the ₹1,000 crore goes", kicker="Recommended allocation",
      body=img("Module_09_Integrated_Allocation/allocation.png", width="92%"),
      notes="Left chart: the split by Board category. Equity ₹250 cr, wealth ₹221 cr, liquidity reserve ₹175 cr, digital ₹163 cr, corporate ₹120 cr, retail ₹41 cr, hedging ₹20 cr, HFT ₹10 cr. "
            "Right chart: every candidate's return against what it could lose in a stress. Green bubbles are funded. "
            "We funded the candidates that earn the most per rupee at risk, within the limits."),
 dict(title="How we built it: one chain for every module", kicker="Method",
      body="""<div class="chain"><span>Data</span>→<span>ML prediction</span>→<span>Financial metric</span>→<span>Risk assessment</span>→<span>Business decision</span></div>
<table><tr><th>Principle</th><th>What we did</th></tr>
<tr><td>Validation matches real use</td><td>Time splits for transactions and markets, trading-day split for HFT, repeated CV for small data</td></tr>
<tr><td>No leakage</td><td>Future columns, CLV and the supplied option price kept out of the features</td></tr>
<tr><td>Simplest model wins</td><td>At least 3 models per task; a complex model must clearly beat the simple one</td></tr>
<tr><td>Explainable</td><td>SHAP or coefficients for every chosen model</td></tr>
<tr><td>Decisions in rupees</td><td>Every model is turned into NPV, ECL, cost, CLV, Sharpe or VaR</td></tr></table>""",
      notes="The Board wanted an integrated answer, not a pile of models. Every module follows the same five steps. "
            "Validation always mimics how the model would really be used: we never let a model see the future. "
            "And we always prefer the simple, explainable model unless a complex one is clearly better."),
 dict(title="Module 1: which strategic initiatives to fund", kicker="Corporate finance",
      body="""<div class="two"><div><table><tr><th>Model (CV AUC)</th><th>AUC</th></tr><tr><td><b>Logistic, 3 drivers ✔</b></td><td><b>0.63</b></td></tr>
<tr><td>Logistic, all features</td><td>0.56</td></tr><tr><td>Gradient boosting</td><td>0.50</td></tr><tr><td>Random forest</td><td>0.45</td></tr></table>
<ul><li>Low risk rating is the strongest success driver (89% vs ~70%)</li><li>Expected NPV with a loss on failure; rank by PI</li>
<li><b>Fund 21 · Review 18 · Reject 141</b></li><li>Realised success in Fund group: 86%</li></ul></div>
<div>""" + img("Module_01_Strategic_Initiatives/init_decision.png") + "</div></div>",
      notes="180 initiatives. Success is only weakly predictable: the best model has an AUC of 0.63. With only 42 failures, the complex models overfit, so the small logistic model wins. "
            "The finance does most of the work: expected NPV over a 5-year life, with a loss if the project fails. "
            "Key judgement to flag: project life. Over 3 years almost nothing pays back."),
 dict(title="Module 2: credit, approve only what pays", kicker="Credit risk",
      body="""<div class="two"><div><table><tr><th>Model</th><th>CV AUC</th></tr><tr><td><b>Logistic ✔</b></td><td><b>0.729</b></td></tr><tr><td>Random forest</td><td>0.706</td></tr><tr><td>Gradient boosting</td><td>0.702</td></tr></table>
<ul><li>Calibrated PDs; default 7% (band A) → 47% (band D)</li><li>Whole book ECL ₹63 cr (9.8%); 2/3 of loans lose value</li>
<li><b>Approve 836</b> (₹68 cr, ECL 2.8%) · Review 815 · Reject 3,349</li><li>Margin is thin: PD ×1.5 breaks the 3% appetite</li></ul></div>
<div>""" + img("Module_02_Credit_Risk/credit_bands.png") + "</div></div>",
      notes="Credit is where ML is most useful. The logistic model ranks borrowers well and its probabilities are believable, which matters because PD multiplies straight into expected loss. "
            "The current book is mispriced: two thirds of loans destroy value. We approve only low-PD, positive-value loans, which keeps expected loss at 2.8%, inside appetite. "
            "Lending gets capital only for that approved segment."),
 dict(title="Module 3: fraud, 38% lower cost", kicker="Fraud detection",
      body="""<div class="two"><div><table><tr><th>Method (test)</th><th>Cost ₹ lakh</th><th>Saving</th></tr>
<tr><td><b>Random forest ✔</b></td><td><b>8.98</b></td><td><b>38%</b></td></tr><tr><td>Gradient boosting</td><td>9.10</td><td>37%</td></tr>
<tr><td>Amount-ratio rule</td><td>10.48</td><td>27%</td></tr><tr><td>Isolation Forest</td><td>14.31</td><td>1%</td></tr><tr><td>No model</td><td>14.40</td><td>0%</td></tr></table>
<ul><li>Fraud = amount far above the customer's normal (5×)</li><li>Investigate 7.5% of transactions, catch 51% of fraud</li><li>Saving holds at 20–50% under stress</li></ul></div>
<div>""" + img("Module_03_Fraud_Detection/fraud_cost_curve.png") + "</div></div>",
      notes="A missed fraud costs ₹10,000, a false alarm ₹500, so the best threshold is low. We chose it on one period and tested it on a later, untouched period. "
            "The random forest cuts operating cost by 38%. The anomaly detector, which does not use the fraud labels, barely helps: unusual is not the same as fraudulent. "
            "This needs analysts and systems, not balance-sheet capital."),
 dict(title="Module 4: churn and customer value", kicker="Customer analytics",
      body="""<ul class="big-list"><li><b>Churn is not predictable</b> from the customer data: every model scores AUC ≈ 0.5</li>
<li>The supplied CLV is a <b>one-year margin</b>: 4% income + 3% deposits + 1.2% loans + 1.8% investments − ₹5,000 per complaint</li>
<li>Lifetime value ₹174 cr; the top 20% of customers hold 42%</li>
<li>Rank the 1,000 calls by <b>churn probability × CLV</b>: reaches 3× more value than a random list</li>
<li>Campaign nets <b>₹22.8 lakh</b> (ROI 152%); RM capacity is the limit</li></ul>""" + img("Module_04_Churn_CLV/churn_clv.png", width="62%"),
      notes="An honest negative result: no model can predict churn from these variables. Pretending otherwise would mislead the relationship managers. "
            "So we target by value: churn hits rich and ordinary customers alike, so calling the most valuable customers protects the most money. "
            "Retention is cheap operating spend, not a capital line."),
 dict(title="Modules 5–6: equity, diversify first", kicker="Equity and portfolio",
      body="""<div class="two"><div><table><tr><th>Strategy</th><th>Return</th><th>Sharpe</th></tr>
<tr><td>ML tilt</td><td>18.2%</td><td>1.43 (n.s.)</td></tr><tr><td>ML mean-variance</td><td>23.0%</td><td>1.38 (n.s.)</td></tr>
<tr><td><b>Equal-weight ✔</b></td><td><b>16.1%</b></td><td><b>1.30</b></td></tr><tr><td>Markowitz max-Sharpe</td><td>8.4%</td><td>0.15</td></tr></table>
<ul><li>Best stock-ranking signal IC 0.056, not significant</li><li>Markowitz chases past winners and fails</li><li>Crisis: monthly VaR 5% → 30%</li></ul></div>
<div>""" + img("Module_06_Portfolio_Optimisation/portfolio_backtest.png") + "</div></div>",
      notes="Can ML pick winning stocks? Not reliably. The best signal is weak and not statistically significant over 38 months. "
            "The classic Markowitz optimiser does worst, because it puts too much weight on last year's winners. "
            "We hold an equal-weight sleeve and watch the ML tilt as a paper portfolio before trusting it. We plan on 13.3%, not the flattering 16% backtest."),
 dict(title="Module 7: HFT, strong signal, fragile profit", kicker="High-frequency trading",
      body="""<div class="two"><div><ul><li>Order-book imbalance predicts the next 100 ms move (corr 0.51); 3 models tie at macro-F1 0.44</li>
<li>Base case: ₹6.3 lakh a day on test days</li><li><b>Costs ×2 → −₹0.8 lakh/day · 1-event delay → −₹1.1 lakh/day</b></li>
<li>Robust use: <b>execution timing</b>, about 7 bp better per order</li><li>Decision: ₹10 cr pilot with a kill switch</li></ul></div>
<div>""" + img("Module_07_HFT/hft_pnl.png") + "</div></div>",
      notes="The signal is real, but the profit disappears as soon as costs double or we react one step late. That is why HFT gets only a small pilot with a hard stop-loss. "
            "The durable value is using the same signal to time our large client orders better."),
 dict(title="Module 8: derivatives, theory wins, hedge the book", kicker="Derivatives",
      body="""<div class="two"><div><table><tr><th>Pricing (test RMSE)</th><th>₹</th></tr><tr><td><b>Black-Scholes</b></td><td><b>9.48</b></td></tr>
<tr><td>BS + ML correction</td><td>10.32</td></tr><tr><td>Gradient boosting</td><td>12.74</td></tr><tr><td>Random forest</td><td>14.64</td></tr></table>
<ul><li>Delta hedge cuts 1-day VaR by 80% (₹0.28 → ₹0.06 cr)</li><li>Volatility spike still costs ₹5.4 cr → vega limit</li><li>Hedging buffer ₹20 cr</li></ul></div>
<div>""" + img("Module_08_Derivatives/options_var.png") + "</div></div>",
      notes="ML did not beat the Black-Scholes formula: market prices are the theory plus noise, so there is nothing extra to learn. We keep the theory for pricing and hedging. "
            "Delta hedging removes most day-to-day risk. What remains is volatility risk: if volatility jumps, the options we sold get dearer. That needs a separate limit and a buffer."),
 dict(title="Liquidity: survive a funding freeze", kicker="Liquidity reserve",
      body="""<div class="two"><div><table><tr><th>30-day stress (99%)</th><th>Shortfall</th><th>Survival</th></tr>
<tr><td>Wholesale freeze</td><td>₹85 cr</td><td>23 days</td></tr><tr><td><b>Freeze + 10% deposit run</b></td><td><b>₹172 cr</b></td><td>15 days</td></tr>
<tr><td>Severe: + 20% run</td><td>₹259 cr</td><td>11 days</td></tr></table>
<ul><li>Daily net outflow (₹4.9 cr) is funded by wholesale money (₹5.0 cr)</li><li>Forecasts cannot replace a reserve (gap is noise)</li><li><b>Reserve ₹175 cr</b></li></ul></div>
<div>""" + img("Extra_Liquidity_Reserve/liquidity_stress.png") + "</div></div>",
      notes="NovaFin relies on wholesale funding every day. If that freezes and 10% of deposits leave, today's buffer lasts about 15 days. "
            "We hold ₹175 crore extra in cash and government securities, following the logic of the regulatory LCR."),
 dict(title="Why this allocation beats the alternatives", kicker="Decision framework",
      body="""<table><tr><th>Allocation</th><th>Expected return</th><th>Stress loss</th><th>Meets all limits?</th></tr>
<tr><td>Return-chasing</td><td>22.0%</td><td>8.5%</td><td>No: no reserve, ₹971 cr in initiatives</td></tr>
<tr><td><b>Recommended</b></td><td><b>16.5%</b></td><td><b>11.6%</b></td><td><b>Yes</b></td></tr>
<tr><td>Equal split</td><td>12.3%</td><td>8.2%</td><td>Yes</td></tr><tr><td>All liquid</td><td>6.5%</td><td>0%</td><td>Yes</td></tr></table>
<p><b>Rule:</b> mandatory lines first, then fund by (return − 7%) ÷ stress loss within the limits (reserve ≥ ₹175 cr, each category ≤ 30%, initiatives ≤ 50%, equity ≤ 25%, stress loss ≤ 15%).</p>
<p><b>Robust:</b> unchanged if initiatives earn 10 pts less, equity 5 pts less or lending 4 pts less. In a combined crisis year: +₹49 cr.</p>""",
      notes="Return-chasing earns more only by betting almost everything on initiatives ranked by our weakest model, with no cash reserve. That fails the risk appetite. "
            "Our allocation earns far more than an equal split or parking the money, and it survives every sensitivity and a combined crisis."),
 dict(title="Risks and how we control them", kicker="Controls and governance",
      body="""<table><tr><th>Risk</th><th>Control</th><th>Trigger</th></tr>
<tr><td>Credit</td><td>Approve PD &lt; 0.11 only; reprice review queue</td><td>Approved ECL &gt; 3%</td></tr>
<tr><td>Initiatives</td><td>Stage-gated tranches</td><td>2 quarters behind plan → stop</td></tr>
<tr><td>Equity</td><td>Equal-weight, 25% cap</td><td>Drawdown &gt; 10% → halve</td></tr>
<tr><td>Derivatives</td><td>Daily delta hedge, vega limit, ₹20 cr buffer</td><td>Volatility exposure over limit → buy protection</td></tr>
<tr><td>HFT</td><td>₹10 cr pilot, kill switch</td><td>Loss &gt; ₹0.5 cr/day or ₹2 cr total</td></tr>
<tr><td>Liquidity</td><td>₹175 cr reserve</td><td>Coverage &lt; 110% → stop wholesale-funded growth</td></tr>
<tr><td>Model risk</td><td>Inventory, annual validation, SHAP on file</td><td>Drift alarm → revalidate</td></tr></table>""",
      notes="Every risk has a control, a trigger and an owner. Every model has a monitoring metric and a retraining trigger, and every decision can be explained with SHAP."),
 dict(title="Where ML paid off, and where it did not", kicker="Honest scorecard",
      body="""<table><tr><th>Module</th><th>ML verdict</th><th>Business use</th></tr>
<tr><td>Credit</td><td class="good">Useful: AUC 0.75, calibrated</td><td>approve / reject with ECL control</td></tr>
<tr><td>Fraud</td><td class="good">Useful: PR-AUC 6× random</td><td>38% lower fraud cost</td></tr>
<tr><td>HFT</td><td class="mid">Strong signal, fragile profit</td><td>execution timing</td></tr>
<tr><td>Initiatives</td><td class="mid">Weak: AUC 0.63</td><td>risk adjustment on NPV</td></tr>
<tr><td>Equity</td><td class="bad">Not significant</td><td>stay diversified</td></tr>
<tr><td>Churn</td><td class="bad">No signal</td><td>value-led targeting</td></tr>
<tr><td>Options</td><td class="bad">Below Black-Scholes</td><td>keep the theory</td></tr></table>
<p class="big">ML adds value where there is real signal and a clear cost function. Elsewhere, simpler models and sound finance win.</p>""",
      notes="We are deliberately honest about where ML did not help. That is part of good model governance: complexity is only worth paying for when it earns its keep."),
 dict(title="Decisions requested and next 90 days", kicker="Next steps",
      body="""<ol class="big-list"><li>Approve the ₹1,000 crore allocation and the risk-appetite limits</li>
<li>Fund the liquidity reserve and the hedging buffer <b>before</b> growth capital is drawn</li>
<li>Release tranche 1 of the five initiatives with stage-gate KPIs</li>
<li>Put the fraud model live; start the 1,000-customer RM campaign</li>
<li>Launch the equal-weight equity sleeve; run the ML tilt as a paper portfolio</li>
<li>Set up model governance: inventory, validation, monitoring dashboards</li></ol>
<p class="small">Limitations: synthetic data; small samples (180 initiatives, 4 HFT test days); key assumptions (5-year project life, units, run-off rates) are stated and stress-tested.</p>""",
      notes="Close with the asks. Liquidity and hedging come first, then growth. Mention the limitations openly: synthetic data and a few judgement calls, all stress-tested."),
]

DECK_CSS = """
:root { --ink:#1d2a35; --navy:#0f3d5c; --teal:#2a9d8f; --muted:#5b6b78; --line:#d6dde3; --bg:#ffffff; --paper:#eef2f5; }
* { box-sizing: border-box; }
body { margin:0; font-family:'Segoe UI', Arial, sans-serif; color:var(--ink); background:var(--paper); }
.slide { width:13.333in; height:7.5in; background:var(--bg); padding:0.45in 0.6in; position:relative; overflow:hidden; page-break-after:always; margin:0 auto; }
.slide .kicker { color:var(--teal); font-weight:600; font-size:13pt; text-transform:uppercase; letter-spacing:.06em; }
.slide h1 { color:var(--navy); font-size:28pt; margin:4px 0 14px; border-bottom:3px solid var(--teal); padding-bottom:6px; }
.slide .num { position:absolute; right:0.5in; bottom:0.25in; color:var(--muted); font-size:10pt; }
.slide table { border-collapse:collapse; width:100%; font-size:12.5pt; margin:4px 0 10px; }
.slide th { background:var(--navy); color:#fff; text-align:left; padding:5px 8px; }
.slide td { border-bottom:1px solid var(--line); padding:4px 8px; }
.slide ul, .slide ol { font-size:14pt; line-height:1.45; padding-left:22px; margin:6px 0; }
.slide .big-list { font-size:16pt; }
.slide .two { display:grid; grid-template-columns: 1fr 1.15fr; gap:24px; align-items:start; }
.slide figure { margin:0; text-align:center; } .slide figure img { max-width:100%; max-height:5.3in; object-fit:contain; }
.slide .big { font-size:20pt; color:var(--navy); }
.slide .small { font-size:11pt; color:var(--muted); }
.kpis { display:grid; grid-template-columns:repeat(4,1fr); gap:18px; margin-top:28px; }
.kpis div { border:1px solid var(--line); border-top:5px solid var(--teal); padding:16px; border-radius:6px; }
.kpis b { display:block; font-size:30pt; color:var(--navy); } .kpis span { font-size:12.5pt; color:var(--muted); }
.chain { display:flex; gap:10px; align-items:center; font-size:15pt; color:var(--muted); margin:10px 0 18px; flex-wrap:wrap; }
.chain span { background:var(--navy); color:#fff; padding:8px 14px; border-radius:6px; font-weight:600; }
td.good { color:#1f7a55; font-weight:600; } td.mid { color:#9a6b00; font-weight:600; } td.bad { color:#b23a2b; font-weight:600; }
.notes { width:13.333in; margin:0 auto 28px; background:#fff8e6; border-left:5px solid #e9c46a; padding:12px 18px; font-size:12.5pt; line-height:1.5; }
.notes b { color:#7a5a00; }
@page { size: 13.333in 7.5in; margin:0; }
@media print { body { background:#fff; } .notes { display:none; } .slide { margin:0; } }
@media screen { .slide { margin:24px auto 6px; box-shadow:0 2px 10px rgba(0,0,0,.12); } }
"""
def deck(with_notes):
    parts = []
    for i, s in enumerate(SLIDES, 1):
        parts.append(f'<section class="slide"><div class="kicker">{s["kicker"]}</div><h1>{s["title"]}</h1>{s["body"]}<div class="num">NovaFin · {i}/{len(SLIDES)}</div></section>')
        if with_notes:
            parts.append(f'<div class="notes"><b>What to say (slide {i}):</b> {s["notes"]}</div>')
    title = "NovaFin Board Deck" + (" with Notes" if with_notes else "")
    intro = ('<div class="notes" style="margin-top:24px"><b>How to use this page:</b> each slide is followed by speaker notes '
             'explaining what it shows and what to say. Print or PDF uses the slides only.</div>') if with_notes else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><style>{DECK_CSS}</style></head><body>{intro}{''.join(parts)}</body></html>"""

(OUT / "NovaFin_Board_Presentation_with_notes.html").write_text(deck(True), encoding="utf-8")
(OUT / "_deck_slides_only.html").write_text(deck(False), encoding="utf-8")

# ------------------------------------------------------------------------------------------------------------------
# 3. PDFs via headless Chrome
# ------------------------------------------------------------------------------------------------------------------
def to_pdf(html_name, pdf_name):
    src = (OUT / html_name).resolve().as_uri()
    tmp = (OUT / ("_tmp_" + pdf_name)).resolve()                       # print to a temp file first
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    f"--print-to-pdf={tmp}", src], capture_output=True, text=True, timeout=180)
    try:
        tmp.replace(OUT / pdf_name)                                    # fails if the PDF is open in a viewer
        print(pdf_name, "updated")
    except PermissionError:
        print(pdf_name, "NOT updated: close the PDF in your viewer and run again (new copy left as", tmp.name + ")")

to_pdf("NovaFin_Capstone_Report.html", "NovaFin_Capstone_Report.pdf")
to_pdf("_deck_slides_only.html", "NovaFin_Board_Presentation_DRAFT.pdf")
(OUT / "_deck_slides_only.html").unlink()
print("done:", [p.name for p in OUT.iterdir()])

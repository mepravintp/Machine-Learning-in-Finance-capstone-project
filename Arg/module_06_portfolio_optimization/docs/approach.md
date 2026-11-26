# Module 6 — Approach

**The chain:** Module 5's ridge forecasts → **Part A: weights for each strategy, monthly backtest with costs, measures** → **Part B: VaR and stress tests** → Module 9 ("Equity investments").

| Stage | Decisions | Status |
| --- | --- | --- |
| Setup | M6-01 monthly, M6-03 window and 261-day year, M6-04 cost, M6-05 risk-free, M6-07 layout, M6-09 test period, M6-10 measures | Agreed 22 Nov 2026 |
| Part A | M6-02 maximum Sharpe, M6-08 ML portfolio | Agreed; built 22 Nov 2026 |
| Part B | M6-06 VaR and stress tests | Agreed; built 22 Nov 2026 |

## Data

- `data/nova_market_data.csv` (same as Module 5): 15 stocks, 29 Jan 2021 – 31 Aug 2026; every weekday, no holidays (261 rows a year).
- `Interest_Rate` and `VIX` are random (15 values per date; Module 5), so the risk-free rate is a fixed 6.8% and stress tests don't use VIX or beta.
- Module 5's `outputs/task1/FINAL_M5_T1_return_predictions.csv`: ridge regression's walk-forward forecasts (M5-15).

## Part A — Three portfolios, backtested (built)

**Strategies** (reset each month-end):
- **Equal weight:** 1 ÷ 15 each.
- **Markowitz (past returns):** maximum Sharpe; μ = past 261 days' average × 21.75; Σ = past 261 days' covariance (Ledoit–Wolf) × 21.75; long-only, ≤ 25% per stock; risk-free 6.8%.
- **ML (ridge forecasts):** same, with μ = ridge's next-month forecast.
- **Top 5 (Module 5):** ridge's top 5 at 20% each.

```text
Maximise (w·μ − risk-free) ÷ √(w·Σ·w)   subject to: weights add to 1, each 0–25%
Turnover = Σ |target − drifted weight|;   cost = 0.15% × turnover on the rebalance day
Daily return = value-weighted average of the stocks' returns (weights drift between resets)
```

**Measures:** CAGR, volatility, Sharpe, Sortino, maximum drawdown, Calmar, VaR, CVaR, turnover, tracking error, information ratio; p = t-test of the 43 monthly differences from equal weight, line 0.05 ÷ 3 = 0.017. Checks: cost 0%, 0.10%, 0.30%; risk-free 0%.

**Result:** equal weight has the best Sharpe (1.06), drawdown (−4.2%) and cost (7% traded a month). Markowitz 16.6% vs 15.6% CAGR but Sharpe 0.80, p 0.79. ML worst: 10.6%, Sharpe 0.36, 90% traded a month. Minimum-risk Markowitz = equal weight exactly.

## Part B — VaR and stress tests (built)

- **VaR 95% and CVaR**, 1 day and 1 month (22 trading days), historical (actual days; overlapping 22-day runs for a month) and parametric (bell curve: −(average − 1.645 × sd); a month scales the sd by √22), in ₹ per ₹100 crore, for all four strategies.
- **Bell-curve fit:** share of days worse than the parametric VaR (5% expected).
- **Stress tests:** (a) each strategy's worst day, holding month and 20-day run; (b) every stock −20% (and a beta-scaled version, betas against the equal-weight portfolio); (c) swing and VaR recomputed with every correlation set to 0.4, each stock's own swing kept, averaged over the 43 months' weights.
- **Result:** equal weight lowest on every measure (1-day VaR ₹0.76 crore, 1-month ₹1.98 crore, worst month ₹3.76 crore). Every stock −20% = ₹20 crore for all. With correlation 0.4, equal weight's swing 7.8% → 19.4% (×2.5); all four 19.4%–21.1%; 1-month VaR ₹8.00–8.95 crore.

## Hand-offs

| From | File | What it holds | How the next step must treat it |
| --- | --- | --- | --- |
| Module 5 | `module_05_equity_markets/outputs/task1/FINAL_M5_T1_return_predictions.csv` | Ridge's forecasts | Expected returns for the ML portfolio; no proven skill |
| Part A | `outputs/partA/daily_returns.csv` | Each strategy's daily return after costs (934 days) | Part B's VaR and stress tests; Module 9 |
| Part A | `outputs/partA/FINAL_M6_A_portfolio_weights.csv` | Weights per strategy, month, stock, with the expected return used | The ML portfolio as an actual portfolio (the brief); Part B stress test (c) |
| Part B | `outputs/partB/FINAL_M6_B_risk_summary.csv` | VaR, CVaR and stress losses per strategy, ₹ per ₹100 crore | Evidence |
| **Modules 5 + 6 → Module 9** | **`outputs/FINAL_M6_module_output.xlsx` (Hand-off tab)** | 16 figures: portfolio, return (and its 95% range), risk at real-market correlation, VaR, CVaR, crash loss, ML's extra return (0) and cost, assumptions; each with status, source, decision and use (M6-11, M6-12) | **The final equity hand-off**; use the real-market risk figures |

## Shared code

- `helpers/m06_metrics.py`: all measures (also for Part B and Module 9). `helpers/m06_style.py`: chart style.
- Module 5's `helpers/m05_data.py`: loading and month-end dates.

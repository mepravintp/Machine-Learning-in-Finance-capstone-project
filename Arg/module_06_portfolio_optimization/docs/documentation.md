# Module 6 — Portfolio Optimization

## 1. What the brief says (verbatim)

> **Module 6 — Portfolio Optimization**
> Dataset: nova_market_data.csv (same dataset as Module 5)
> One must transform ML predictions into an actual portfolio. Compare strategies- Equal-weight portfolio, Traditional Markowitz portfolio, ML-predicted-return portfolio. Perform backtesting to demonstrate performance and generate performance metrics.

Related learning objectives (brief section 3) not listed in any module's tasks, which we cover here: "Conduct stress testing", "Calculate VaR". Also "Evaluate investment strategies", "Conduct backtesting", "Construct portfolios".

## 2. The task in plain words

A portfolio = the set of investments held and how much of each (weights adding to 100%). Module 5 forecast returns; here we turn forecasts into real holdings and test them.

- **Equal-weight portfolio** — same amount in every stock (15 stocks → 6.67% each). Simple benchmark.
- **Traditional Markowitz portfolio** — choose weights that give the best return for the risk taken, using past average returns and covariance (how much two stocks move together). Holding stocks that do not move together lowers total risk; this is diversification.
- **ML-predicted-return portfolio** — the same Markowitz method, but using Module 5's ML forecasts instead of past averages.
- **Backtesting** — replay each strategy month by month over past data, using only information available at each date, as if we had really traded.
- **Performance metrics** — numbers that compare the strategies (defined in approach.md): annual return, volatility (how much returns swing), Sharpe ratio (return per unit of risk), maximum drawdown (worst fall from a peak), VaR (Value at Risk = loss not exceeded on 95% of days), turnover (how much we trade).

## 3. Data

Same as Module 5: data/nova_market_data.csv, 15 stocks, daily, 29 Jan 2021 – 31 Aug 2026; every weekday, no holidays (261 rows a year). Uses Module 5's `outputs/task1/FINAL_M5_T1_return_predictions.csv` (ridge regression, decision M5-15) for the ML portfolio. Checked 22 Nov 2026: `Interest_Rate` and `VIX` are random (15 values per date), so neither is used as a risk-free rate or for stress tests.

## 4. Required outputs (from the brief)

- [x] ML predictions transformed into an actual portfolio (`outputs/partA/FINAL_M6_A_portfolio_weights.csv`)
- [x] Three strategies compared: equal-weight, traditional Markowitz, ML-predicted-return (plus Module 5's top 5)
- [x] Backtest of all three (43 test months, 0.15% costs)
- [x] Performance metrics table and charts (`strategy_comparison.csv`, 2 charts)
- [x] (Learning objectives) VaR and stress tests, for all four strategies (`outputs/partB/FINAL_M6_B_risk_summary.csv`)

## 5. Learning objectives shown here

Construct portfolios · Evaluate investment strategies · Conduct backtesting · Conduct stress testing · Calculate VaR · Validation · Business recommendations.

## 6. Link to other modules

Input: Module 5 forecasts (ridge regression, M5-15). Output: **`outputs/FINAL_M6_module_output.xlsx` (Hand-off tab)** (Modules 5 and 6 combined: equal weight's return, its range, real-market risk, VaR, CVaR, crash loss, ML's extra return of 0) → "Equity investments" in Module 9; the 20% crash loss → hedging (Module 8).

## 7. Results

**Part A — Three portfolios, backtested (built).** 43 test months (31 Jan 2023 – 31 Aug 2026), after 0.15% costs:

| Strategy | CAGR | Volatility | Sharpe | Max drawdown | Turnover a month | p vs equal weight |
| --- | --- | --- | --- | --- | --- | --- |
| Equal weight | 15.6% | 7.8% | 1.06 | −4.2% | 7% | — |
| Markowitz (past returns) | 16.6% | 11.8% | 0.80 | −12.1% | 33% | 0.79 |
| ML (ridge forecasts) | 10.6% | 11.6% | 0.36 | −14.9% | 90% | 0.39 |
| Top 5 (Module 5) | 13.2% | 13.3% | 0.51 | −17.0% | 99% | 0.81 |

- Equal weight best on every risk-adjusted measure; no strategy beats it beyond luck (line 0.017); the order holds at costs 0%–0.30% and risk-free 0%.
- ₹100 crore → ₹168.0 crore (equal weight); Markowitz +₹5.2 crore with a ₹12.1 crore worst fall; ML −₹24.6 crore.
- Minimum-risk Markowitz = equal weight exactly (alike, independent stocks).
- Details: `reports/partA_report.md`.

**Part B — VaR and stress tests (built).** ₹ crore lost on ₹100 crore, 95% level:

| Strategy | VaR 1 day | CVaR 1 day | VaR 1 month | Worst month | Every stock −20% | VaR 1 month, real-market correlation |
| --- | --- | --- | --- | --- | --- | --- |
| Equal weight | 0.76 | 0.98 | 1.98 | 3.76 | 20.0 | 8.00 |
| Markowitz (past returns) | 1.18 | 1.48 | 4.05 | 6.15 | 20.0 | 8.43 |
| ML (ridge forecasts) | 1.16 | 1.44 | 4.14 | 7.67 | 20.0 | 8.84 |
| Top 5 (Module 5) | 1.29 | 1.62 | 5.59 | 7.55 | 20.0 | 8.95 |

- The bell curve fits this data (4.9%–5.6% of days breach the parametric VaR; worst day about 3 sd), unlike real markets' fat tails.
- With real-market correlation (0.4), equal weight's yearly swing rises from 7.8% to 19.4%; all four strategies end up at 19.4%–21.1%.
- Details: `reports/partB_report.md`.

## 8. Risks and limitations

- Markowitz weights are very sensitive to estimated returns; we cap weights and shrink estimates.
- Backtest of about 43 out-of-sample months: performance differences may be luck; we report confidence ranges.
- Transaction costs are assumed (0.15% per side, proposed), not given.
- The data's stocks move independently (correlation 0.004), so measured risk understates real-market risk; stress test (c) shows by how much (equal weight's swing ×2.5).
- Returns follow a bell curve here; real markets have fat tails, so real VaR would be larger still.

## 9. Concepts explained (for study)

### 9.1 Performance measures used

| Measure | What it is | Formula | Good is |
| --- | --- | --- | --- |
| CAGR | Steady yearly growth rate from start to end value | (end ÷ start) ^ (1 ÷ years) − 1 | Higher |
| Volatility | How much returns swing a year | daily sd × √261 (this data's year) | Lower |
| Sharpe ratio | Return above a safe bond per unit of risk | (annual return − 6.8%) ÷ volatility | Higher (above 1 good) |
| Sortino ratio | Sharpe using only downside swings | (annual return − 6.8%) ÷ downside volatility | Higher |
| Maximum drawdown | Worst fall from a previous high | min(value ÷ running high − 1) | Closer to 0 |
| Calmar ratio | Return per unit of worst fall | CAGR ÷ size of the max drawdown | Higher |
| Turnover | How much is traded per rebalance | sum of the size of each weight change (new − old) | Lower |
| Tracking error | How far returns wander from equal weight | sd of daily (strategy − equal weight) × √261 | — |
| Information ratio | Extra return over equal weight per unit of tracking error | excess a year ÷ tracking error | Higher (0.5 good) |
| VaR 95% | Loss not exceeded on 95% of days | 5th percentile of daily returns (historical); −(mean − 1.645 × sd) (parametric) | Smaller |
| CVaR 95% | Average loss on the worst 5% of days | mean of returns below VaR | Smaller |

### 9.2 Measures not used, and why

| Measure | What it is | Why not |
| --- | --- | --- |
| Beta | Move of an investment per 1% market move: cov(investment, market) ÷ var(market) | Needs a real market index; `Market_Return` isn't one (−0.016 with the stocks' average). Against the equal-weight portfolio every stock's beta is about 1 |
| Alpha (Jensen's) | Return beyond what market exposure explains: actual − [risk-free + beta × (market − risk-free)] | Needs beta and a market; excess return and information ratio vs equal weight play its role |
| Treynor ratio | (return − risk-free) ÷ beta | Needs beta |
| R-squared, up/down capture | Share of swings explained by the market; share of market rises/falls caught | Need a real market |
| Omega ratio, Ulcer index | Gains vs losses around a target; drawdown depth × length | Add little: returns are near bell-curve (skew 0.14) and drawdowns are covered by max drawdown and Calmar |
| Fama–French factor alpha | Alpha after size, value, momentum factors | No size, valuation or factor data |

### 9.3 Other concepts

- **Markowitz (1952):** choose weights from expected returns (μ) and co-movement (Σ). Portfolio risk = √(wᵀΣw). Maximum Sharpe picks the weights with the most return per unit of risk. It wins when stocks differ in risk or move in groups and when expected returns can be estimated; here stocks are alike and independent and returns unpredictable, so equal weight is as good or better (as found on real data by DeMiguel, Garlappi and Uppal, 2009).
- **261 vs 252 days:** 252 is the US convention (after holidays; India about 248). This data has every weekday (261 a year), so 261 keeps yearly figures in line with the calendar.
- **Test (out-of-sample) months:** the 43 months from Jan 2023 are each predicted or estimated using only earlier data, then scored. The first 24 months (2021–2022) are training only.
- **The 0.05 line:** the usual accepted chance (1 in 20) of being fooled by luck (Fisher's convention). With several tests, divide by their number (Bonferroni): 0.05 ÷ 3 ≈ 0.017 for three strategy comparisons.
- **VIX:** the "fear index", the market's expected 30-day swing from index option prices; 10–20 calm, 30+ panic. A VIX stress test replays the highest-fear period. Not usable here: VIX is random in this data.
- **Beta stress test:** market falls X% → each stock falls X% × its beta. Not usable here: no real market; it reduces to "every stock falls X%".
- **Indian trading costs (approx.):** STT 0.1% on buy and sell; stamp duty 0.015% on buys; exchange charge about 0.003%; GST on charges; brokerage 0 for retail delivery, about 0.02%–0.05% for institutions; market impact for large orders. About 0.11% per side retail, about 0.15% institutional.

## Module 9 inputs (22 Nov 2026)

| Category | Return per ₹ (% a year) | Range | Bad year per ₹ | Bad year means | Capacity | Gap / assumption |
| --- | --- | --- | --- | --- | --- | --- |
| Equity investments (equal weight, 15 stocks) | 15.6 | 8.6 to 22.6 (95% range of the measured return) | -16.24 | 1-in-20 year at the real-market swing (19.4%): return − 1.645 × swing; a crash (all stocks −20%) loses 20% | Large (listed stocks) | Stocks in the data move independently, so measured risk understates the real one; no dividends |

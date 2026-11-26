# Module 5 — Equity Markets: ML-Driven Investment Strategy

## 1. What the brief says (verbatim)

> **Business problem**
> NovaFin manages an equity portfolio.
> The investment committee wants to know:
> **Can ML identify stocks with superior future returns?**
>
> **Dataset:** nova_market_data.csv
>
> Variables: Ticker · Date · Open · High · Low · Close · Volume · Sector · Market_Return · GDP_Growth · Interest_Rate · VIX · Momentum_20D · Volatility_20D · Return
>
> **Task 1 — predict future returns by various models**
>
> **Task 2 — Stock ranking**
> For every rebalance date (assumed):
> 1. Predict future returns
> 2. Rank stocks
> 3. Select top-ranked stocks
> 4. Construct portfolio

## 2. The task in plain words

An equity portfolio = a set of shares (part-ownerships of companies) NovaFin holds. The investment committee asks whether ML can pick the shares that will rise more than others.

- **Task 1 — forecast returns.** Return = % change in price (₹100 → ₹103 = 3%). Train several regression models (models that predict a number) to forecast each stock's future return, using only information known today.
- **Task 2 — rank and pick.** A rebalance date is a day on which we reset what we hold; the brief lets us choose ("assumed"), and we use month-ends. On each one: forecast every stock's return for the next month, rank the 15 stocks, buy the top-ranked ones, and hold until the next rebalance.

Example: on 31 March the model forecasts April returns of +3% for INFY, +2.5% for TCS, −1% for RELIANCE → buy INFY and TCS for April.

## 3. Data

| Item | Value |
| --- | --- |
| File | data/nova_market_data.csv |
| Rows | 21,855 = 15 stocks × 1,457 trading days |
| Period | 29 Jan 2021 – 31 Aug 2026, daily |
| Sectors | Energy, Banking, IT, Consumer, Industrials, Telecom, Healthcare, Auto |
| Return column | Today's close-to-close return (checked: equals Close ÷ previous Close − 1 exactly) |
| Momentum_20D / Volatility_20D | 20-day price change and 20-day return swing, both including today's close |
| Macro columns | Market_Return (whole market's move), GDP_Growth (economy's growth), Interest_Rate, VIX ("fear index" = expected market volatility) |
| Prices | Rupees per share |

Key fact: today's return tells almost nothing about tomorrow's (correlation 0.004, where 0 = no link). Forecasting will be hard; even a small edge is valuable. Checked in Task 1: the macro columns are random numbers (a different value for each stock on the same date).

## 4. Required outputs (from the brief)

- [x] Task 1: future returns predicted with various models, compared (`outputs/task1/model_tests.csv`, `FINAL_M5_T1_return_predictions.csv`)
- [x] Task 2: for every rebalance date, predicted returns, ranking, selected stocks, portfolio (`outputs/task2/FINAL_M5_T2_stock_selections.csv`, `portfolio_returns.csv`, `portfolio_summary.csv`)
- [x] Answer to the committee: can ML identify stocks with superior future returns (evidence from Task 2 performance): no, on this data

## 5. Learning objectives shown here

Engineer financial features · Regression · Compare algorithms · Validation (walk-forward) · Avoid leakage · Forecast financial variables · Construct portfolios · Business recommendations.

## 6. Link to other modules

Module 6 uses this module's forecasts (ridge regression, M5-15) to build the "ML-predicted-return portfolio"; Module 9 uses the resulting performance for the "Equity investments" bucket (Module 6's after-cost figures, M6-11, replaced the M5-16 rates).

## 7. Results

**Task 1 — Predict future returns (built).**
- The data: the macro columns are random numbers (15 different values on the same date; about 0 correlation with the day before); Market_Return isn't the market (−0.016 with the stocks' average); stocks move independently (correlation 0.004); returns are balanced (54.8% up) with no outliers.
- 22 inputs × 3 horizons: 0 of 66 tests pass (line 0.05 ÷ 66 = 0.0008); no sector, calendar or VIX effect; the best of 946 combined conditions is luck (p 0.48).
- Five ways of predicting over 43 test months: no model beats luck (IC −0.049 to +0.005; shuffled-returns p 0.53–0.93) or the benchmarks (predict zero RMSE 8.67%, lowest; no model beats "always up" at 55.0%).
- In ₹: an IC of 0.05 would be worth about ₹5.3 crore a year on ₹100 crore; the test could detect 0.08 or more.
- To Task 2: every model's predictions, labelled "Returns predictable: No". Details: `reports/task1_report.md`.

**Task 2 — Stock ranking and portfolio (built).**
- Each month, each ranker's top 5 held at 20% each, 43 months (31 Jan 2023 – 31 Aug 2026), before trading costs.
- Benchmark all 15 equal weight: 15.8% a year, volatility 6.7%; ₹100 crore → ₹169.0 crore.
- Top 5: past average 18.9%, linear 14.4%, ridge 15.2%, random forest 8.3%, LightGBM 19.1%; p 0.40–0.98 (line 0.01); random top 5: 3.6%–29.3% (95%).
- Top 3 / 7 check: the best strategy flips with the number held; smallest p 0.31.
- 5 stocks carry about 1.8 times the risk of 15; models replace 48%–68% of holdings a month.
- Same answer with quarterly rebalancing (13 quarters; smallest p 0.08) and with the top 5 weighted by rank or predicted return (lowers the ML models' returns).
- September 2026 (latest rebalance date): every strategy's top 5 saved; ML models agree on LT and ITC, as much as they agreed in past months without beating luck.
- Answer: on this data ML does not identify stocks with superior future returns. To Module 6: ridge regression's predictions (M5-15) and the portfolio returns. To Module 9: rates (M5-16), replaced by Module 6's after-cost figures (M6-11). Details: `reports/task2_report.md`, `reports/module_5_report.md`.

## 8. Risks and limitations

- Low predictability of returns: high chance of overfitting (a model learning noise); strict walk-forward testing needed.
- Only 15 stocks: ranking "top 5" is a third of the universe.
- Synthetic prices: random macro columns, independent stocks, bell-curve returns; no dividends, no transaction costs in the data.
- 43 test months can only detect an IC of about 0.08 or more.
- Task 2 returns are before trading costs; the models' turnover (48%–68% a month) makes costs material (Module 6).

## Module 9 inputs (22 Nov 2026)

| Category | Return per ₹ (% a year) | Range | Bad year per ₹ | Bad year means | Capacity | Gap / assumption |
| --- | --- | --- | --- | --- | --- | --- |
| Equity investments: ML stock selection (extra over holding all 15) | 0.0 | Best model (LightGBM) +3.4 points, p = 0.57 (luck); ridge -0.5 | -7.42 | Worst model's shortfall against holding all 15 (a year, before costs) | — | Before trading costs; the stocks in the data look independent (synthetic) |

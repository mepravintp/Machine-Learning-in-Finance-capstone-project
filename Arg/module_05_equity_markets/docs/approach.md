# Module 5 — Approach

**The chain:** **forecast each stock's next-month return** (Task 1) → **rank, select the top stocks, build a portfolio** (Task 2) → Module 6 (portfolio optimisation) → Module 9 ("Equity investments").

| Stage | Decisions | Status |
| --- | --- | --- |
| Setup | M5-01 target, M5-02 safe inputs, M5-09 layout | Agreed |
| Task 1 | M5-03 monthly, M5-04 walk-forward, M5-06 exploration, M5-07 inputs, M5-08 models and pass test, M5-10 hand-off | Agreed 22 Nov 2026; built |
| Task 2 | M5-05 top 5, M5-11 benchmark, M5-12 equal weight, M5-13 before costs, M5-14 output file, M5-15 model for Module 6, M5-16 Module 9 figures, M5-17 latest portfolio and checks | Agreed 22 Nov 2026; built |

## Data

`data/nova_market_data.csv`: 15 stocks × 1,457 trading days (29 Jan 2021 – 31 Aug 2026), no missing values.
- `Return` is today's close-to-close change: predicting it would be leakage (M5-01).
- `Momentum_20D` and `Volatility_20D` include today's close, so they are known at the day's end (M5-02).
- **The macro columns (GDP_Growth, Interest_Rate, VIX, Market_Return) are random numbers:** 15 different values on the same date, about 0 correlation with the day before; Market_Return correlates −0.016 with the stocks' average. The stocks correlate 0.004 with each other.

## Target and timing

```text
Next-month return of stock i at month-end t = Close(i, next month-end) ÷ Close(i, t) − 1
68 month-ends − 1 = 67 months; first 24 train only → 43 test months (Jan 2023 – Jul 2026) × 15 stocks = 645 predictions
```

- **Monthly rebalancing (M5-03):** no input predicts at any horizon (day, week, month), so weekly's extra testing power has nothing to find, at about 4× the trading cost.
- **Walk-forward (M5-04):** each month, train on all earlier months, predict the next. Smallest detectable IC about 0.08.

## Task 1 — Predict future returns (built)

- **Exploration (M5-06):** target balance and outliers; 22 inputs × 3 horizons (66 tests, line 0.05 ÷ 66); inputs against each other; sector, calendar, VIX; 946 pairs of conditions with a shuffle test. Nothing predicts returns.
- **Inputs (M5-07):** 13 price and trading inputs + sector; macro dropped (random numbers); Past_20D dropped (identical to Momentum_20D). All 22 run once as a check.
- **Models (M5-08):** predict zero and past average (benchmarks), linear regression, ridge, random forest, LightGBM. IC decides; RMSE, MAE, hit rate vs "always up" reported. Pass test: 100 shuffled-returns runs per model, line 0.05 ÷ 4 = 0.0125.
- **Result:** no model beats luck (ICs −0.049 to +0.005; p 0.53–0.93) or the benchmarks.

## Hand-offs to Task 2

| From | File | What it holds | How Task 2 must treat it |
| --- | --- | --- | --- |
| Task 1 | `outputs/task1/FINAL_M5_T1_return_predictions.csv` | For 43 test months × 15 stocks: actual next-month return, every model's and benchmark's prediction, Sector, "Returns predictable: No: no model beats luck" | Predictions carry no ranking skill (M5-08); Task 2's portfolio is each model's business check |
| Task 1 | `outputs/task1/model_tests.csv` | IC, p-values, RMSE, MAE, hit rate per model | Evidence |

## Task 2 — Stock ranking and portfolio (built)

On each of the 43 rebalance dates, for each ranker (past average, linear regression, ridge, random forest, LightGBM):
1. **Predict:** read Task 1's walk-forward predictions (no retraining).
2. **Rank:** rank 1 = highest predicted return; ties to the alphabetically first ticker.
3. **Select:** the top 5 (M5-05); top 3 and 7 as one check table.
4. **Construct:** 20% in each, held to the next month-end (M5-12).

- **Benchmark (M5-11):** all 15 equal weight; random picks (1,000 runs) give luck's range.
- **Measures:** annual return (decides), excess and its p (t-test over months; line 0.05 ÷ 5 = 0.01), months beating the benchmark, share of random picks doing as well, volatility, return per unit of risk, maximum drawdown, turnover. Before costs (M5-13).
- **The latest rebalance date (M5-17):** every model trained on all 67 months picks its top 5 for September 2026 (31 Aug 2026); not scored, as September's result isn't in the data.
- **Checks (M5-17):** quarterly rebalancing (13 test quarters) and weighting the top 5 by rank or predicted return. Neither changes the answer.
- **Result:** no portfolio beats all 15 (15.8% a year): top 5 earned 8.3%–19.1%, p 0.40–0.98, all inside luck's range (3.6%–29.3%); the best strategy flips with the number held; 5 stocks carry about 1.8 times the risk of 15.

## Hand-offs to Module 6

| From | File | What it holds | How Module 6 must treat it |
| --- | --- | --- | --- |
| Task 1 | `outputs/task1/FINAL_M5_T1_return_predictions.csv` | Every model's predicted next-month return per stock and month | Input to the ML-predicted-return portfolio; model per M5-15: ridge regression. No proven skill |
| Task 2 | `outputs/task2/FINAL_M5_T2_stock_selections.csv` | Rank, selection, weight, reason per strategy, month, stock | The top-5 equal-weight portfolios, for comparison |
| Task 2 | `outputs/task2/portfolio_returns.csv` | Monthly returns of each top-5 portfolio and of all 15 equal weight | Same months (31 Jan 2023 – 31 Aug 2026); before costs, Module 6 applies the cost rate |

## Hand-off to Module 9 (M5-16)

| What | Value | How Module 9 must treat it |
| --- | --- | --- |
| Holding all 15 equal weight | 15.8% a year, volatility 6.7%, worst fall −3.6% (before costs) | Replaced by Module 6 (M6-11): final figures in `module_06_portfolio_optimization/outputs/FINAL_M6_module_output.xlsx` (Hand-off tab) |
| Extra return from ML stock-picking | 0 (none proven) | Don't allocate capital on an ML equity edge |
| Basis | 43 months, 15 stocks, likely synthetic | Planning figures, not forecasts |

## Shared code

- `helpers/m05_data.py`: loading, checks, rebalance dates, target, the 22 inputs, the monthly panel (also used by Module 6).
- `helpers/m05_style.py`: chart style.

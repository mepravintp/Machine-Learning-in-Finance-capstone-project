# Module 8 — Solution design

**Final output:** the workbook `outputs/FINAL_M8_module_output.xlsx` (Read me · Key numbers · Board actions · task tabs · Hand-off · Decisions · Evidence index), built from `FINAL_M8_T1_bs_benchmark.csv` and `FINAL_M8_T2_…`.

Chain: **Option data → Black–Scholes price and ML price → pricing error → Greeks → hedge → recommendation on pricing and exposure.**

## Task 1 — Black–Scholes benchmark

S = Spot, K = Strike, T = Time_to_Maturity (years), σ = Volatility, r = Interest_Rate, N(·) = chance a standard normal value is below that number.

```text
d₁ = [ ln(S ÷ K) + (r + σ² ÷ 2) × T ] ÷ (σ × √T)
d₂ = d₁ − σ × √T

Call price = S × N(d₁) − K × e^(−r × T) × N(d₂)
Put price  = K × e^(−r × T) × N(−d₂) − S × N(−d₁)
```

Checks: our price vs the provided Black_Scholes_Price column (matches within ₹0.27). Also: no-arbitrage floor (M8-08), gap breakdowns with Kruskal-Wallis tests and a Bonferroni line (M8-07), Greeks and book risk (M8-04).

Comparison with Market_Price:

```text
Pricing error = Market_Price − BS price
MAE  = average of |error|            RMSE = √(average of error²)
% gap = error ÷ BS price, only for options worth ₹1 or more (M8-06)
```

Reported overall and by: Option_Type, moneyness bucket (moneyness = S ÷ K; ITM = in the money, ATM = at the money, OTM = out of the money), maturity bucket, underlying.

## Task 2 — ML pricing (decided after Task 1's review, 22 Nov 2026)

| Part | What was done | Decision |
| --- | --- | --- |
| Set-ups | Direct ML (market price ÷ strike from the inputs) and hybrid (BS + learned correction ÷ strike) | M8-02 |
| Inputs | Spot ÷ strike, ln(spot ÷ strike), time, volatility, rate, call/put, volatility × √time; hybrid adds BS ÷ strike; no stock name | M8-10 |
| Models | Linear regression, random forest, LightGBM, neural network; seed 42 | M8-11 |
| Split | 80/20 random; 5-fold choice on the 80%; test once | M8-03 |
| Impossible prices | Excluded from training; test with and without | M8-12 |
| Better than BS | Lower ₹ and % gap, paired 95% range above 0; by price fifth, moneyness, call/put | M8-13 |
| Checks | Overfitting gap, shuffled-correction test, permutation importance | Standard sections |

## Greeks and hedge (learning objectives)

n(·) = standard normal density (bell-curve height).

```text
Delta (call) = N(d₁)             Delta (put) = N(d₁) − 1
Gamma        = n(d₁) ÷ (S × σ × √T)
Vega         = S × n(d₁) × √T              (per 1.00 change in σ; ÷ 100 for one volatility point)
Theta (call) = −S × n(d₁) × σ ÷ (2 × √T) − r × K × e^(−r × T) × N(d₂)     (per year; ÷ 365 per day)
```

Delta hedge (M8-14), one unit of each option, sized in ₹ (options on one stock carry different spots in the data):

```text
Shares to hold per underlying = −(sum of Deltas of all options on it)
Change in option book value ≈ Delta × ΔS + ½ × Gamma × ΔS²
```

Show P&L of the hedged vs unhedged book for spot moves of ±1%, ±5%, ±10%: the hedge removes most of the small-move risk; Gamma shows what is left for big moves.

## Reusable code

- `helpers/m08_data.py` — load and validate.
- `helpers/m08_black_scholes.py` — prices and Greeks (built and checked against the dataset now).
- `helpers/m08_style.py` — chart style; `helpers/m08_final_output.py` — the workbook.
- Notebooks: `m08_task1_bs_benchmark.ipynb`, `m08_task2_ml_pricing.ipynb`; runner `run_module_8.ipynb`.

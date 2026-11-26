# Module 8 — Derivatives

## 1. What the brief says (verbatim)

> **Business problem**
> NovaFin has exposure to equity options.
> Management wants to know:
> **Can ML improve option pricing and help manage derivatives exposure?**
>
> **Dataset:** nova_options.csv
>
> Variables: Underlying · Option_Type · Strike · Spot · Expiry · Time_to_Maturity · Volatility · Interest_Rate · Black_Scholes_Price · Market_Price
>
> **Task 1 — Black-Scholes benchmark**
> Calculate theoretical option price.
> Compare: BS Price with: Market Price
>
> **Task 2 — ML pricing**
> Predict: market price using ml models and compare performance w.r.t Black-Scholes

Related learning objectives (brief section 3) not in this module's tasks, which we cover here: "Understand Greeks", "Construct simple hedges". The business question also says "help manage derivatives exposure", which Greeks and hedging answer.

## 2. The task in plain words

- **Option** = a contract giving the right, but not the duty, to buy (a **Call**) or sell (a **Put**) a share at a fixed price (the **Strike**) on or before a date (the **Expiry**).
- **Spot** = today's share price. **Time_to_Maturity** = years left until expiry. **Volatility** = how much the share price is expected to swing in a year (0.20 = 20%). **Interest_Rate** = risk-free rate (return on a safe government bond), as a decimal.
- **Task 1** — compute the textbook fair price with the Black–Scholes formula and compare it with the price the option actually trades at (Market_Price). The gap shows what the formula misses.
- **Task 2** — train regression models (models that predict a number) to predict Market_Price and see whether they beat Black–Scholes.
- **Greeks** = how much the option price changes when one input changes: Delta (share price moves ₹1), Gamma (how fast Delta changes), Vega (volatility moves 1 point), Theta (one day passes).
- **Hedge** = a position that gains when the main position loses. A Delta hedge holds shares so that small share-price moves cancel out on the option book.

Example: Spot ₹1,500, Strike ₹1,550, 6 months, volatility 25%, rate 7% → Black–Scholes call price ≈ ₹107. If the market price is ₹115, the market is paying ₹8 more than the formula says.

## 3. Data

| Item | Value |
| --- | --- |
| File | data/nova_options.csv |
| Rows | 10,000 options (Call 4,945 · Put 5,055) on 15 underlyings (the shares the options are on) |
| Extra column not in the brief's list | Option_ID |
| Units | Prices in rupees per share; Volatility and Interest_Rate as decimals; Time_to_Maturity in years |
| Target (Task 2) | Market_Price |

## 4. Required outputs (from the brief)

- [x] Task 1: theoretical (Black–Scholes) price for every option; comparison with Market_Price
- [x] Task 2: ML models predicting Market_Price; performance compared with Black–Scholes
- [x] (Learning objectives / business question) Greeks for the book; a simple hedge and its effect
- [x] Answer: can ML improve option pricing and help manage derivatives exposure?

## 5. Learning objectives shown here

Engineer financial features · Regression · Compare algorithms · Validation · Price derivatives · Understand Greeks · Construct simple hedges · Business recommendations.

## 6. Link to other modules

Hedge cost and the loss avoided under stress feed the "Derivatives hedging" bucket in Module 9.

## 7. Results

**Pricing: ML doesn't improve on Black-Scholes on this data. Exposure: yes, a delta + half vega hedge cuts the bad days by almost half.**

| Finding | Number |
| --- | --- |
| Average gap from the market on 2,000 unseen options | Black-Scholes ₹6.07 · hybrid ML ₹6.22 · direct ML ₹8.48 |
| Biggest risk of the book | Volatility falling 5 points: −₹2.40 lakh |
| 1-in-100 bad day: no hedge / delta only / delta + half vega | −₹1.03 lakh / −₹1.15 lakh / −₹56,653 |

Task by task below; details in `reports/task1_report.md`, `reports/task2_report.md`, `reports/module_8_report.md`.

## 8. Risks and limitations

- Black–Scholes assumes constant volatility, no dividends and European exercise (only at expiry); the data does not say which style the options are.
- No time order or trade dates, so we cannot test the ML model on a later period.
- The book's position sizes are not given; hedging is shown per option and for an assumed holding of one contract each.

## Task 1 results (22 Nov 2026)

| Finding | Number | Meaning |
| --- | --- | --- |
| Our BS vs the file's | Within ₹0.27 | Formula correct |
| Average gap market − BS (MAE) | ₹5.84 (95% range ₹5.69–₹6.01) | About 3.1% of the price; grows with price (₹1.48 cheapest fifth → ₹14.42 dearest) |
| Bias | +₹0.05 (range −₹0.14 to +₹0.25) | No direction: BS neither too cheap nor too dear |
| Pattern by call/put, moneyness, maturity, volatility, price, stock | Direction never differs (p ≥ 0.18, line 0.004) | No "volatility smile": market ≈ BS + about 3% random noise |
| Learned correction (LightGBM, unseen options) | R² −0.10 (shuffled −0.02) | Nothing to learn beyond BS |
| Market prices below the no-arbitrage floor | 359 (3.6%), all in-the-money | Data errors; flagged |
| Book (one unit each): value / stock-equivalent | ₹19.4 lakh / ₹22.6 lakh | Behaves like ₹22.6 lakh of shares |
| All stocks −5% / +5% | −₹0.80 lakh / +₹1.44 lakh | Options cushion falls (gamma) |
| Volatility +1 point / one day | +₹50,463 / −₹2,068 | Time costs about ₹7.5 lakh a year |

**Why BS fits so well here:** each option comes with its own volatility. In real markets volatility must be estimated, and that is where most of BS's error comes from.

## Task 2 results (22 Nov 2026)

| Pricer (2,000 unseen options) | Average gap | vs BS (95% range) |
| --- | --- | --- |
| Black-Scholes | ₹6.07 | — |
| Direct ML (LightGBM) | ₹8.48 | ₹2.09–₹2.71 worse |
| Hybrid ML (BS + linear correction) | ₹6.22 | ₹0.07–₹0.23 worse (no clear difference without impossible prices) |

| Check | Result |
| --- | --- |
| BS best by price fifth, moneyness, call/put | 12 of 12 groups |
| Hybrid correction vs shuffled | No better (p = 1.0) |
| Overfitting (trees, neural network) | ₹1.8–₹3.3 better on training options: learned noise |
| By stock | BS closest in 13 of 15 stocks (hybrid ahead by ₹0.14–₹0.17 in two: noise) |
| Biggest risk | Volatility −5 points: −₹2.40 lakh (stocks −5%: −₹0.80 lakh) |
| Worst of 21 scenarios: A / B / C / D | −₹3.20 / −₹2.40 / −₹1.15 lakh / ₹0 (D unreliable on this data) |
| 1-in-100 bad day (100,000 simulated days): A / B / C | −₹1.03 lakh / −₹1.15 lakh / −₹56,653; chance of a losing day ≈ 49% for all |
| Running C | ≈ ₹10,900 day 1; ≈ ₹45,500 a year re-hedging; ≈ ₹13.3 lakh cash tied up |
| D | Flagged unreliable: options on one "stock" have different spots and volatilities |
| Choice rule | Board's 1-in-100 bad-day limit → least trading within it; default 4% → C |
| Written book (check) | Every risk flips; C still cuts the bad day by 42% |

**Answer to management:** ML doesn't improve option pricing on this data; BS's Greeks do help manage exposure through a delta hedge. Recommendations: keep BS; hedge with choice C (delta + half vega), shares reset daily; don't use delta-only; the Board sets the 1-in-100 bad-day limit and the choice rule picks the hedge; revisit ML with real market data.

**Why shares can't hedge volatility:** a share's price doesn't depend on volatility, so when volatility changes the shares don't move. Only other options (here, 1-year at-the-money calls sold) can offset it.


## Data check and volatility (added to Task 1, 22 Nov 2026)

| Finding | Number | Meaning |
| --- | --- | --- |
| Spot prices per stock on the one pricing day | 623–702 different, ₹100–₹3,500 | The stock label isn't a single real stock; pricing unaffected; hedges in ₹ |
| Volatility −5 points | −₹2,39,685 | Biggest risk: three times a 5% stock fall |
| Owned or written | Not in the data | Main view owned; written checked |

## Module 9 inputs: protecting equity money (22 Nov 2026)

| Floor | Priced at | Cost a year (per ₹100 crore) | Normal year after cost | Stocks −10% | **Stocks −20%** | Stocks −30% |
| --- | --- | --- | --- | --- | --- | --- |
| 100% | Module 6 swing (19.4%) | ₹4.67 crore | 10.9% | ₹-4.7 crore | **₹-4.7 crore** | ₹-4.7 crore |
| 100% | Check: puts priced dearer (25.0%) | ₹6.75 crore | 8.8% | ₹-6.8 crore | **₹-6.8 crore** | ₹-6.8 crore |
| 90% | Module 6 swing (19.4%) | ₹1.81 crore | 13.8% | ₹-11.8 crore | **₹-11.8 crore** | ₹-11.8 crore |
| 90% | Check: puts priced dearer (25.0%) | ₹3.33 crore | 12.3% | ₹-13.3 crore | **₹-13.3 crore** | ₹-13.3 crore |
| 80% | Module 6 swing (19.4%) | ₹0.49 crore | 15.1% | ₹-10.5 crore | **₹-20.5 crore** | ₹-20.5 crore |
| 80% | Check: puts priced dearer (25.0%) | ₹1.31 crore | 14.3% | ₹-11.3 crore | **₹-21.3 crore** | ₹-21.3 crore |

*Unprotected: −₹10 / −₹20 / −₹30 crore; normal year 15.6%.*

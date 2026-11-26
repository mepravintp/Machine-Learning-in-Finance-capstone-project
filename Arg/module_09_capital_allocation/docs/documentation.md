# Module 9 — Integrated Capital Allocation

## 1. What the brief says (verbatim)

> **Module 9 — Integrated Capital Allocation**
> This is the most important part of the capstone.
> The Board gives NovaFin: **₹1,000 crore**
> Students must allocate this capital.
>
> **Potential allocation categories**
> - Corporate lending
> - Retail lending
> - Digital banking
> - Equity investments
> - Wealth management
> - High frequency trading
> - Derivatives hedging
>
> Students should construct their own allocation. And give explanataion.
>
> **Additional points to be kept in mind:**
> 1. Make suitable assumptions as and where necessary
> 2. Clearly outline Risks & Limitations- data limitations, model risk etc
> 3. Model governance and explainability is important
> 4. Model complexity is not priced in though more than happy to experiment
> 5. Senior management is looking for actionable inputs

From section 2 of the brief (the central Board question), which Module 9 answers:

> Your team must justify the allocation using the ML models and financial analysis developed throughout the project.
> The final recommendation should answer:
> **Where should NovaFin deploy its capital, what risks will it take, and how should those risks be controlled?**

Section 2's example list also includes "Liquidity reserves" and "Risk management / hedging", so we cover both lists.

## 2. The task in plain words

The Board hands over ₹1,000 crore (= ₹10,000,000,000; 1 crore = 100 lakh) of incremental capital (new money). We split it across the businesses, using numbers from Modules 1–8, and answer three things:

1. **Where** the money goes (a table: bucket, ₹ crore, % share).
2. **What risks** each bucket brings (credit, fraud, market, liquidity, derivatives, model risk).
3. **How** those risks are controlled (limits, hedges, human review, model monitoring).

"Model governance" = rules for who owns each model, how it is checked, monitored and retrained. "Explainability" = being able to show why a model decided something (e.g. SHAP for a declined loan).

## 3. Inputs (from earlier modules)

| Bucket | Evidence that sizes it | Module |
| --- | --- | --- |
| Corporate lending | Approved corporate loans: return after ECL (expected credit loss) and costs | 2 |
| Retail lending | Approved retail loans: return after ECL and costs | 2 |
| Digital banking | Funded initiatives (Expected NPV), fraud loss and investigation cost rates | 1, 3 |
| Wealth management | Value protected by retention (CLV), fee income on investment balances | 4 |
| Equity investments | Chosen portfolio: return, volatility, VaR, drawdown, stress loss | 5, 6 |
| High frequency trading | Net profit after costs, its volatility, capacity | 7 |
| Derivatives hedging | Hedge cost vs loss avoided under stress | 8 (with 6) |
| Liquidity reserves | Assumed minimum share (liquidity file out of scope, P-03) | — |

## 4. Required outputs (from the brief)

- [x] Our own allocation of ₹1,000 crore across the categories, with explanation
- [x] Justification from the ML models and financial analysis of Modules 1–8
- [x] Where capital goes, what risks are taken, how they are controlled
- [x] Assumptions stated; risks and limitations (data, model risk); model governance and explainability; actionable inputs for senior management
- [x] (Learning objectives) stress test and VaR of the whole allocation

## 5. Learning objectives shown here

Integrated decision-making · Conduct stress testing · Calculate VaR · Construct simple hedges · Business recommendations.

## 6. Risks and limitations

- **Synthetic data:** equities move independently and every option on a stock has its own price, so real-market risk is added as a stress estimate.
- **Model risk:** weak models (initiative success) are used only as flags; models with no skill (churn, returns, ML option pricing) are not used.
- **No data links the businesses,** so stress scenarios are set by hand, with one where everything happens at once.
- **Assumptions:** the liquidity floor, the ₹100 crore bad-year budget and re-priced loans keeping the same borrowers.

## 7. Results

**In one sentence: put ₹300 crore into equities protected by a put, ₹51 crore into strategic initiatives (all but ₹1 crore in units that clear the 6.8% hurdle), ₹5 crore into an HFT pilot and ₹6 crore into hedging, and hold ₹638 crore in safe securities, of which ₹286 crore waits for lending to be re-priced. That earns about ₹91.8 crore a year (9.2%), against about −₹2 crore if the money went the bank's current way, and even a crash, a rate cut and failing initiatives together cost only about ₹5 crore.**

### Where the ₹1,000 crore goes (Year 1)

| Category | ₹ crore | Share | Expected return | What the money buys |
| --- | --- | --- | --- | --- |
| Equity investments | 300.0 | 30.0% | 15.6% | All 15 stocks, equal weight (no ML stock-picking) |
| Digital banking | 19.4 | 1.9% | 13.1% | Digital Banking and Payments initiatives, only while the ML fraud rule runs |
| Wealth management | 15.3 | 1.5% | 17.6% | Wealth initiatives (one approved now) |
| Derivatives hedging | 17.1 | 1.7% | cost | Risk Analytics initiatives (₹11.5 crore), the 90% put on the equities (₹5.4 crore a year), option-book hedge C (₹0.1 crore) |
| High frequency trading | 5.0 | 0.5% | 0% planned | Trading pilot with a stop rule (order timing needs no capital) |
| Retail lending | 4.2 | 0.4% | 13.3% | SME initiatives; approved retail loans wait in the reserve until re-priced |
| Corporate lending | 1.0 | 0.1% | 6.3% | One approved Corporate Banking initiative; corporate loans wait until re-priced |
| Liquidity reserve | 638.0 | 63.8% | 6.8% | Government securities; ₹286 crore earmarked for re-priced lending |
| **Total** | **1,000** | | **9.2% (₹91.8 crore)** | |

### Is it better than what NovaFin would do anyway? (profit, growth, safety)

| Way to deploy ₹1,000 crore | Profit a year | Put into NovaFin's businesses | Bad year, all at once |
| --- | --- | --- | --- |
| The bank's way (every loan at today's prices, all 180 initiatives) | **−₹2.4 crore** | ₹923 crore | −₹74 crore |
| All in safe securities | ₹68.0 crore | ₹0 | +₹50 crore |
| All in equities, unprotected | ₹156 crore | ₹0 | **−₹200 crore** (twice the budget) |
| **Our plan, Year 1** | **₹91.8 crore** | ₹56 crore | **−₹5 crore** |
| **Year 2, after re-pricing** | ₹91.8 crore (₹99.0 crore in the bank view) | **₹506 crore** | −₹27 crore |

- **The bank's way loses money:** its lending earns 0.43% above expected losses (on actual losses it breaks even at a 0.48% cost of funds) and its initiatives lose 3.6% a year. Putting more money through today's practice lowers profit.
- **Growth comes from re-pricing, not from lending more at today's prices.** Approved loans need about 12.3% a year (8.75% today), Review loans about 15.6% (9.8%). Once re-priced loans pass the quarterly test, ₹450 crore moves from the reserve into lending.

### The capital plan: what we use now, and how the ₹638 crore reserve is put to work

**In one line: the reserve is a waiting room, not idle money. It earns ₹43.4 crore a year while it waits, ₹538 crore of it moves into lending and initiatives as each test is passed, and only a ₹100 crore floor stays safe for good.**

**1. What we put to work now (Year 1)**

| Use | ₹ crore | Earns a year | Bad year | Owner | First action |
| --- | --- | --- | --- | --- | --- |
| Equities: all 15 stocks, equal weight, with a 1-year 90% put | 305.4 | +₹41.4 crore | −₹35.4 crore (20% crash, the put pays) | Chief Investment Officer | Month 1: buy, with the put |
| Initiatives ready now: 1075 Wealth in full, 1062 Corporate Banking in stages | 3.2 | +₹0.5 crore | ₹0.0 crore | Head of Strategy | Now |
| Initiatives after review: Wealth, Payments, Digital Banking, Risk Analytics, SME | 48.2 | +₹6.6 crore | −₹1.0 crore (1-in-20 case) | Head of Strategy | Quarters 1–2, unit by unit |
| HFT trading pilot with a stop rule | 5.0 | ₹0 planned | −₹0.5 crore (stop rule) | Head of Trading | Now; decide after 1 quarter |
| Option book hedge (choice C) | 0.1 | ₹0.0 crore | Cuts the 1-in-100 bad day by 45% | Derivatives desk | Now, reset daily |
| **Liquidity reserve, released by the plan below** | **638.0** | **+₹43.4 crore** | +₹31.9 crore (rates fall to 5%) | Treasurer with ALCO | Now |
| **Total** | **1,000** | **₹91.8 crore (9.2%)** | **−₹5.1 crore, all at once** | | |

**2. The reserve release plan: what moves the ₹638 crore, and when**

| Step | ₹ crore | What it funds | Released when (the test) | Checked | Owner | If the test fails | Cost of releasing it now, at today's prices |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 286 | Approved loans, re-priced | Re-priced loans earn at least 6.8% a year after expected loss (rate about 12.3%, 8.75% today); the scorecard stays stable (score drift PSI ≤ 0.25; defaults ≤ 1.5 × predicted in every band); the plan's combined bad year stays within ₹100 crore | Every quarter | Chief Risk Officer + Head of Lending; ALCO releases | Stays in the reserve, earning 6.8% | ₹10.0 crore a year |
| 2 | 164 | Review loans, fixed | The same test at about 15.6% (9.8% today), or the risk cut by collateral or a person checking each large loan; only after step 1 | Every quarter, after step 1 | Chief Risk Officer + Head of Lending; ALCO releases | Stays in the reserve | ₹9.6 crore a year |
| 3 | up to 88 | Future initiatives | Each project passes Module 1's rules: Expected NPV above 0, return above 6.8% a year, loss tolerance decides full or staged funding; Digital only while the fraud rule runs; combined bad year within ₹100 crore | At each project review | Head of Strategy; CFO approves | Not funded; stays in the reserve | — |
| Floor | 100 | Never released | At least 10% of the ₹1,000 crore stays safe, for withdrawals and a bad year | Every quarter | Treasurer with ALCO | — | — |
| **Total** | **638** | | | | | | **₹19.6 crore a year** if all loans went out today |

**3. What each stage changes: profit, growth, risk**

| Stage | When | Reserve | Loan book | Money working in NovaFin's businesses | Profit a year | Profit, bank view | Bad year, all at once (budget used) | Same, if collateral also fetches less (LGD 60%) | Profit above the bank's way |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Today | Now | ₹638 crore | ₹0 | ₹56 crore | ₹91.8 crore | ₹91.8 crore | −₹5.1 crore (5%) | −₹5.1 crore (5%) | +₹94.2 crore |
| After step 1 | Quarterly test; planned in Year 2 | ₹352 crore | ₹286 crore | ₹342 crore | ₹91.8 crore | ₹96.4 crore | −₹15.5 crore (16%) | −₹31.1 crore (31%) | +₹94.2 crore |
| After step 2 | Year 2 | ₹188 crore | ₹450 crore | ₹506 crore | ₹91.8 crore | ₹99.0 crore | −₹27.0 crore (27%) | −₹57.0 crore (57%) | +₹94.2 crore |
| After step 3 (if like today's initiatives) | As projects pass review | ₹100 crore (the floor) | ₹450 crore | ₹594 crore | ₹97.9 crore | ₹105.1 crore | −₹33.1 crore (33%) | −₹63.1 crore (63%) | +₹100.3 crore |

- **Growth:** money working in NovaFin's own businesses grows from ₹56 crore to ₹506 crore after the two lending steps, and up to ₹594 crore with step 3, ten times today.
- **Profit:** never falls. Re-priced loans are planned at exactly the 6.8% hurdle, so in the ₹1 = ₹1 view lending earns what the reserve did; anything above the hurdle is upside. In the bank view (deposits fund 88% of each loan at 5%), profit rises to ₹99.0 crore, and to ₹105.1 crore with step 3.
- **Loss avoided:** lending the ₹450 crore today, at today's prices, would cost ₹19.6 crore a year against the reserve and lose money in a recession. Waiting for the test avoids that.
- **Risk:** the combined bad year grows as money goes to work, but uses at most a third of the ₹100 crore budget (−₹33.1 crore after step 3). If collateral also fetches less (60% of a defaulted loan lost instead of 40%), it reaches −₹57.0 crore after step 2 and −₹63.1 crore after step 3: still inside the budget. Every release is stress-tested first.

### What the ML adds

| Module | ₹ effect |
| --- | --- |
| Credit risk | +₹7.4 crore a year above actual losses, with ₹354 crore less lent at risk |
| Initiatives | +₹17.4 crore a year expected (the 33 the plan funds, ₹51.4 crore at 13.7%, instead of all 180 at −3.6%); mostly from the NPV, payback and hurdle rules, because the success model only screens slow payers (the risk rating alone gives a similar Review list: 31 vs 38) |
| Equities | +₹15.0 crore a year on ₹300 crore by **not** following ML stock picks that failed validation (measured over 43 months; the gap is not beyond luck, p 0.39) |
| Fraud | Saves ₹4.58 crore per ₹100 crore of money moved |
| HFT order timing | ₹3.43 crore a year (261 trading days) per ₹100 crore of orders a day |
| **Total of the first three** | **₹39.8 crore a year** against the same decisions without this work (the loan book, the 180 initiatives, the ₹300 crore of equities), before fraud and order-timing savings, which scale with volumes. The equities ₹15.0 crore is measured but not proven beyond luck (p 0.39) |

### How safe is it?

| Stress | Year's result |
| --- | --- |
| Plan | +₹91.8 crore |
| Market crash −20% (the put pays) | +₹15.0 crore |
| Equities at the low end (8.6%) | +₹70.8 crore |
| Rates fall to 5% | +₹80.3 crore |
| Credit recession with the approved loans released at today's prices (LGD 60%) | +₹50.6 crore |
| **All at once, today** | **−₹5.1 crore** |
| All at once, approved loans released at today's prices (LGD 60%) | −₹41.1 crore |
| All at once, all three steps released (loans re-priced, LGD 60%) | −₹63.1 crore |
| Reverse stress | With the put no crash can break the ₹100 crore budget; without it a 50% fall would (with the rest of the plan earning as expected) |

**What the ₹100 crore is:** the bad-year budget, the most the whole ₹1,000 crore plan may lose in one bad year (10%). It is a **loss limit, not an amount we allocate**: all ₹1,000 crore is allocated. The brief gives no figure (it asks for "acceptable levels of" risk), so 5%, 10% and 15% were considered and 10% was agreed (M9-10). It did not shape the split: the 30% cap stopped equities first. The reserve floor is also ₹100 crore (10%), but it is a different rule: money that is never released.

All scenarios stay inside the ₹100 crore budget. Two ways to read how much of it is used today: **5%** (−₹5.1 crore) is the whole year's result, with the reserve's interest counted; **₹37.5 crore** is what the allocation rule counts, adding each use's own bad year and no interest, which leaves ₹62.5 crore.

### Why it looks like this
- **Few uses beat the 6.8% risk-free rate at scale:** equities (13.8% after the put) and ₹50 crore of initiatives. Lending at today's prices earns 3.3% and loses 2.2% in a recession.
- **The optimiser (method B) lands on the same split:** the result comes from the evidence and the limits, not the method.
- **The bank view of lending** (12% capital) beats the hurdle only if deposits cost under 2.8%, and loses 33% of the capital in a recession even at 2%. That's why the main view stays ₹1 = ₹1 and growth waits for re-pricing.
- **Evidence strength:** ₹638 crore strong (market rate), ₹306 crore medium (equities, the put, the option-book hedge), ₹51 crore weak (initiatives, staged), ₹5 crore pilot.
- **Liquidity:** ₹943 crore can come back within days; ₹51 crore (initiatives) is locked in for about 5 years; ₹5 crore (the put) is spent each year.

### Limitations
- **Synthetic data:** equities move independently, and every option on a stock has its own price. Real-market risk is a stress estimate.
- **No data links the businesses,** so the scenarios are set by hand. No cost of funds, running costs or recovery data. Lending's Year 2 assumes re-priced loans keep the same borrowers.
- **Short histories:** 43 months for equities, 3 test days for HFT. The P(Success) model is weak; it only screens slow payers (36 into Reject), and the risk rating alone gives a similar list.


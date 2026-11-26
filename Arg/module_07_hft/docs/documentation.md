# Module 7 — HFT (High-Frequency Trading)

## 1. What the brief says (verbatim)

> **Business Scenario**
> NovaFin's trading desk executes large equity orders in the market.
> The Head of Trading asks:
> **Can ML use limit-order-book information to predict short-horizon price movements and improve order execution?**
>
> **Dataset**
> nova_hft_orderbook.zip (provided as a zip due to file size; unzip to nova_hft_orderbook.csv)
>
> Recommended structure:
>
> | Variable | Description |
> | --- | --- |
> | Timestamp | Millisecond/microsecond timestamp |
> | Stock | Security |
> | Bid_Price_1 | Best bid |
> | Ask_Price_1 | Best ask |
> | Bid_Size_1 | Best bid quantity |
> | Ask_Size_1 | Best ask quantity |
> | Bid_Price_2 | Second bid |
> | Ask_Price_2 | Second ask |
> | Bid_Size_2 | Second bid quantity |
> | Ask_Size_2 | Second ask quantity |
> | Bid_Price_3 | Third bid |
> | Ask_Price_3 | Third ask |
> | Bid_Size_3 | Third bid quantity |
> | Ask_Size_3 | Third ask quantity |
> | Last_Price | Last traded price |
> | Trade_Volume | Trade volume |
> | Trade_Side | Buy/Sell |
> | Order_Arrival_Rate | Order arrival intensity |
> | Cancellation_Rate | Cancellation intensity |
> | Future_Return | Target |
> | Price_Move_Class | Up/Down/No Move |
>
> **ML Task 1 — Short-Horizon Direction Prediction**
> Target: Price_Move_Class with: UP · DOWN · NO_MOVE
> Note: the provided dataset (nova_hft_orderbook.csv) labels this class FLAT. Treat FLAT as equivalent to NO_MOVE.
> Important: Exclude Future_Return_100ms and Future_Price_100ms from your feature set for this task — these variables are used to construct the target label and will cause data leakage if included.
> Compare models and performance
>
> **ML task 2- model probability into trading signal**
> Does the prediction generate enough economic value? Can we generate some trading signal and backtest.

Instructor clarifications 4 and 7: the HFT module is compulsory for all groups; FLAT = NO_MOVE.

## 2. The task in plain words

- **Limit order book** = the live list of everyone waiting to buy (bids) and sell (asks) a stock, at each price. Best bid = highest price a buyer offers; best ask = lowest price a seller accepts; spread = best ask − best bid (the cost of trading immediately).
- **Short horizon** = the next 100 milliseconds.
- **Task 1** — classify whether the price will go UP, DOWN or stay FLAT in the next 100 ms, using only what the order book shows now. Never use Future_Return_100ms or Future_Price_100ms as inputs: they are the answer itself (data leakage).
- **Task 2** — turn the model's probabilities into buy / sell / do-nothing signals, backtest them (replay on past data) after paying the spread and fees, and judge if the profit is worth it. The execution angle: when NovaFin must buy a large order, delaying when the model expects a fall can save money.

Example: best bid ₹2,100.65, best ask ₹2,100.70, spread ₹0.05. Buying at the ask and seeing the price rise only ₹0.03 still loses money after paying the spread.

## 3. Data

| Item | Value |
| --- | --- |
| File | data/nova_hft_orderbook.csv (unzipped) |
| Rows | 120,000 order-book events |
| Period | 20 trading days, January 2026 (Trading_Day column, day-first dates) |
| Stocks | 10 (NOVA01–NOVA10) |
| Event types | LIMIT_ORDER 57,473 · MARKET_ORDER 32,406 · CANCEL 30,121 |
| Target | Price_Move_Class: DOWN 42% · UP 42% · FLAT 16% |
| Label rule (checked) | UP if Future_Return_100ms > +0.012%; DOWN if < −0.012%; else FLAT |
| Columns beyond the brief's table | Trading_Day, Event_Type, Short_Term_Volatility, Mid_Price, Spread, Relative_Spread, OBI_Level1, OBI_3Level, Total_Depth, Microprice, Microprice_Minus_Mid, Future_Return_100ms, Future_Price_100ms |
| Timestamp | Minute precision only (7,506 unique values), not milliseconds as the brief's table says; order within a minute = file order |

## 4. Required outputs (from the brief)

- [x] Task 1: models compared on UP / DOWN / NO_MOVE (FLAT), with Future_* columns excluded
- [x] Task 2: trading signal from model probabilities, backtest, verdict on economic value
- [x] Answer to the Head of Trading: can ML predict short-horizon moves and improve execution?

## 5. Learning objectives shown here

Engineer financial features · Classification (3 classes) · Compare algorithms · Validation (by day) · Avoid data leakage · Forecast financial variables · Evaluate strategies · Backtesting · Business recommendations.

## 6. Link to other modules

Net profit, its volatility and capacity feed the "High frequency trading" bucket in Module 9 (likely small, given fragility).

## 7. Results

**Yes on both counts: ML predicts the next tenth of a second's move, and it improves order execution.**

| Finding | Number |
| --- | --- |
| Right direction on unseen days | 60.6%, against 42.0% for guessing |
| ML against the simple order-balance rule | AUC 0.791 vs 0.781 (gain 95% range +0.008 to +0.012), in all 10 stocks |
| Timing the desk's own orders | Saves ₹1,315 per ₹1 crore: about ₹3.4 crore a year per ₹100 crore of orders a day |
| Trading on the signal | +₹700 per ₹1 crore trade after all costs; 86% of the gross gain goes on costs |

Details: `reports/task1_report.md`, `reports/task2_report.md`, `reports/module_7_report.md`.

## 8. Risks and limitations

- Only 20 days: results may not hold in other market conditions.
- Timestamps are minute-level, so true 100 ms timing and latency (delay in sending orders) cannot be checked.
- Backtest assumes we trade at the quoted prices without moving the market.

## Concepts explained (for study)

| Concept | Meaning | Formula / example |
| --- | --- | --- |
| Limit order book | The exchange's live list of waiting orders for a stock: bids (buyers) and asks (sellers) | — |
| Level 1, 2, 3 | Best, second-best, third-best price on each side, with the shares waiting there | NOVA09: bid 2,100.65 × 1,349 / ask 2,100.70 × 2,933 at level 1 |
| Tick | Smallest price step | ₹0.05 here |
| Spread | Best ask − best bid: the cost of trading immediately | ₹0.05 = 0.24 bps on ₹2,100; median 1.14 bps |
| Mid price | (Best bid + best ask) ÷ 2 | 2,100.675 |
| Microprice | Mid weighted by waiting sizes, leaning to the lighter side | (ask × bid size + bid × ask size) ÷ (bid size + ask size) = 2,100.666 |
| OBI (order-book imbalance) | (bid size − ask size) ÷ (bid size + ask size), −1 to +1; positive = more buyers waiting | (1,349 − 2,933) ÷ 4,282 = −0.37 → leans down |
| OFI (order-flow imbalance) | Change in best-bid size − change in best-ask size since the last event | A flow, where OBI is a snapshot |
| bp (basis point) | 0.01% = 1/10,000; on ₹1 crore = ₹1,000; on a ₹2,100 share = 21 paise. One common unit for tiny moves, spreads and charges, comparable across stock prices | 1.2 bps = the label's UP/DOWN line; move about 4 bps; spread about 1.1; Indian intraday charges about 3.5 (2.5 transaction tax + 0.6 exchange + 0.3 stamp duty + 0.1 SEBI/GST) |

**Findings on the questions raised (22 Nov 2026):**
- **Trade volume:** a trade's side matters (after a buy 57% of moves are UP, after a sell 42%), its size doesn't (UP share 57.4% / 57.9% / 57.5% for small / medium / large buys). Unsigned volume has no direction (AUC 0.50); the waiting orders (OBI) show the pressure before trades happen.
- **Time of day:** tested within each stock; none changes its UP / DOWN / NO_MOVE mix by hour beyond chance (line 0.05 ÷ 10; smallest p 0.009).
- **Industries:** no sector column in the data. The 10 stocks move together (minute-to-minute correlation 0.51), but other stocks' imbalance adds nothing once a stock's own OBI is known (validation AUC 0.7795 either way).

## Results (22 Nov 2026)

**Final output:** `outputs/FINAL_M7_module_output.xlsx`.

**Task 1:**
- Logistic regression on 15 order-book inputs is right 60.6% of the time on 3 unseen days, against 42.0% for guessing. AUC for rises vs falls is 0.791, against 0.781 for the simple buyer/seller balance (OBI) alone; DeLong p < 0.0001.
- The percentages are honest.
- NO_MOVE can't be foreseen: the model's chance of it runs from 5% to 22%, barely higher before real no-moves.

**Task 1 is solid:**
- Overfitting gap +0.003 (trees +0.043 to +0.053).
- It beats the simple rule in all 10 stocks and on all 3 test days.
- It passes the luck test: shuffled AUC 0.54 vs real 0.79, p = 0.0099.
- Its gain over the simple rule is +0.010 (95% range +0.008 to +0.012).
- **Main drivers:** buyers vs sellers waiting at the best price (odds × 2.39) and the spread (× 0.74).

**What Task 1 means for Task 2 (review, M7-17):**
- The move a trade catches grows in step with the lean: about 7.1 bps × the lean (+0.27 bps in the least confident tenth, +5.46 in the most).
- Spreads are widest when the model is most confident: 1.77 vs 1.10 bps.
- No-moves are fewer when the model is confident: 10.5% vs 20.9%.
- So Test 1 trades only when the expected gain beats that moment's own cost (M7-13 revised).

**Task 2:**
- **Test 1, trading on the signal, cost-aware rule** (trade when 7.1 bps × the lean beats that moment's spread + 3.5 bps):
  - per ₹1 crore trade: +₹4,994 before costs → +₹4,200 after the spread → +₹700 after charges;
  - +₹10.3 lakh over 3 test days (95% range +₹6.4 to +₹14.1 lakh), every day positive, 8 of 10 stocks, beyond luck (p = 0.001);
  - the old fixed cut-off made +₹4.5 lakh;
  - if real costs are 1 bp higher: −₹4.4 lakh if the rule isn't told, +₹0.7 lakh if it is.
- **Test 2, timing the desk's orders:** ₹1,315 saved per ₹1 crore of orders (95% range ₹1,272–₹1,356), beyond luck. That's ₹3.43 crore a year per ₹100 crore of orders a day.

**Recommendation:** time the desk's orders now; run the cost-aware trading rule as a measured pilot (real costs fed into the rule, stop rule).

## The recommendation: what it means, what it adds, why it matters

**It answers the Head of Trading's two-part question** ("predict short-horizon price movements **and improve order execution**") and the brief's "does the prediction generate enough economic value?". It turns the analysis into what to do, and what each part is worth.

**1. Time the desk's own orders now.**
- **What it means:** the desk already places large client orders every day. When it has to buy, it checks the model first. If the model expects the price to dip in the next tenth of a second, it waits a moment and buys a little cheaper (the reverse for sales).
- **What it adds:** about **₹1,315 saved for every ₹1 crore of orders**, which is about **₹1.3 lakh a day, ₹3.4 crore a year** for a desk placing ₹100 crore of orders a day. It grows with the desk's volume.
- **Why now:** there's no extra cost (the order and its taxes happen anyway), it's reliable (buys and sells, all 10 stocks, far beyond luck), and it's low-risk (it changes only *when* an order goes in, not *whether*).

**2. Run the cost-aware trading rule as a measured pilot.**
- **What it means:** NovaFin could also trade for its own profit, buying and selling within a tenth of a second when the expected gain beats that moment's cost. On the test days this made **+₹700 per ₹1 crore trade, +₹10.3 lakh over 3 days, profitable every day**.
- **Why a pilot, not full scale:**
  - The margin is thin. Of ₹4,994 caught per trade before costs, ₹4,294 (86%) went on the spread and taxes.
  - It rests on costs that were assumed, not measured (zero brokerage, fills at the quoted price). If the real cost is 1 bp higher and the rule isn't told, the ₹10.3 lakh becomes a ₹4.4 lakh loss.
- **The pilot, step by step:**
  1. Start with small trades in the narrow-spread stocks, where most of the profit came from (NOVA09: +₹4.7 lakh).
  2. Record the real brokerage, the prices actually achieved and the slippage.
  3. Feed the real cost into the rule. Told the true cost, it trades less and stayed profitable even at 1 bp more (+₹0.7 lakh).
  4. Stop if the profit after costs turns negative.
- **What it adds:** a chance at extra trading income, with the true costs found out before real money is committed.

**Why it matters for the Board and Module 9**

| Without the recommendation | With it |
| --- | --- |
| "The model is 60.6% accurate", which says nothing about money | Two concrete uses, each with a ₹ value and a risk level |
| Risk of funding a trading desk on a thin, cost-sensitive profit | Capital goes only where the gain is solid (order timing); trading earns its place through a pilot |
| Module 9 can't value high-frequency trading | Module 9 gets ₹1,315 saved per ₹1 crore of orders as a cost saving, and trading as a small pilot rather than a capital line |

**In short:** the model's value lies mainly in making the desk's existing trading cheaper, which is dependable and should start now. Trading on it for profit may add more, but only after its real costs are proven.

## Module 9 inputs (22 Nov 2026)

| Category | Return per ₹ | Range | Bad case | Capital needed |
| --- | --- | --- | --- | --- |
| Order timing (desk orders) | Saves 0.013% of every ₹ of orders (₹1,315 per ₹1 crore) | 0.013–0.014% | 0 (if the signal stopped working, waits save nothing) | None |
| Order timing on Module 9's equity money | 0.010% a year of the equity money (Module 6 turnover ≈ 0.8× a year) | 0.010–0.011% | 0 | None |
| Trading pilot | +₹700 per ₹1 crore traded, per trade | +₹6.4 to +₹14.1 lakh over 3 test days | −₹4.4 lakh over 3 days if costs are 1 bp higher and the rule isn't told | Small; same-day positions |

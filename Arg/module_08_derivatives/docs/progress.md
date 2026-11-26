# Module 8 — Progress

| Task | Step | Status | Date | Notes |
| --- | --- | --- | --- | --- |
| Setup | Data loads and passes checks (`helpers/m08_data.py`) | Done | 16 Nov 2026 | 10,000 options |
| Setup | Black–Scholes and Greeks functions (`helpers/m08_black_scholes.py`) | Done | 16 Nov 2026 | Matches provided Black_Scholes_Price within ₹0.27 (mean gap ₹0.02); worked example gives ₹107.20. Market vs BS mean gap ₹5.84 |
| Task 1 | Decisions M8-01, M8-04, M8-06 to M8-09 agreed after the first data look | Done | 22 Nov 2026 | ₹ measures; % only ≥ ₹1; 359 below-floor prices flagged |
| Task 1 | Notebook `m08_task1_bs_benchmark.ipynb` end to end: data, EDA, BS check, gap in ₹/%, breakdowns with tests, impossible prices, Greeks and book risk, Task 2 review, findings, save; report, docs, runner | Done | 22 Nov 2026 | MAE ₹5.84, bias ₹+0.05, 3.1% typical; no pattern (R² −0.10); book ≈ ₹22.6 lakh of stock, −5% → −₹0.80 lakh |
| Task 1 → 2 | Review of Task 1 results; Task 2 decisions M8-02, M8-03, M8-10 to M8-14 agreed | Done | 22 Nov 2026 | No pattern in the gap → ML expected at best to match BS |
| Task 2 | Notebook `m08_task2_ml_pricing.ipynb` end to end: 8 models (5-fold), overfitting check, factor table, test once vs BS (paired 95% ranges), segments, shuffled-correction test, drivers, delta hedge, ₹, findings, recommendation, save | Done | 22 Nov 2026 | BS ₹6.07 vs hybrid ₹6.22 vs direct ₹8.48; BS best in 12/12 groups; hedge: −5% day −₹79,948 → +₹32,925 |
| Task 2 | What the models rely on: permutation importance (simpler than SHAP, same purpose) | Done | 22 Nov 2026 | Direct ML relies on BS's own inputs |
| Greeks | Greeks for the book (Task 1); delta hedge scenarios (Task 2) | Done | 22 Nov 2026 | ±1% risk cut about 95% |
| Wrap-up | Module report, workbook `FINAL_M8_module_output.xlsx`, runner, HOW_TO_RUN | Done | 22 Nov 2026 | |
| Task 2 | Added: pricing by stock (step 6b); four hedging choices over 21 stock × volatility scenarios, choice rule, hedge by stock (step 9); default C agreed; reports, workbook, docs, prep files updated | Done | 22 Nov 2026 | Worst case A −₹3.20 / B −₹2.40 / C −₹1.15 / D ₹0 lakh; BS best in 13/15 stocks |
| Task 1 + 2 | Tested first, then agreed and added: Task 1 data check (spots per stock) and volatility scenarios; Task 2 step 9c (loss chances over 100,000 simulated days, running costs, written-book check) and 9d (choice rule on the 1-in-100 bad day); D flagged unreliable; reports, workbook, docs, prep files updated | Done | 22 Nov 2026 | 1-in-100 bad day A −₹1.03 lakh / B −₹1.15 lakh / C −₹56,653 |
| Module 9 inputs | Task 2 step 9e: cost of protecting equity money (puts at 100/90/80% floors), Module 7 turnover link; `module9_inputs.csv`, `protect_equity_money.csv`; workbook tabs; reports, docs, prep files | Done | 22 Nov 2026 | 90% floor ₹1.81 crore a year per ₹100 crore; crash −20% → −₹11.8 crore |

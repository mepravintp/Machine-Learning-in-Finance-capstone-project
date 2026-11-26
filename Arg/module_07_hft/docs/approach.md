# Module 7 — Approach

**The Head of Trading's question (brief, verbatim):** *"Can ML use limit-order-book information to predict short-horizon price movements and improve order execution?"*

**The chain:** order book at one moment → **Task 1:** chance the price goes up, down or doesn't move in the next 0.1 second → **Task 2:** (Test 1) does trading on that make money after costs? (Test 2) does it make the desk's own orders cheaper? → one recommendation → Module 9 ("High frequency trading").

## Where to find everything (decision M7-16, project decision P-21)

| What | File | Who it's for |
| --- | --- | --- |
| **Open this first** | **`outputs/FINAL_M7_module_output.xlsx`**: Read me (with a column guide) · Key numbers · Board actions · Task 1 tab · Task 2 tab · Hand-off to Module 9 · Decisions · Evidence index | Everyone |
| Task 1 final file | `outputs/task1/FINAL_M7_T1_direction_predictions.csv`: every tuning- and test-day moment, the model's chances of up / down / no move, its prediction, what happened, and why in plain words | Board, evaluator, Task 2 |
| Task 2 final file | `outputs/task2/FINAL_M7_T2_trade_decisions.csv`: every test-day moment, what Test 1 and Test 2 did, the ₹ result, and the reason in plain words | Board, evaluator, Module 9 |
| Full explanation | `reports/task1_report.md`, `task2_report.md`, `module_7_report.md` | Everyone |
| Code | `notebooks/m07_task1_direction.ipynb`, `m07_task2_signal.ipynb`; `run_module_7.ipynb` runs all, ending with the workbook | Evaluator |
| Shared code | `helpers/m07_data.py` (loading, split, leakage guard, the 15 inputs), `helpers/m07_style.py`, `helpers/m07_final_output.py` (the workbook) | — |

## Decisions, in order

| Stage | Decisions | Status |
| --- | --- | --- |
| Data | M7-01 FLAT = NO_MOVE · M7-02 Future_* never inputs · M7-03 given order-book columns are safe · M7-05 keep file order | Agreed |
| Split | M7-04 days 1–14 train, 15–17 tune, 18–20 test (test touched once) | Agreed |
| Task 1 | M7-07 exploration on training days · M7-08 15 inputs, OBI alone as benchmark · M7-09 four models · M7-10 AUC decides, log-loss second, DeLong p < 0.017 to beat OBI alone · M7-11 NO_MOVE kept, models unweighted | Agreed |
| Review | M7-17 Task 1's results checked against Task 2's rules (Task 1 step 7): M7-13 revised | Agreed |
| Task 2 | M7-06 costs: spread both ways + Indian intraday charges 3.5 bps · M7-12 two tests, one recommendation · M7-13 Test 1 trades when expected gain beats this moment's cost (revised) · M7-14 Test 2 middle detail · M7-15 Test 1 measures, "enough value" = net > 0, beyond luck, most days positive | Agreed |
| Layout | M7-16 notebooks, final files, workbook, reports | Agreed |

## Plain-language standard for every output (user, 22 Nov 2026)
- Explanation columns are written for someone who has never seen an order book: no "OBI", "lean" or "bps" without saying what they mean.
- Money is shown in ₹ per ₹1 crore traded, beside any bps figure (1 bp of ₹1 crore = ₹1,000).
- The workbook's Read me has a column guide: every column of every task tab in one plain sentence.
- Each report finding opens with a one-sentence plain answer, then the detail.

## Task 1 — predict the next move
Exploration on the 14 training days → 15 inputs → OBI alone, logistic regression, random forest, LightGBM trained on days 1–14, compared on days 15–17, tested on days 18–20. The best model goes to Task 2 only if it beats OBI alone beyond luck on the test days.

## Hand-off: Task 1 → Task 2

| File | What it holds | How Task 2 must use it |
| --- | --- | --- |
| `outputs/task1/FINAL_M7_T1_direction_predictions.csv` | Each tuning- and test-day moment: chances of up / down / no move, the lean, what happened, every model's lean, why in words | Decide on the lean; score with the actual move only |
| `outputs/task1/key_numbers.json` (`task2_review`) | Expected-gain slope 7.09 bps per unit of lean; spread and no-move share by confidence | Sets each moment's expected gain in Test 1 |

**Task 1's review (step 7, M7-17):** the move caught grows with the lean, percentages are honest, and spreads are widest when the model is most confident → Test 1 compares expected gain with each moment's own cost.

## Task 2 — is it worth money?
- **Test 1 (trading on the signal):** trade when the expected gain (7.09 bps × the lean, from Task 1) beats that moment's spread + 3.5 bps of charges (revised M7-13); buy if the lean is positive, sell if negative, out 0.1 s later; luck check; by day; nearby margins; cost check; the old fixed cut-off for comparison.
- **Test 2 (timing the desk's own orders):** wait 0.1 s when the model expects the price to move against the order; saving vs placing now; luck check; buys vs sells; by stock; downside; ₹ a year per ₹100 crore of orders a day.
- **One recommendation** from both, and the hand-off to Module 9.

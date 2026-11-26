# The reusable code framework

**Purpose:** anyone can rerun every number in the report, locally or in Google Colab, and reuse the same pattern for a new dataset.

## The pattern every module follows

```text
data/*.csv ──► helpers/m0N_data.py (load, check, prepare; no leakage)
            ──► notebooks/m0N_taskK_*.ipynb (one task each, standard sections, seed 42)
            ──► outputs/taskK/FINAL_M<N>_T<K>_*.csv (final file, reasons in words) + key_numbers.json + charts
            ──► helpers/m0N_final_output.py ──► outputs/FINAL_M<N>_module_output.xlsx (the module's final output)
            ──► outputs/<last task>/module9_inputs.csv (the same fields for Module 9)
run_module_N.ipynb runs all of it in order; it must give the same files as the standalone notebooks.
```

## Standard notebook sections (task notebooks)
Each notebook uses the sections its task needs, from this list (the luck test is in Modules 1, 4, 5, 7 and 8): know the data · exploration · inputs · models compared against a simple benchmark · overfitting check · shuffled-label luck test · model choice with a plain-words factor table and 95% ranges · the finance case in ₹ · final test used once · calibration · does it hold everywhere (segments) · what the model relies on · what the results say · what goes to the next task · save.

## Shared code (project level)

| File | What it gives |
| --- | --- |
| `scripts/final_workbook.py` | `build_workbook()` (one standard workbook per module, column guide enforced), `handoff_row()`, `key_row()`, `action_row()`, `read_decisions()`, `evidence_index()`, the standard Module 9 fields `M9_INPUT_COLUMNS` |
| `scripts/md_to_pdf.py` | Markdown → PDF for the reports and this guide |
| `scripts/build_final_deliverables.py` | Builds the Final Report, this Code Guide and the PDF of every module and task report from the project's files |
| `module_0N_*/helpers/m0N_style.py` | One chart style everywhere (colour-blind-safe) |

## Reusing the framework for a new problem
1. Add `helpers/mXX_data.py` with `load_…()` and `data_report()`; list leakage columns explicitly.
2. Copy a task notebook's structure; keep the benchmark, the luck test, the overfitting check and the ₹ case.
3. Save a FINAL file with plain-language reasons, `key_numbers.json`, and `module9_inputs.csv` in the standard fields.
4. Write `helpers/mXX_final_output.py` with `build_workbook()`; describe every column in the column guide.
5. Add `run_module_XX.ipynb`; check runner = standalone, file by file.

<<PAGEBREAK>>

# How to run everything (HOW_TO_RUN.md)

This guide tells you what to install, how to run each part, what to look at afterwards, and what every file is for.

---

## 0. Start here: the final files

Each module has **one file to open first**, holding every task's final output, the key numbers, the Board actions, the hand-off, the decisions and an index of the supporting files (project decision P-21):

| Module | Open this first | Task final files (inside it, and in each task folder) |
| --- | --- | --- |
| 1 Corporate finance | `module_01_corporate_finance/outputs/FINAL_M1_module_output.xlsx` | `FINAL_M1_T1_business_unit_view.csv`, `FINAL_M1_T2_success_probability.csv`, `FINAL_M1_T3_initiative_decisions.csv` |
| 2 Credit risk | `module_02_credit_risk/outputs/FINAL_M2_module_output.xlsx` | `FINAL_M2_T1_default_predictions.csv`, `FINAL_M2_T2_risk_categories.csv`, `FINAL_M2_T3_loan_decisions.csv` |
| 3 Fraud detection | `module_03_fraud_detection/outputs/FINAL_M3_module_output.xlsx` | `FINAL_M3_T1_fraud_evidence.csv`, `FINAL_M3_T2_fraud_scores.csv`, `FINAL_M3_T3_anomaly_scores.csv`, `FINAL_M3_T4_transaction_decisions.csv` |
| 4 Customer analytics | `module_04_customer_analytics/outputs/FINAL_M4_module_output.xlsx` | `FINAL_M4_T1_churn_scores.csv`, `FINAL_M4_T2_customer_value.csv`, `FINAL_M4_T3_contact_list.csv` |
| 5 Equity markets | `module_05_equity_markets/outputs/FINAL_M5_module_output.xlsx` | `FINAL_M5_T1_return_predictions.csv`, `FINAL_M5_T2_stock_selections.csv` |
| 6 Portfolio optimisation | `module_06_portfolio_optimization/outputs/FINAL_M6_module_output.xlsx` | `FINAL_M6_A_portfolio_weights.csv`, `FINAL_M6_B_risk_summary.csv` |
| 7 High-frequency trading | `module_07_hft/outputs/FINAL_M7_module_output.xlsx` | `FINAL_M7_T1_direction_predictions.csv`, `FINAL_M7_T2_trade_decisions.csv` |
| 8 Derivatives | `module_08_derivatives/outputs/FINAL_M8_module_output.xlsx` | `FINAL_M8_T1_bs_benchmark.csv`, `FINAL_M8_T2_ml_pricing.csv` |
| 9 Capital allocation | `module_09_capital_allocation/outputs/FINAL_M9_module_output.xlsx` | `FINAL_M9_allocation.csv` |

- Every other file in `outputs/` is supporting evidence (listed in each workbook's Evidence index tab).
- The module reports (`reports/module_N_report.pdf`, also as `.md`) are the full explanation in words, with their charts. Every task report has a PDF too.

### The brief's final deliverables (`final_deliverables/`)

| File | What it is | Rebuild with |
| --- | --- | --- |
| `NovaFin_Final_Report.pdf` | Detailed report: executive summary, the financial decision framework, the evaluation criteria, the integrated allocation, module-wise methodology and results, risks and limitations, assumptions register and a short code summary | `python scripts/build_final_deliverables.py` |
| `NovaFin_Code_Guide.pdf` | The reusable Python/Colab code framework and how to run everything | same |
| `NovaFin_Board_Presentation.pptx` | The Board presentation (16 slides, native charts, speaker notes) | `python scripts/build_board_deck.py` |

All three are built from the modules' saved outputs, so they always match the notebooks. `build_final_deliverables.py` also rebuilds the PDF of every module and task report.

## 1. One-time setup

### Option A — on your own computer (what we use day to day)

1. Install Python 3.12 or 3.13 (we use 3.13 with Anaconda, which already includes Jupyter; with plain Python also run `pip install notebook`).
2. Unzip the project and open a terminal in the unzipped folder. The folder can have any name.
3. Install the libraries at the exact versions we tested:

```text
pip install -r requirements.txt
```

4. Check everything works: open `module_01_corporate_finance/run_module_1.ipynb` in Jupyter (or VS Code) and choose **Run all**. It should finish without errors in about 20 minutes (Task 2 takes most of it). For a quick check, run `module_06_portfolio_optimization/run_module_6.ipynb` instead: under a minute.

### Option B — Google Colab

1. Unzip the project and upload the whole unzipped folder to your Google Drive. The folder can have any name, anywhere up to three folders deep.
2. In Google Drive, open `run_novafin.ipynb` with Google Colab and choose **Run all**. Allow Google Drive access when asked: the first cell finds the project folder by itself.
3. The second cell installs the tested library versions. If Colab had already loaded another version, the session restarts once: choose **Run all** again.
4. A single module or task notebook runs the same way, on Colab's own library versions (results can differ slightly). For the tested versions, add this cell after the first one, then restart the session:

```text
%pip install -q -r {PROJECT_ROOT}/requirements.txt
```

You don't need a GPU for any part of the project.

---

## 2. Running the solution

There are three ways, and all give the same results. Way A installs the libraries itself; for B and C install them once first (section 1: `pip install -r requirements.txt`).

### A. Run the whole project: open `run_novafin.ipynb`

The project runner at the top level runs Modules 1 → 9 in order (each through its own runner, in its own folder), then rebuilds the final report, code guide and Board deck in `final_deliverables/`.

- Its first step installs the libraries from `requirements.txt` (a minute the first time, seconds after that), so no separate `pip install` is needed.
- **Run all** reproduces everything: about 2 hours (measured 24 Nov 2026: Module 1 ≈ 19 min, 2 ≈ 9, 3 ≈ 13, 4 ≈ 13, 5 ≈ 48, 6–9 ≈ 7 together).
- **On another computer** the results are the same, but saved files aren't byte-for-byte identical: in our test on a fresh install (24 Nov 2026) numbers differed by at most 0.000001, every key number was the same, and charts differed only in how the letters are drawn. A list of ties can print in another order.
- **Run one cell** reruns one module (it uses the other modules' saved outputs).
- Without opening it: `jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 run_novafin.ipynb`

### B. Run a whole module: open its runner notebook

Each module has one runner notebook in its folder, e.g. `module_01_corporate_finance/run_module_1.ipynb`.

- **Run all** runs the whole module in order: the data check, then Task 1, Task 2 and Task 3.
- **Run one cell** runs just that step.
- Each cell runs one task notebook in full and shows all its charts and main tables in the runner; the task notebook itself shows every table.

### C. Run one task: open its notebook

Every task notebook in `notebooks/` also runs on its own: open it and **Run all**. It loads everything it needs itself.

### What a task can need from another task (decision P-15)

| Kind | Example | How it is shared |
| --- | --- | --- |
| Data | the CSV | Each notebook loads it through the shared `helpers/mXX_data.py` |
| Code used by more than one task | derived columns, NPV formula | Lives in a helper in `helpers/`; each task imports it |
| A result one task produces | Task 2's P(Success) per initiative | Saved to a file in `outputs/taskN/`; the later task reads the file |

A task notebook never runs another task notebook; only the runner does that. If a task needs a result file that does not exist yet, its first cell stops and says which task to run first.

## 3. Suggested order to work through a task

For each task, read and run in this order:

1. `module_XX/docs/documentation.md`: what the brief asks, word for word, and what that means in plain language.
2. `module_XX/docs/approach.md`: how we solve it, step by step, with the formulas.
3. `module_XX/docs/decisions.md`: every choice we made and why.
4. `module_XX/notebooks/mXX_taskN_*.ipynb`: the task's full code, commented line by line, with each table and chart under the code that makes it.
5. `module_XX/helpers/`: the shared helpers the notebook imports (data loading; formulas used by more than one task).
6. `module_XX/reports/taskN_report.md`: the findings, with the charts.
7. `module_XX/reports/module_N_report.md`: the final report for the whole module, bringing the tasks together.
8. `module_XX/docs/progress.md`: the steps done, with dates.

---

## 4. What every file does

### Project level

| File / folder | Purpose | How to use |
| --- | --- | --- |
| **`run_novafin.ipynb`** | **Runs the whole project**: one cell per module (1 → 9, each running that module's runner in its own folder), then rebuilds the final report, code guide and Board deck. Run all takes about 2 hours (Module 5 ≈ 50 min, Module 1 ≈ 20 min); any single cell can be run on its own | Open, Run all; or without opening it: `jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 run_novafin.ipynb` |
| `scripts/` | Shared code and build scripts: `final_workbook.py`, `md_to_pdf.py`, `build_final_deliverables.py`, `build_board_deck.py` | Used by the runners |
| `project_docs/` | Project-wide documents: the brief and `decisions.md` | Read |
| `scripts/final_workbook.py` | Shared builder of every module's final output workbook (tabs, formatting, Decisions and Evidence index); called by each module's `helpers/mNN_final_output.py` in the runner's last cell | Used by the notebooks |
| `README.md` | Project overview, folder tree, data table | Read |
| `HOW_TO_RUN.md` | This guide | Read |
| `requirements.txt` | Library versions | Read |
| `data/` | All input CSV files. Read-only: never edited by code | Used by the notebooks |
| `project_docs/decisions.md` | Decisions that apply to every module (units, seed, structure, coding style) and the instructor's clarifications | Read |
| `project_docs/NovaFin_Group_Capstone_Project_CORRECTED.docx` | The brief | Read |
| `data/README.txt` | The instructor's original data-package readme (files, units, seed 42) | Read |

### Inside every module folder

| File / folder | Purpose |
| --- | --- |
| `run_module_N.ipynb` | The common place to run the module: one cell per step (data check, then each task), Run all or one cell |
| `docs/documentation.md` | The brief's text for the module (verbatim), plain explanation, data, required outputs, results, risks |
| `docs/approach.md` | Solution design per task: steps, methods, formulas |
| `docs/decisions.md` | The module's decisions, with options considered, evidence and status |
| `docs/progress.md` | Status of every step |
| `notebooks/` | One notebook per task, holding that task's full code: explanation, then commented code, then its table and chart |
| `helpers/` | Only code shared by several tasks or modules: `mXX_data.py` loads and checks the data, plus helpers such as `m01_finance.py` (NPV, used by Tasks 1 and 3) |
| `outputs/taskN/` | Saved results: tables (CSV), charts (PNG), key numbers (JSON) |
| `reports/taskN_report.md` | Written findings for the task, with its charts |

### Module 1 files

| File | What it does | Run with |
| --- | --- | --- |
| `helpers/m01_final_output.py` → `outputs/FINAL_M1_module_output.xlsx` | **The module's final output workbook** (open first): Read me, Key numbers, Board actions, every task's final file, Hand-off, Decisions, Evidence index | Runner's last cell, or `python module_01_…/helpers/m01_final_output.py` |
| `run_module_1.ipynb` | Runs Module 1: data check → Task 1 → Task 2 → Task 3, with every table and chart shown | Open, Run all (or one cell) |
| `helpers/m01_data.py` | Loads `strategic_initiatives.csv`, checks the columns, sets types, adds the derived columns used by Tasks 1 and 2; run directly it prints a health check | Runner cell 0, or `python module_01_corporate_finance/helpers/m01_data.py` |
| `helpers/m01_finance.py` | Cash flows, discount rate, NPV, Expected NPV, hurdle check, break-even life, Fund/Review/Reject rule. Run directly, it checks the worked example (initiative 1002) | `python module_01_corporate_finance/helpers/m01_finance.py` |
| `notebooks/m01_task1_eda.ipynb` | Task 1: setup, quality checks, one section per brief item (code, table, chart), Board view in ₹, what the results say. Saves to `outputs/task1/` | Runner cell 1, or open it and Run all |
| `outputs/task1/` | `0_quality_checks.csv`; `1_…` to `6_…` (a CSV and a PNG per brief item); `7_correlations.csv`; `key_numbers.json` | Created by Task 1 |
| `reports/task1_report.md` | Task 1 findings with the charts, and what they mean for Tasks 2 and 3 | Read (any Markdown viewer, e.g. VS Code preview) |
| `helpers/m01_style.py` | Shared chart style (colours, fonts) used by Task 1 and Task 2 | Imported by the notebooks |
| `notebooks/m01_task2_model.ipynb` | Task 2: 7 models compared over 25 cross-validation rounds, balancing comparison, model choice, ML and finance scorecard, rupee replay of each model's flag, shuffled-label check, odds ratios, lasso (inputs kept, path), SHAP, ranked drivers with business reasoning, reliability, ML and finance case. Saves to `outputs/task2/`, including `FINAL_M1_T2_success_probability.csv` for Task 3. About 19 minutes | Runner cell 2, or open it and Run all |
| `reports/task2_report.md` | Task 2 findings with the charts: which model, how good, what drives success | Read |
| `notebooks/m01_task3_decision.ipynb` | Task 3: NPV, Expected NPV, break-even life, hurdle; Fund / Review / Reject with reason, priority and funding condition; loss tolerance; sensitivity (three sources of P(Success), cut-off 4/5/6 years). Reads `outputs/task2/FINAL_M1_T2_success_probability.csv`; saves `outputs/task3/FINAL_M1_T3_initiative_decisions.csv`; step 10c: Module 9 inputs by business unit (`module9_inputs.csv`, `10c_business_unit_returns.csv`) | Runner cell 3, or open it and Run all (after Task 2 has run once) |
| `reports/task3_report.md` | Task 3 decisions with the charts: what to fund, review and reject, and what the ML adds | Read |
| `reports/module_1_report.md` | **The final Module 1 report**: the answer, how the three tasks connect, key decisions, hand-off to Module 9, limitations and glossary | Read first |

### Module 2 files

| File | What it does | Run with |
| --- | --- | --- |
| `helpers/m02_final_output.py` → `outputs/FINAL_M2_module_output.xlsx` | **The module's final output workbook** (open first): Read me, Key numbers, Board actions, every task's final file, Hand-off, Decisions, Evidence index | Runner's last cell, or `python module_02_…/helpers/m02_final_output.py` |
| `run_module_2.ipynb` | Runs Module 2: data check → Task 1 → Task 2 → Task 3, with every chart and the main tables shown | Open, Run all (or one cell) |
| `helpers/m02_data.py` | Loads `nova_loans.csv` and checks it; makes `Loan_ID` the identifier (uses `Loan_ID` if present, otherwise renames `Customer_ID`; the raw file is never edited); adds the four lending ratios; lists the 15 model inputs. Run directly, it prints a health check | Runner cell 0, or `python module_02_credit_risk/helpers/m02_data.py` |
| `helpers/m02_style.py` | Shared chart style (colours, fonts) for all Module 2 tasks | Imported by the notebooks |
| `notebooks/m02_task1_pd_model.ipynb` | Task 1: first look at the data in ₹; the 15 inputs and why Interest_Rate is the champion, not an input; 80/20 split; champion (interest rate) vs reference (credit score) vs five challengers over 25 cross-validation rounds; rebalancing evidence; overfitting check; selection rule; the ₹ case (losses at the same approval level, extra lending at the same default rate, mispriced loans); final test on 1,000 loans with bootstrap ranges and DeLong; Retail vs Corporate and sector risk (one model or one per segment?); weights, odds ratios, SHAP, example loans. About 9 minutes | Runner cell 1, or open it and Run all |
| `outputs/task1/` | Tables (CSV), 10 charts (PNG), `FINAL_M2_T1_default_predictions.csv` (PD per Loan_ID for Task 2), `chosen_model.joblib`, `chosen_model.json`, `key_numbers.json` | Created by Task 1 |
| `reports/task1_report.md` | Task 1 findings with the charts: champion vs challenger in ML terms and in ₹, what drives default | Read |
| `notebooks/m02_task2_pd_bands.ipynb` | Task 2: loads Task 1's PD for every loan; four calibration checks (Platt scaling only if needed); the brief's four bands tested (inside range, rising clearly, enough loans, economics) with a merge fallback; the bands in ₹; the scorecard's bands against the bank's. Reads `outputs/task1/FINAL_M2_T1_default_predictions.csv`. Under a minute | Runner cell 2, or open it and Run all (after Task 1 has run once) |
| `outputs/task2/` | `loan_pd.csv` (**the brief's deliverable**: Loan_ID, Predicted_PD, Risk_Category), `FINAL_M2_T2_risk_categories.csv` (for Task 3), tables, 4 charts, `key_numbers.json` | Created by Task 2 |
| `reports/task2_report.md` | Task 2 findings with the charts: calibration, the band tests, the bands in ₹, scorecard vs bank | Read |
| `notebooks/m02_task3_ecl_decision.ipynb` | Task 3 (step 11b adds Module 9 inputs: lending return and bad-year results per ₹, `module9_inputs.csv`): ECL = PD × 40% × loan amount for every loan; the Approve / Review / Reject rule (PD, ECL, loan size, collateral, risk appetite; borrower characteristics through the PD) with a reason and required rate per loan; the evidence for each part of the rule; the result in ₹ against today's book, checked on the 1,000 test loans; risk-appetite trade-off; cost-of-lending and LGD sensitivities; scorecard vs the bank's own price; concentration and results by segment; example loans. Reads `outputs/task2/FINAL_M2_T2_risk_categories.csv`. Under a minute | Runner cell 3, or open it and Run all (after Tasks 1 and 2 have run once) |
| `outputs/task3/` | `FINAL_M2_T3_loan_decisions.csv` (**the decision file**, one row per loan, no blanks or codes: Customer_Type, loan and collateral, PD and band, ECL, interest, expected return and required rate as numbers; every check in words; Decision; an action for each Review loan; full reason. Column guide in the Task 3 report §5.1), tables, 6 charts, `key_numbers.json` | Created by Task 3 |
| `reports/task3_report.md` | Task 3 findings with the charts: ECL, the rule and its evidence, the result in ₹, risk appetite, sensitivities, recommendation to the Board | Read |
| `reports/module_2_report.md` | **Module 2 final report**: the answer and actions for the Board, how the three tasks connect, cross-task conclusions, key decisions, hand-off to Module 9 | Read first |

### Module 3 files

| File | What it does | Run with |
| --- | --- | --- |
| `helpers/m03_final_output.py` → `outputs/FINAL_M3_module_output.xlsx` | **The module's final output workbook** (open first): Read me, Key numbers, Board actions, every task's final file, Hand-off, Decisions, Evidence index | Runner's last cell, or `python module_03_…/helpers/m03_final_output.py` |
| `run_module_3.ipynb` | Runs Module 3: data check → Task 1 → Task 2 → Task 3 → Task 4, with every chart and the main tables shown. About 13 minutes | Open, Run all (or one cell) |
| `helpers/m03_data.py` | Loads `nova_transactions.csv`, checks it and sorts it by time; `add_features()` adds the amount ratio, hour, weekday and device / city change (earlier transactions only). Run directly, it prints a health check | Runner cell 0, or `python module_03_fraud_detection/helpers/m03_data.py` |
| `helpers/m03_style.py` | Shared chart style (colours, fonts) for all Module 3 tasks | Imported by the notebooks |
| `notebooks/m03_task1_eda.ipynb` | Task 1: data checks and how the columns behave; fraud rate overall, in ₹ and by month; fraud by transaction type, amount (tenths and concentration), location, merchant category, customer behaviour, time of day and weekday; device and customer history; the evidence table (every column on the same yardsticks); Board view in ₹. Under a minute | Runner cell 1, or open it and Run all |
| `outputs/task1/` | `FINAL_M3_T1_fraud_evidence.csv` (**every column's evidence and verdict**, used by Task 2), 7 charts, `key_numbers.json` | Created by Task 1 |
| `reports/task1_report.md` | Task 1 findings with the charts: what drives fraud, with the evidence for every column, and where the ₹ lost to fraud sits | Read |
| `notebooks/m03_task2_supervised.ipynb` | Task 2: time split and leakage checks; amount alone (benchmark) vs logistic, lasso, decision tree, random forest and LightGBM on two input sets over 25 rounds; overfitting check; the agreed selection rule; the finance case (frauds and ₹ caught at every investigation budget, per 1,000 transactions); final test on 6,000 later transactions with bootstrap ranges; calibration (reported); SHAP and example transactions. About 11 minutes | Runner cell 2, or open it and Run all |
| `outputs/task2/` | `FINAL_M3_T2_fraud_scores.csv` (**each transaction's P(fraud)**, for Tasks 3 and 4), `cv_summary.csv` (the 25-round comparison), `chosen_model.joblib`, `chosen_model.json`, 5 charts, `key_numbers.json` | Created by Task 2 |
| `reports/task2_report.md` | Task 2 findings with the charts: which model and why, what it adds over the amount rule in ML terms and in ₹ | Read |
| `notebooks/m03_task3_isolation_forest.ipynb` | Task 3: Isolation Forest fitted on training transactions without the fraud label; the input tests (raw vs logged ₹, all columns, category encodings); settings and the unusual list; amount alone vs supervised vs Isolation Forest on 6,000 test transactions, in frauds and ₹; overlap; combining; SHAP reasons for every unusual transaction. Reads `outputs/task2/FINAL_M3_T2_fraud_scores.csv`. About 2 minutes | Runner cell 3, or open it and Run all (after Task 2 has run once) |
| `outputs/task3/` | `unusual_transactions.csv` (**the brief's deliverable**: each unusual transaction with its reasons in words), `FINAL_M3_T3_anomaly_scores.csv` (anomaly score for every transaction, for Task 4), `comparison.csv`, `isolation_forest.joblib` / `.json`, 4 charts, `key_numbers.json` | Created by Task 3 |
| `reports/task3_report.md` | Task 3 findings with the charts: what anomaly detection finds without the label, and how it compares with the supervised model and the amount rule | Read |
| `notebooks/m03_task4_cost_threshold.ipynb` | (Last step: Module 9 inputs in the standard fields, `module9_inputs.csv`.) Task 4: the threshold from the brief's costs (P(fraud) > 4.76%); calibration check around it; every cut-off tried on training; the real cost on 6,000 test transactions; the finance view (frauds at their real amount); how the line moves if the costs change. Reads Task 2's and Task 3's scores. Under a minute | Runner cell 4, or open it and Run all (after Tasks 2 and 3 have run once) |
| `outputs/task4/` | `FINAL_M3_T4_transaction_decisions.csv` (**the answer applied to every transaction**: Investigate / Let through with the expected cost each way), `threshold_summary.csv`, 2 charts, `key_numbers.json` | Created by Task 4 |
| `reports/task4_report.md` | Task 4 findings with the charts: the threshold, its cost and saving in ₹, the finance view, and the risks | Read |
| `reports/module_3_report.md` | **Module 3 final report**: the answer and actions for the Board, how the four tasks connect, cross-task conclusions, key decisions, hand-off to Module 9 | Read first |

### Module 4 files

| File | What it does | Run with |
| --- | --- | --- |
| `helpers/m04_final_output.py` → `outputs/FINAL_M4_module_output.xlsx` | **The module's final output workbook** (open first): Read me, Key numbers, Board actions, every task's final file, Hand-off, Decisions, Evidence index | Runner's last cell, or `python module_04_…/helpers/m04_final_output.py` |
| `reports/module_4_report.md` | **Module 4 final report**: the answer and actions for the Board, how the three tasks connect, cross-task conclusions, key decisions, hand-off to Module 9 | Read first |
| `run_module_4.ipynb` | Runs Module 4: data check → Task 1 → Task 2 → Task 3, with every chart and the main tables shown. About 13 minutes | Open, Run all (or one cell) |
| `helpers/m04_data.py` | Loads `nova_customers.csv` and checks it; `add_features()` adds the 5 business-based features; lists the 15 model inputs. Run directly, it prints a health check | Runner cell 0, or `python module_04_customer_analytics/helpers/m04_data.py` |
| `helpers/m04_style.py` | Shared chart style for all Module 4 tasks | Imported by the notebooks |
| `notebooks/m04_task1_churn.ipynb` | Task 1: each column tested; four models and a 115-input feature-engineering check over 25 rounds; each against 100 runs on shuffled labels; churners in the top 1,000 against random picking; rebalancing evidence; drivers. Every pass line's derivation is shown. About 12 minutes | Runner cell 1, or open it and Run all |
| `outputs/task1/` | `FINAL_M4_T1_churn_scores.csv` (each customer's chance of churn, labelled no better than chance, for Task 3), `model_tests.csv`, `evidence_table.csv`, `churn_model.joblib`, 2 charts, `key_numbers.json` | Created by Task 1 |
| `reports/task1_report.md` | Task 1 findings with the charts: whether churn can be predicted, and the evidence | Read |
| `notebooks/m04_task2_clv.ipynb` | Task 2: five regression models estimating CLV over 25 rounds; the CLV rule found from the data with each weight explained; where the value sits. About 1 minute | Runner cell 2, or open it and Run all |
| `outputs/task2/` | `FINAL_M4_T2_customer_value.csv` (**each customer's CLV and its sources**, for Task 3), `model_comparison.csv`, 3 charts, `key_numbers.json` | Created by Task 2 |
| `reports/task2_report.md` | Task 2 findings with the charts: how CLV is built, what drives it, what it leaves out | Read |
| `notebooks/m04_task3_prioritisation.ipynb` | (Last step: Module 9 inputs in the standard fields, `module9_inputs.csv`.) Task 3: the four groups (each with its actual churn rate), the 1,000 customers to contact, a back-test against other lists, and the call break-even. Under a minute; needs Tasks 1 and 2 | Runner cell 3, or open it and Run all |
| `outputs/task3/` | **`FINAL_M4_T3_contact_list.csv` (the 1,000 customers to contact, in call order, with the reason for each)**, `customer_groups.csv`, 2 charts, `key_numbers.json` | Created by Task 3 |
| `reports/task3_report.md` | Task 3 findings with the charts: the four groups, the 1,000 to contact, whether calling pays | Read |

### Module 5 files

| File | What it does | Run with |
| --- | --- | --- |
| `helpers/m05_final_output.py` → `outputs/FINAL_M5_module_output.xlsx` | **The module's final output workbook** (open first): Read me, Key numbers, Board actions, every task's final file, Hand-off, Decisions, Evidence index | Runner's last cell, or `python module_05_…/helpers/m05_final_output.py` |
| `run_module_5.ipynb` | Runs Module 5: data check → Task 1 → Task 2, with every table and chart shown. About 50 minutes | Open, Run all (or one cell) |
| `helpers/m05_data.py` | Loads `nova_market_data.csv` and checks it; month-end rebalance dates; the next-month return target; builds the 22 inputs and the monthly table (also used by Module 6). Run directly, it prints a health check | Runner cell 0, or `python module_05_equity_markets/helpers/m05_data.py` |
| `helpers/m05_style.py` | Shared chart style for all Module 5 tasks | Imported by the notebooks |
| `notebooks/m05_task1_returns.ipynb` | Task 1: what the data and its macro columns really contain; 22 inputs tested at three horizons; combinations of conditions; five ways of predicting, walk-forward over 43 months; each model against 100 runs on shuffled returns; what an IC is worth in ₹. About 50 minutes | Runner cell 1, or open it and Run all |
| `outputs/task1/` | `FINAL_M5_T1_return_predictions.csv` (**every model's predicted next-month return per stock and month**, for Task 2), `model_tests.csv`, `evidence_table.csv`, 3 charts, `key_numbers.json` | Created by Task 1 |
| `reports/task1_report.md` | Task 1 findings with the charts: whether any model predicts returns, and the evidence | Read |
| `notebooks/m05_task2_ranking.ipynb` | (Last step: Module 9 inputs in the standard fields, `module9_inputs.csv`.) Task 2: on every rebalance date, ranks the 15 stocks by each model's prediction, selects the top 5 and holds them equally; compares with holding all 15 and with 1,000 random picks; top 3 and 7 check; risk of 5 stocks vs 15; ₹; every strategy's top 5 for September 2026; quarterly and weighting checks. Under a minute; needs Task 1's outputs | Runner cell 2, or open it and Run all |
| `outputs/task2/` | `FINAL_M5_T2_stock_selections.csv` (**rank, selected, weight and reason per strategy, month and stock**), `portfolio_returns.csv` (monthly returns, for Module 6), `portfolio_summary.csv`, `september_2026_portfolio.csv` (**each strategy's picks for the latest rebalance date**), 3 charts, `key_numbers.json` | Created by Task 2 |
| `reports/task2_report.md` | Task 2 findings with the charts: whether the models' top picks beat holding all 15, and the answer to the committee | Read |
| `reports/module_5_report.md` | Module 5 in one place: the answer, both tasks, decisions, hand-offs to Module 6 and Module 9 | Read |

### Module 6 files

| File | What it does | Run with |
| --- | --- | --- |
| `helpers/m06_final_output.py` → `outputs/FINAL_M6_module_output.xlsx` | **The module's final output workbook** (open first): Read me, Key numbers, Board actions, every task's final file, Hand-off, Decisions, Evidence index | Runner's last cell, or `python module_06_…/helpers/m06_final_output.py` |
| `run_module_6.ipynb` | Runs Module 6: metrics check → Part A → Part B, with every table and chart shown. Under a minute. Needs Module 5's Task 1 outputs | Open, Run all (or one cell) |
| `helpers/m06_metrics.py` | All performance and risk measures (CAGR, volatility, Sharpe, Sortino, drawdown, Calmar, tracking error, information ratio, VaR, CVaR); 261-day year, 6.8% risk-free. Run directly, it self-tests | Runner cell 0, or `python module_06_portfolio_optimization/helpers/m06_metrics.py` |
| `helpers/m06_style.py` | Shared chart style for Module 6 | Imported by the notebooks |
| `notebooks/m06_partA_backtest.ipynb` | Part A: equal weight, Markowitz (past returns), ML (ridge forecasts in Markowitz) and Module 5's top 5; monthly backtest over 43 months with 0.15% costs; every measure, the luck test, cost and risk-free checks, ₹ | Runner cell A, or open it and Run all |
| `outputs/partA/` | `FINAL_M6_A_portfolio_weights.csv` (**ML predictions as an actual portfolio**: weights per strategy, month, stock), `daily_returns.csv` (for Part B and Module 9), `strategy_comparison.csv`, `cost_checks.csv`, 2 charts, `key_numbers.json` | Created by Part A |
| `reports/partA_report.md` | Part A findings with the charts | Read |
| `notebooks/m06_partB_risk.ipynb` | (Last step: Module 9 inputs in the standard fields, `module9_inputs.csv`.) Part B: VaR and CVaR (1 day, 1 month), bell-curve fit, stress tests (worst stretches; every stock −20%; real-market correlation) for all four strategies, in ₹ per ₹100 crore. Under a minute; needs Part A's outputs | Runner cell B, or open it and Run all |
| `outputs/partB/` | `FINAL_M6_B_risk_summary.csv` (**every strategy's risk figures in ₹, for Module 9**), `var_table.csv`, `stress_tests.csv`, 2 charts, `key_numbers.json` | Created by Part B |
| `reports/partB_report.md` | Part B findings with the charts | Read |
| **`outputs/FINAL_M6_module_output.xlsx` (Hand-off tab)** | **The final equity hand-off to Module 9, Modules 5 and 6 combined**: 16 figures with status, source, decision and how to use each | Created by Part B |
| `reports/module_6_report.md` | Module 6 in one place: the answer, both parts, decisions, hand-off to Module 9 | Read |

### Module 7 files

| File | What it does | Run with |
| --- | --- | --- |
| `helpers/m07_final_output.py` → `outputs/FINAL_M7_module_output.xlsx` | **The module's final output workbook** (open first): Read me with column guide, Key numbers, Board actions, Task 1 and Task 2 final files, Hand-off to Module 9, Decisions, Evidence index | Runner's last cell, or `python module_07_hft/helpers/m07_final_output.py` |
| `run_module_7.ipynb` | Runs Module 7: data check → Task 1 → Task 2 → workbook, with every table and chart shown. About 4 minutes | Open, Run all (or one cell) |
| `helpers/m07_data.py` | Loads and checks `nova_hft_orderbook.csv`; the day split; the 15 inputs; never uses Future_Return_100ms / Future_Price_100ms as inputs. Run directly, it prints a health check | Runner cell 0, or `python module_07_hft/helpers/m07_data.py` |
| `helpers/m07_style.py` | Shared chart style | Imported by the notebooks |
| `notebooks/m07_task1_direction.ipynb` | Task 1: exploration, 15 inputs, OBI alone vs logistic regression vs random forest vs LightGBM, test days with DeLong, overfitting check, by stock and day, shuffled-label luck test, model-choice factor table, honest percentages, NO_MOVE, what the model relies on, what Task 1 means for Task 2. About 3 minutes | Runner cell 1, or open it and Run all |
| `outputs/task1/` | `FINAL_M7_T1_direction_predictions.csv` (**each moment's chances, prediction, outcome and why in words**), `evidence_table.csv`, `model_tests.csv`, `model_drivers.csv`, 4 charts, `key_numbers.json` (incl. the review figures Task 2 reads) | Created by Task 1 |
| `notebooks/m07_task2_signal.ipynb` | Task 2 (step 5b adds Module 9 inputs, `module9_inputs.csv`): Test 1 (cost-aware trading on the signal after spread and charges; the old fixed cut-off for comparison), Test 2 (timing the desk's orders), luck checks, 95% ranges, by day and stock, cost check, recommendation. Under a minute; needs Task 1's outputs | Runner cell 2, or open it and Run all |
| `outputs/task2/` | `FINAL_M7_T2_trade_decisions.csv` (**each test moment: Test 1 trade and ₹ result, Test 2 wait-or-go and ₹ saving, reasons in words**), `test1_rules.csv`, 2 charts, `key_numbers.json` | Created by Task 2 |
| `reports/task1_report.md`, `task2_report.md`, `module_7_report.md` | Findings with charts, in plain language | Read |

### Module 8 files

| File | What it does | How to run |
| --- | --- | --- |
| `helpers/m08_final_output.py` → `outputs/FINAL_M8_module_output.xlsx` | **The module's final output workbook** (open first): Read me with column guide, Key numbers, Board actions, Task 1 and Task 2 final files, pricing by stock, hedging choices, hedge scenarios, choice rule, hedge by stock, Hand-off to Module 9, Decisions, Evidence index | Runner's last cell, or `python module_08_derivatives/helpers/m08_final_output.py` |
| `run_module_8.ipynb` | Runs Module 8: data check → Task 1 → Task 2 → workbook, with every chart and the main tables shown. About 3 minutes | Open, Run all (or one cell) |
| `helpers/m08_data.py` | Loads and checks `nova_options.csv`. Run directly, it prints a health check | Runner cell 0, or `python module_08_derivatives/helpers/m08_data.py` |
| `helpers/m08_black_scholes.py` | Black-Scholes prices and Greeks (delta, gamma, vega, theta) | Imported by the notebooks |
| `helpers/m08_style.py` | Shared chart style | Imported by the notebooks |
| `notebooks/m08_task1_bs_benchmark.ipynb` | Task 1: data, exploration, BS price and check, market vs BS in ₹ and %, where BS misses (tests), impossible prices, Greeks and the book's risk in ₹, what Task 1 means for Task 2. About 1 minute | Runner cell 1, or open it and Run all |
| `outputs/task1/` | `FINAL_M8_T1_bs_benchmark.csv` (**each option: BS vs market, gap in ₹ and %, flags, Greeks, why in words**), `gap_by_segment.csv`, `segment_tests.csv`, `book_risk_by_stock.csv`, `book_stress_scenarios.csv` (stock and volatility moves), `spot_check_by_stock.csv`, 4 charts, `key_numbers.json` | Created by Task 1 |
| `notebooks/m08_task2_ml_pricing.ipynb` | Task 2: direct and hybrid ML × 4 models (5-fold), overfitting check, factor table, test once vs BS with paired 95% ranges, by group and by stock, shuffled-correction test, what the models rely on, four hedging choices (none, delta, delta + half vega, delta + full vega): stress scenarios; step 9e: protecting Module 9's equity money with puts (`protect_equity_money.csv`, `module9_inputs.csv`); chance of loss over 100,000 simulated days, running costs, written-book check, choice rule on the 1-in-100 bad day, ₹, recommendation. About 2 minutes; needs Task 1's outputs | Runner cell 2, or open it and Run all |
| `outputs/task2/` | `FINAL_M8_T2_ml_pricing.csv` (**each test option: BS, direct ML, hybrid ML vs market, closest, why in words**), `model_comparison.csv`, `test_by_segment.csv`, `test_by_stock.csv`, `hedging_choices.csv` (4 hedging choices compared), `hedge_loss_chances.csv` and `hedge_loss_chances_written_book.csv` (how often and how badly each loses), `hedge_running.csv` (day-1 trades, cash, daily re-hedging), `hedge_vol_sensitivity.csv`, `hedging_choice_rule.csv`, `hedge_scenarios.csv` (21 scenarios × 4 choices), `hedge_by_stock.csv`, `model_drivers.csv`, 3 charts, `key_numbers.json` | Created by Task 2 |
| `reports/task1_report.md`, `task2_report.md`, `module_8_report.md` | Findings with charts, in plain language | Read |

### Module 9 files

| File | What it does | How to run |
| --- | --- | --- |
| `helpers/m09_final_output.py` → `outputs/FINAL_M9_module_output.xlsx` | **The final output workbook** (open first): allocation, plan vs alternatives, what the ML adds, growth path, decision framework, integration map, ML scorecard, evidence, optimiser, stress tests, leverage, governance, actions | Runner's last cell, or `python module_09_capital_allocation/helpers/m09_final_output.py` |
| `run_module_9.ipynb` | Evidence check → allocation notebook → workbook. Under a minute (needs Modules 1–8's outputs) | Open, Run all |
| `helpers/m09_data.py` | Reads every module's `module9_inputs.csv` and key numbers; health check when run directly | Runner cell 0 |
| `helpers/m09_style.py` | Chart style | Imported |
| `notebooks/m09_allocation.ipynb` | The allocation of ₹1,000 crore, steps 0–11 (7g: the capital plan, how the reserve is released) | Runner cell 1, or open it and Run all |
| `outputs/` | `FINAL_M9_allocation.csv` (**one row per category with the reason in words**), plan_vs_alternatives, ml_value_by_module, growth_path, financial_decision_framework, integration_map, ml_scorecard, evidence_all_modules, optimiser_comparison, stress_tests, lending_leverage_sensitivity, governance, actions (phased action plan), capital_plan_use_now, reserve_release_plan, capital_plan_stages (the capital plan, step 7g), 5 charts, key_numbers.json | Created by the notebook |
| `reports/module_9_report.md` | The allocation explained, in plain language | Read |

---

## 5. If something goes wrong

| Problem | Fix |
| --- | --- |
| `ModuleNotFoundError: lightgbm` (or another library) | `pip install -r requirements.txt` |
| `FileNotFoundError: ... data/...csv` | The `data/` folder must sit next to the module folders. Don't move the helper files out of `helpers/` |
| Strange characters instead of ₹ when running a script in a Windows terminal | Run `set PYTHONIOENCODING=utf-8` first (notebooks are not affected) |
| "Project folder not found" | Keep `run_novafin.ipynb`, `data/` and the module folders together in one folder; in Colab, put that folder in Google Drive (up to three folders deep) |
| A task says a result file is missing | Run the task it names first (e.g. Task 2 before Task 3), or Run all in the runner |


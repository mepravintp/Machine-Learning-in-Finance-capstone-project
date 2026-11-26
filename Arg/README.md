# NovaFin Group Capstone — ML-Driven Enterprise Financial Strategy

**Group 07:** Arg Ankit · Pravin Patil · Vineet Ojha · Pratik Saxena · Kshitiz Saxena

Machine Learning in Finance capstone. We act as Data & ML Strategy Consultants for NovaFin Group (a fictitious financial services company) and recommend how to deploy ₹1,000 crore of new capital, backed by ML models and financial analysis across 9 modules.

Brief followed: `project_docs/NovaFin_Group_Capstone_Project_CORRECTED.docx` (plus instructor clarifications of 16 Nov 2026, recorded in `project_docs/decisions.md`).

## Folder structure

```text
<project folder>/                     (any folder name works)
├── README.md                         ← this file
├── HOW_TO_RUN.md                     ← user guide: setup, how to run, what every file does
├── requirements.txt                  ← exact library versions (works locally or in Colab)
├── data/                             ← all CSV files (read-only inputs) and the instructor's README.txt
├── run_novafin.ipynb                 ← RUN THE WHOLE PROJECT: Modules 1 → 9, then the final report, code guide and Board deck
├── final_deliverables/               ← NovaFin_Final_Report.pdf, NovaFin_Code_Guide.pdf, NovaFin_Board_Presentation.pptx
├── scripts/                          ← shared code and build scripts (workbook builder, report/PDF and Board deck builders)
├── project_docs/
│   ├── NovaFin_Group_Capstone_Project_CORRECTED.docx  ← the brief
│   └── decisions.md                  ← decisions that affect several modules; instructor clarifications
├── module_01_corporate_finance/
│   ├── run_module_1.ipynb            ← run the module: one cell per step; Run all or one cell
│   ├── docs/
│   │   ├── documentation.md          ← brief text for the module (verbatim), plain explanation, outputs, results
│   │   ├── approach.md               ← solution design: steps, methods, formulas, validation
│   │   ├── decisions.md              ← decisions for this module, with evidence
│   │   └── progress.md               ← task-by-task status
│   ├── notebooks/                    ← one notebook per task: full commented code + tables + charts (local or Colab)
│   ├── helpers/                      ← only code shared by several tasks/modules (data loading, formulas)
│   ├── outputs/taskN/                ← tables (CSV), charts (PNG), key numbers (JSON)
│   └── reports/                      ← taskN_report per task, and module_N_report: the final module report (each as .pdf with its charts, and .md)
├── module_02_credit_risk/            ← same layout in every module
├── module_03_fraud_detection/
├── module_04_customer_analytics/
├── module_05_equity_markets/
├── module_06_portfolio_optimization/
├── module_07_hft/
├── module_08_derivatives/
└── module_09_capital_allocation/
```

## Data files (`data/`)

| File | Module | Rows | Note |
| --- | --- | --- | --- |
| strategic_initiatives.csv | 1 | 180 | money in ₹ lakh |
| nova_loans.csv | 2 | 5,000 | money in plain rupees |
| nova_transactions.csv | 3 | 30,000 | money in plain rupees |
| nova_customers.csv | 4 | 5,000 | money in plain rupees |
| nova_market_data.csv | 5, 6 | 21,855 | prices in rupees per share |
| nova_hft_orderbook.csv | 7 | 120,000 | unzipped from nova_hft_orderbook.zip |
| nova_options.csv | 8 | 10,000 | prices in rupees per share |
| nova_liquidity.csv | — | 1,216 | out of scope (instructor clarification); kept only for completeness |

## Running the code

**1. Install the libraries (once).** Not needed if you use `run_novafin.ipynb`: its first step installs them. Needed before running a module or task notebook on its own:

```text
pip install -r requirements.txt
```

**2. Run the whole project:** open **`run_novafin.ipynb`** (top level) and **Run all**.
- Its first step installs the libraries from `requirements.txt`, so nothing needs installing beforehand.
- It runs Modules 1 → 9 in order, each through its own runner, then rebuilds the final report, code guide and Board deck in `final_deliverables/`.
- Takes about 2 hours (Module 5 ≈ 50 min, Module 1 ≈ 20 min, Module 2 ≈ 9 min, Modules 3 and 4 ≈ 13 min each, Modules 6–9 ≈ 7 min together).
- Or without opening it: `jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 run_novafin.ipynb`

**3. Run one module or one task (optional):**
- One module: open `module_0N_*/run_module_N.ipynb` and Run all (or run a single cell for one step).
- One task: open a notebook in `module_0N_*/notebooks/` and Run all.
- Running one module on its own uses the other modules' saved outputs, so the order only matters when rerunning everything.

**Google Colab:** unzip, upload the whole project folder to Google Drive, open `run_novafin.ipynb` with Google Colab and **Run all**. Every notebook finds the project folder by itself, whatever it is called. If the first step updates a library, the session restarts once: choose **Run all** again. Random seed 42 everywhere.

**Already run:** every chart, table, report and workbook is saved in the folder, so nothing has to be run to read the results.

Full instructions, and what every file does: `HOW_TO_RUN.md`.

## Deliverables (from the brief) — in `final_deliverables/`

1. Detailed Report + Code Guide — "includes the complete report structure, module-wise methodology, reusable Python/Colab code framework, financial decision framework" → `NovaFin_Final_Report.pdf`, `NovaFin_Code_Guide.pdf`.
2. Final Group Presentation — "just the same assuming you are presenting to the board" → `NovaFin_Board_Presentation.pptx`.

Each module's results are in its workbook `module_0N_*/outputs/FINAL_MN_module_output.xlsx` (open first) and its report `module_0N_*/reports/module_N_report.md`.

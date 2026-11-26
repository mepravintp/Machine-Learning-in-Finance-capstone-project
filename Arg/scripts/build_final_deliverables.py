"""
Final deliverables: the Final Report and the Code Guide, and the module and task reports (PDF)
=============================================================================================

WHAT THIS FILE DOES
    Assembles the brief's final "asks" from the project's own files, so every number matches the
    notebooks' saved outputs:
      1. final_deliverables/NovaFin_Final_Report.pdf — executive summary, the Board's answer, the financial
         decision framework, how the work meets each evaluation criterion, module-wise methodology and results
         (from each module report), the integrated allocation (Module 9), risks and limitations, the assumptions
         register (from every module workbook) and a short summary of the code framework. Charts are embedded.
      2. final_deliverables/NovaFin_Code_Guide.pdf — the reusable Python/Colab code framework and how to run it
         (HOW_TO_RUN.md plus the framework overview).
      3. module_0N_*/reports/*.pdf — a PDF of every module and task report, with its charts inside, so the charts show
         in any PDF viewer (a plain text editor shows a .md file without its charts).

HOW TO USE
    python scripts/build_final_deliverables.py          (after Modules 1–9 have run)
"""
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from md_to_pdf import build_pdf   # noqa: E402

OUT = ROOT / "final_deliverables"
OUT.mkdir(exist_ok=True)
M9 = ROOT / "module_09_capital_allocation"
MODS = {1: ("module_01_corporate_finance", "Corporate finance: strategic initiatives"), 2: ("module_02_credit_risk", "Credit risk"),
        3: ("module_03_fraud_detection", "Fraud detection"), 4: ("module_04_customer_analytics", "Customer analytics"),
        5: ("module_05_equity_markets", "Equity markets"), 6: ("module_06_portfolio_optimization", "Portfolio optimisation and risk"),
        7: ("module_07_hft", "High-frequency trading"), 8: ("module_08_derivatives", "Derivatives")}
# charts shown in chapter 4 besides those in a module report's section 1 (modules whose section 1 has only the decision chart)
KEY_CHARTS = {1: ["6_model_comparison.png"], 2: ["04_cv_comparison.png", "task2/01_calibration.png"],
              3: ["03_catch_curves.png"]}
GROUP = "Group 07"
TEAM = "Arg Ankit · Pravin Patil · Vineet Ojha · Pratik Saxena · Kshitiz Saxena"
TODAY = "24 November 2026"      # the version date printed on the cover (fixed, so a rebuild with the same content is identical)


def section(text: str, start: str, stop_pattern: str = r"^## ") -> str:
    """The Markdown from heading `start` up to the next heading matching `stop_pattern` (same level)."""
    lines = text.splitlines()
    i = next(k for k, l in enumerate(lines) if l.strip().startswith(start))
    j = next((k for k in range(i + 1, len(lines)) if re.match(stop_pattern, lines[k])), len(lines))
    return "\n".join(lines[i + 1:j]).strip()


def rel(p: Path) -> str:
    """A path relative to final_deliverables/, so the Markdown's images show on any computer and on GitHub."""
    return Path(os.path.relpath(Path(p).resolve(), OUT.resolve())).as_posix()


def fix_images(md: str, report_dir: Path) -> str:
    """Re-point image paths in a module report (relative to its reports/ folder) to final_deliverables/."""
    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", lambda m: f"![{m.group(1)}]({rel(report_dir / m.group(2))})", md)


def demote(md: str, by: int = 1) -> str:
    """Push headings down a level so a module's sections sit under its chapter heading."""
    return re.sub(r"^(#{1,3}) ", lambda m: "#" * min(len(m.group(1)) + by, 4) + " ", md, flags=re.M)


def table(df: pd.DataFrame, d: int = None) -> str:
    """A DataFrame as a Markdown table; with d, every number gets d decimals and a true minus sign."""
    show = lambda v: str(v) if d is None or not isinstance(v, float) else f"{v + 0.0:,.{d}f}".replace("-", "−") if abs(v) >= 0.5 * 10 ** -d else f"{0:.{d}f}"
    cells = lambda r: "| " + " | ".join(show(v).replace("|", "/").replace("\n", " ") for v in r) + " |"
    return "\n".join([cells(df.columns), "| " + " | ".join("---" for _ in df.columns) + " |"] + [cells(r) for r in df.itertuples(index=False)])


def handoff_assumptions(n: int, mod: str) -> str:
    """The 'Assumptions behind these figures' row of a module workbook's Hand-off tab."""
    f = ROOT / mod / "outputs" / f"FINAL_M{n}_module_output.xlsx"
    raw = pd.read_excel(f, sheet_name="Hand-off", header=None)
    hdr = raw.index[raw.apply(lambda r: "Figure" in r.values, axis=1)][0]
    h = pd.read_excel(f, sheet_name="Hand-off", header=hdr)
    row = h[h.Figure.astype(str).str.startswith("Assumptions")]
    return str(row.Value.iloc[0]) if len(row) else "—"


CODE_FRAMEWORK = """# The reusable code framework

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
"""


# ------------------------------------------------------------------------------------------- report
m9 = (M9 / "reports" / "module_9_report.md").read_text(encoding="utf-8")
K9 = json.loads((M9 / "outputs" / "key_numbers.json").read_text(encoding="utf-8"))
fw = pd.read_csv(M9 / "outputs" / "financial_decision_framework.csv").set_index("Module")
sc = pd.read_csv(M9 / "outputs" / "ml_scorecard.csv").set_index("Module")
acts = pd.read_csv(M9 / "outputs" / "actions.csv")
use_now = pd.read_csv(M9 / "outputs" / "capital_plan_use_now.csv")
release = pd.read_csv(M9 / "outputs" / "reserve_release_plan.csv")
stages = pd.read_csv(M9 / "outputs" / "capital_plan_stages.csv")
CP9 = K9["capital_plan"]
LGD60 = "Bad year if collateral also fetches less, LGD 60% (₹ crore)"
RISK_A = K9["initiatives_crore"] - sum(K9["by_category_crore"][c] for c in ["Corporate lending", "Retail lending", "Digital banking", "Wealth management"])   # Risk Analytics initiatives, inside Derivatives hedging
HEDGE = K9["by_category_crore"]["Derivatives hedging"] - RISK_A                                                                 # the put and the option-book hedge
assert abs(K9["equities_crore"] + K9["initiatives_crore"] + 5 + HEDGE + K9["reserve_crore"] - 1000) < 0.01                           # the headline adds to ₹1,000 crore
m9 = fix_images(m9, M9 / "reports")                                   # Module 9's charts, re-pointed to final_deliverables/
answer9 = section(m9, "## 1. The answer")
one_line = answer9.splitlines()[0]

parts = [f"""# Executive summary for the Board

**The Board's question:** "How should NovaFin use ML to grow its business while maintaining acceptable levels of credit, fraud, market, liquidity and derivatives risk?", and with ₹1,000 crore of new capital: "Where should NovaFin deploy its capital, what risks will it take, and how should those risks be controlled?"

{one_line}

{table(pd.read_csv(M9 / "outputs" / "FINAL_M9_allocation.csv")[["Category", "₹ crore", "Expected ₹ crore a year", "Bad-year result (₹ crore)", "Owner"]], 2)}

The bad-year column is each category's own bad year. Initiatives total ₹{K9["initiatives_crore"]:.1f} crore: the Corporate, Retail, Digital and Wealth rows, plus ₹{RISK_A:.1f} crore of Risk Analytics inside Derivatives hedging (whose other ₹{HEDGE:.1f} crore is the put and the option-book hedge).

![The allocation]({rel(M9 / "outputs" / "02_allocation.png")})

**Why this, and not the bank's current way?**

{table(pd.read_csv(M9 / "outputs" / "plan_vs_alternatives.csv"), 1)}

**What the ₹100 crore bad-year budget is:** a loss limit, not an amount we allocate. It is the most the whole ₹1,000 crore plan may lose in one bad year (10%). The brief gives no figure ("acceptable levels of" risk), so 5%, 10% and 15% were considered and 10% was agreed (M9-10). All ₹1,000 crore is allocated; the ₹100 crore reserve floor below is a different rule that happens to be the same size.

**The capital plan, part 1: what we put to work now**

{table(use_now[["Use", "₹ crore", "Expected ₹ crore a year", "Bad-year result (₹ crore)", "Owner", "First action and when"]], 1)}

**The capital plan, part 2: how the ₹638 crore reserve is released.** The reserve is a waiting room, not idle money: it earns ₹{CP9["reserve_earns_crore"]:.1f} crore a year while it waits, and each step moves only when its test passes. Releasing the loans today, at today's prices, would cost ₹{CP9["cost_release_now_crore"]:.1f} crore a year.

{table(release.assign(**{"Release": release.Release.replace("Future initiatives", "Future initiatives (up to)"), "₹ crore": [f"{v:.0f}" for v in release["₹ crore"]]})[["Step", "Release", "₹ crore", "Released when (the test)", "Checked", "Owner", "If the test fails"]])}

**The capital plan, part 3: what each stage changes (profit, growth, risk)**

{table(stages[["Stage", "Liquidity reserve (₹ crore)", "Loan book (₹ crore)", "Money working in NovaFin's businesses (₹ crore)", "Profit a year (₹ crore)", "Profit a year, bank view (₹ crore)", "Bad year, all at once (₹ crore)", "Bad year if collateral also fetches less, LGD 60% (₹ crore)", "Profit above the bank's way (₹ crore a year)"]], 1)}

Profit never falls: re-priced loans are planned at exactly the 6.8% hurdle, so lending earns what the reserve did, and the business grows; the bank view (deposits fund 88% of each loan at 5%) adds the profit leverage gives. Step 3 assumes future initiatives perform like today's. The bad year uses at most a third of the ₹100 crore loss limit; if collateral also fetches less (LGD 60%: a defaulted loan loses 60% instead of 40%), it reaches −₹{-stages.iloc[3][LGD60]:.1f} crore after step 3, still inside it.

![The capital plan by stage]({rel(M9 / "outputs" / "05_capital_plan.png")})

**The action plan we ask the Board to approve (phased):**

{table(acts)}

<<PAGEBREAK>>

# How this report meets the brief's evaluation criteria

| Criterion (brief) | Where it is shown | In one line |
| --- | --- | --- |
| **Technically sound ML** | Chapter 4 (each module) and the ML scorecard (chapter 3.3) | Every model is tested against a simple benchmark on data it never saw. Shuffled-label luck test: Modules 1, 4, 5, 7 and 8; Modules 2 and 3 use paired 95% ranges over 25 rounds and a held-out test instead. Check of training against unseen scores (overfitting): Modules 1, 2, 3, 7 and 8. Models that win drive decisions; Module 1's weak one only screens slow payers (36 into Reject; the risk rating alone gives a similar list) |
| **Strong financial reasoning** | Chapter 2 (framework), every module's ₹ metric, chapter 3 | Every module's result becomes ₹ (NPV, ECL, cost of fraud, CLV, return after costs, Black-Scholes); every use of the ₹1,000 crore faces a 6.8% hurdle and a bad-year test |
| **Rigorous validation** | ML scorecard; each module's checks; reproducibility | Out-of-sample and time-ordered tests, shuffled-label luck tests (Modules 1, 4, 5, 7, 8), calibration, DeLong, paired 95% ranges; seed 42; every runner gives the same files as its notebooks |
| **Integrated decision-making across modules** | Chapter 3.2 (integration map), Module 9 inputs | All modules hand over the same fields; one ranking decides the ₹1,000 crore; results pass between modules (e.g. Module 6's risk prices Module 8's put) |
| **Excellent executive communication** | This summary, the Board deck, every module's workbook | Answer first, ₹ throughout, plain words, actions with owners |
| **Financial decision framework** (brief's 'asks') | Chapter 2 | Six steps from data to control, applied in every module |
| **Detailed report, module-wise methodology** (brief's 'asks') | Chapters 4 to 6; each module's full report is in the code folder | Method, models, results, decisions, limitations and charts, module by module |
| **Code Guide, reusable Python/Colab code framework** (brief's 'asks') | Chapter 7; the Code Guide is a separate PDF, `final_deliverables/NovaFin_Code_Guide.pdf` in the code folder | How the code is built, how to run it anywhere, what every file does |

# 1. The approach: from data to decision

The Board asked for "an integrated answer", not "a collection of isolated ML models". Every module follows the brief's chain **Data → ML prediction → Financial metric → Risk assessment → Business decision**, and Module 9 combines them:

```text
Modules 1–8:  data → model (validated) → ₹ metric → bad-year test → decision rule → owner and control
                                       ↓  the same fields from every module ("Module 9 inputs")
Module 9:     return per ₹ vs the 6.8% hurdle → best uses first within limits → stress tests → governance → actions
```

# 2. The financial decision framework
{section(m9, "## 2. The financial decision framework")}

<<PAGEBREAK>>

# 3. Integrated capital allocation (Module 9)

## 3.1 The answer
{demote(answer9, 1)}

## 3.2 Integrated decision-making: how the modules feed each other
{section(m9, "## 3. Integrated decision-making")}

## 3.3 Sound ML, validation and explainability
{section(m9, "## 4. Sound ML")}

## 3.4 Method, comparison and the lending sensitivity
{section(m9, "## 5. Method and comparison")}

## 3.5 Governance and controls
{section(m9, "## 6. Governance and controls")}

<<PAGEBREAK>>

# 4. Module-wise methodology and results
Each module below shows its method on the six framework steps, its ML verdict, and its own summary. **Where a § number appears (e.g. §5.4), it points to that section of the module's full report, `reports/module_N_report.pdf` in that module's folder.** File names refer to the project's code folder, submitted as the ZIP.
"""]

for n, (mod, name) in MODS.items():
    rep = (ROOT / mod / "reports" / f"module_{n}_report.md").read_text(encoding="utf-8")
    key = next(k for k in fw.index if k.startswith(f"{n} "))
    steps = fw.loc[key]
    method = table(pd.DataFrame({"Step": steps.index, "In this module": steps.values}))
    scrow = next((k for k in sc.index if k.startswith(f"{n} ")), None)
    ml = "" if scrow is None else table(sc.loc[[scrow]].reset_index()[["Predicts", "Models compared (and benchmark)", "Result on unseen data", "Verdict", "Validation", "Used in the allocation?"]])
    brief = fix_images(demote(section(rep, "## 1. The answer in brief"), 2), ROOT / mod / "reports")
    images = re.findall(r"!\[[^\]]*\]\([^)]+\)", rep)
    more = [next(i for i in images if i.split("](")[1].rstrip(")").endswith(k)) for k in KEY_CHARTS.get(n, [])]
    key_charts = "" if not more else "**Evidence behind the model** (" + " ".join(re.match(r"!.([^]]*)]", i).group(1) for i in more) + ")\n\n" + fix_images("\n\n".join(more), ROOT / mod / "reports")
    parts.append(f"""{"<<PAGEBREAK>>" if n > 1 else ""}

## 4.{n} Module {n}: {name}

**Method (the six framework steps):**

{method}

{"**ML verdict:**" if ml else ""}

{ml}

**Summary from the module report:**

{brief}

{key_charts}
""")

lim_rows = []
for n, (mod, name) in MODS.items():
    rep = (ROOT / mod / "reports" / f"module_{n}_report.md").read_text(encoding="utf-8")
    head = next((l for l in rep.splitlines() if re.match(r"^## \d+\. (Risks and )?[Ll]imitations", l)), None)
    lim = section(rep, head) if head else ""
    lim_rows.append(f"### Module {n}: {name}\n\n{demote(lim, 2)}\n")
assump = pd.DataFrame([{"Module": f"{n} {name}", "Assumptions behind the hand-off figures": handoff_assumptions(n, mod)} for n, (mod, name) in MODS.items()])

parts.append(f"""<<PAGEBREAK>>

# 5. Risks and limitations

| Type | What it means here | How we handled it |
| --- | --- | --- |
| **Data limitations** | The datasets are synthetic: stocks move independently, every option on a stock has its own price, there is no cost of funds, recovery or fee-revenue data, and the files can't be linked across businesses | Real-market risk added as stress estimates; gaps marked as assumptions in every module's hand-off; scenarios set by hand in Module 9 |
| **Model risk** | Some models are weak (P(Success), ROC-AUC 0.58) or show no skill (churn, returns, ML option pricing) | Full use only where they beat a benchmark beyond luck; the weak one only screens slow payers; no-skill ones not used |
| **Short histories** | 43 months of equities, 3 test days of HFT, one pricing day of options | Ranges and luck tests reported; pilots and staged releases instead of full commitments |
| **Assumption risk** | Risk-free 6.8%, LGD 40%, trading costs, the ₹100 crore bad-year budget (10%) | Sensitivities in each module; Module 9 stress tests and reverse stress |

{"".join(lim_rows)}

<<PAGEBREAK>>

# 6. Assumptions register (from every module's hand-off)

{table(assump)}

Module 9's own assumptions: risk-free 6.8%; ₹1 of capital = ₹1 deployed (the leveraged bank view as a sensitivity); no data links the businesses, so stress scenarios are set by hand; the HFT pilot is planned at 0%; re-priced loans keep the same borrowers.

<<PAGEBREAK>>

# 7. The code framework (summary; the full guide is the separate Code Guide)

| Layer | What it is | Files |
| --- | --- | --- |
| Data helpers | Load, check and prepare each dataset; leakage columns never used as inputs | `module_0N_*/helpers/m0N_data.py` |
| Task notebooks | One per task, with the sections that task needs, from: data, exploration, inputs, models, overfitting, luck test, model choice, ₹ case, test once, calibration, segments, drivers, findings, hand-off, save | `module_0N_*/notebooks/*.ipynb` |
| Final output builders | One workbook per module (Read me with column guide, key numbers, Board actions, task tabs, hand-off, Module 9 inputs, decisions, evidence index) | `scripts/final_workbook.py`, `module_0N_*/helpers/m0N_final_output.py` |
| Runners | Run a whole module in order, locally or in Colab; give the same files as the standalone notebooks | `module_0N_*/run_module_N.ipynb` |
| Final deliverables | This report and the Code Guide, built from the project's files | `scripts/build_final_deliverables.py`, `scripts/md_to_pdf.py` |

Reproducibility: seed 42 in every random step; each runner was checked file by file against the standalone notebooks on our computer. A fresh install of the libraries gave the same key numbers (differences of at most 0.000001, from a different maths library).
""")

report_md = "\n".join(parts)
(OUT / "NovaFin_Final_Report.md").write_text(report_md, encoding="utf-8")
build_pdf(report_md, OUT / "NovaFin_Final_Report.pdf", "NovaFin Group — ML-Driven Enterprise Financial Strategy, Risk & Decision Support",
          f"Final report to the Board · capital allocation of ₹1,000 crore · {TODAY}", OUT, f"{GROUP} · NovaFin capstone · Final report", f"{GROUP}: {TEAM}", img_cm=7.4)

# ------------------------------------------------------------------------------------------- code guide
howto = (ROOT / "HOW_TO_RUN.md").read_text(encoding="utf-8")
howto = re.sub(r"^# .*\n", "", howto, count=1)
guide_md = f"""{CODE_FRAMEWORK}
<<PAGEBREAK>>

# How to run everything (HOW_TO_RUN.md)
{howto}
"""
(OUT / "NovaFin_Code_Guide.md").write_text(guide_md, encoding="utf-8")
build_pdf(guide_md, OUT / "NovaFin_Code_Guide.pdf", "NovaFin Group — Code Guide",
          f"Reusable Python / Colab code framework and how to run it · {TODAY}", ROOT, f"{GROUP} · NovaFin capstone · Code guide", f"{GROUP}: {TEAM}")
# ------------------------------------------------------------------------------------------- module and task reports
reports = sorted(ROOT.glob("module_0*/reports/*_report.md"))
for f in reports:
    n, text = int(f.parts[-3][7:9]), f.read_text(encoding="utf-8")
    title = re.match(r"# (.+)", text).group(1).strip()
    body = re.sub(r"^## Final report\n", "", re.sub(r"^# .*\n", "", text, count=1), count=1, flags=re.M)
    body = re.sub(r"^(#{2,4}) ", lambda m: m.group(1)[1:] + " ", body, flags=re.M)      # the title is on the cover, so headings move up a level
    build_pdf(body, f.with_suffix(".pdf"), title, f"Module {n} report · {TODAY}" if f.stem.startswith("module_") else f"Module {n} task report · {TODAY}",
              f.parent, f"{GROUP} · NovaFin capstone · {title}", f"{GROUP}: {TEAM}")
print(f"Saved: NovaFin_Final_Report.pdf and NovaFin_Code_Guide.pdf in final_deliverables/, and {len(reports)} module and task report PDFs")

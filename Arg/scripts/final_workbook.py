"""
Final output workbook — shared builder for every module
=======================================================

WHAT THIS FILE DOES
    Writes one Excel workbook per module, FINAL_M<n>_module_output.xlsx, in the module's outputs/ folder.
    It is the single place where Module 9, the Board, the presenter and the evaluator see everything a
    module produced, in numbers and short text (project decision P-21). The module reports remain the
    full explanation in words.

    Every workbook has the same tabs, in this order:
        1 Read me        the brief's question, the answer, which tab to read for what, a column guide (every
                         column of every task tab in one plain sentence)
        2 Key numbers    the headline figures: value, unit, what it means, good or bad, how it was worked out
        3 Board actions  the recommendations, each with its ₹ effect and evidence
        T1, T2 …         each task's final output file, all rows and columns
        Hand-off         what the next module needs; each figure points to the tab, column(s) and rows behind it
        Decisions        every agreed decision (read from docs/decisions.md)
        Evidence index   every supporting output file: what it shows, which notebook step made it

    The module-specific content (answer, key numbers, actions, hand-off rows) lives in each module's
    helpers/mNN_final_output.py, which calls build_workbook() here. Figures in the hand-off are computed
    from the task files' rows wherever the recipe says so, so the pointers are always true.

HOW TO USE
    from final_workbook import build_workbook
    build_workbook(module_dir, number=4, read_me=..., key_numbers=df, board_actions=df,
                   task_tabs=[("T1 churn scores", path, "about this tab"), ...], handoff=df, receiver="Module 9")
"""
import json
import re
from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from repeatable import normalise_office_file   # fixed stored times: a rebuild with the same content is byte-identical

HEADER_FILL = PatternFill("solid", fgColor="1F3A5F")      # dark blue header row
TITLE_FONT = Font(bold=True, size=13)
HEADER_FONT = Font(bold=True, color="FFFFFF")
WRAP = Alignment(wrap_text=True, vertical="top")

HANDOFF_COLUMNS = ["Figure", "Value", "Unit", "Status", "Detail tab", "Detail column(s)", "How it comes from the rows",
                   "Decision", "How the receiving module should use it"]
# The same fields for every business category, so Module 9 can compare them side by side (project rule, 22 Nov 2026)
M9_INPUT_COLUMNS = ["Category", "What NovaFin would put money into", "Return per ₹ deployed (% a year)", "Return range (% a year)",
                    "Bad-year result per ₹ (% a year)", "How the bad year is defined", "Capacity (₹ crore)", "Evidence strength",
                    "How fast the money can come back", "Data gap or assumption", "Controls", "Detail tab", "Detail column(s)", "Decision"]
STATUS_LEGEND = [
    ("Measured", "Computed from this data (the test rows, months or transactions)."),
    ("Stress estimate", "Computed under an assumption that is not in the data (for example, stocks moving together like real ones)."),
    ("Assumption", "An input we chose and stated (for example, a cost per investigation or a trading cost)."),
    ("Conclusion", "The answer reached across the module's tasks."),
]


# ---------------------------------------------------------------------------------------------
# Decisions: read the markdown table in docs/decisions.md
# ---------------------------------------------------------------------------------------------
def read_decisions(module_dir: Path) -> pd.DataFrame:
    """Turn the markdown decisions table into rows. Bold/italic markers are removed for Excel."""
    lines = [l for l in (module_dir / "docs" / "decisions.md").read_text(encoding="utf-8").splitlines()
             if l.startswith("|")]
    header = [h.strip() for h in lines[0].strip("|").split("|")]
    rows = []
    for l in lines[2:]:
        cells = [re.sub(r"\*\*|`", "", c).strip() for c in l.strip().strip("|").split(" | ")]
        if len(cells) == len(header):
            rows.append(cells)
    return pd.DataFrame(rows, columns=header)


# ---------------------------------------------------------------------------------------------
# Evidence index: which notebook step saved each supporting file
# ---------------------------------------------------------------------------------------------
SAVE_PATTERNS = [r'save_table\([^\n]*?,\s*"([^"]+)"\)', r'save_chart\([^\n]*?,\s*"([^"]+)"\)',
                 r'OUT_DIR\s*/\s*f?"([^"{}]+\.(?:csv|png|json|joblib))"', r'"([A-Za-z0-9_\-]+\.(?:csv|png|json|joblib))"']


def evidence_index(module_dir: Path, exclude: set) -> pd.DataFrame:
    """List every file in outputs/ (except the final files) with the notebook and step heading that made it."""
    made_by = {}
    for nb_path in sorted((module_dir / "notebooks").glob("*.ipynb")):
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
        allsrc = "\n".join("".join(c["source"]) for c in nb["cells"])
        # Which outputs folder this notebook writes to (e.g. "task2"), so same-named files in
        # different task folders (each task has a key_numbers.json) are told apart.
        folder = re.search(r'OUT_DIR\s*=\s*MODULE_DIR\s*/\s*"outputs"\s*/\s*"([^"]+)"', allsrc)
        folder = folder.group(1) if folder else ""
        heading = ""
        for cell in nb["cells"]:
            src = "".join(cell["source"])
            if cell["cell_type"] == "markdown":
                h = re.findall(r"^#{2,3}\s+(.+)$", src, flags=re.M)
                if h:
                    heading = h[0].strip()
                continue
            for pat in SAVE_PATTERNS:
                for name in re.findall(pat, src):
                    made_by.setdefault((folder, Path(name).stem), (nb_path.name, heading))
    rows = []
    for f in sorted((module_dir / "outputs").rglob("*")):
        if not f.is_file() or f.name in exclude or f.name.startswith("FINAL_"):
            continue
        rel = f.relative_to(module_dir / "outputs")
        nb_name, step = made_by.get((rel.parts[0] if len(rel.parts) > 1 else "", f.stem), ("", ""))
        kind = {".csv": "Table", ".png": "Chart", ".json": "Key numbers (machine-readable)",
                ".joblib": "Saved model"}.get(f.suffix, f.suffix)
        rows.append({"File": str(f.relative_to(module_dir)).replace("\\", "/"), "Kind": kind,
                     "Made by (notebook)": nb_name or "—", "Notebook step (what it shows)": step or "—"})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------------------
# Writing and formatting
# ---------------------------------------------------------------------------------------------
def _format(ws, df: pd.DataFrame, start_row: int, wide_cols: set):
    """Header colours, wrapped long-text columns, sensible widths, frozen header."""
    for j, col in enumerate(df.columns, start=1):
        cell = ws.cell(row=start_row, column=j)
        cell.fill, cell.font, cell.alignment = HEADER_FILL, HEADER_FONT, WRAP
        sample = df[col].astype(str).head(200)
        longest = max([len(str(col))] + [len(s) for s in sample])
        width = 70 if col in wide_cols else min(max(10, longest + 2), 45)
        ws.column_dimensions[get_column_letter(j)].width = width
        if col in wide_cols or longest > 45:
            for i in range(start_row + 1, start_row + 1 + min(len(df), 5000)):
                ws.cell(row=i, column=j).alignment = WRAP
    ws.freeze_panes = ws.cell(row=start_row + 1, column=1)


def _write_table(writer, sheet: str, df: pd.DataFrame, title: str, note: str = "", wide_cols: set = frozenset()):
    """A title line, an optional note line, then the table."""
    start = 3 if note else 2
    df.to_excel(writer, sheet_name=sheet, index=False, startrow=start)
    ws = writer.sheets[sheet]
    ws.cell(row=1, column=1, value=title).font = TITLE_FONT
    if note:
        ws.cell(row=2, column=1, value=note).alignment = Alignment(wrap_text=False)
    _format(ws, df, start + 1, set(wide_cols))


def build_workbook(module_dir: Path, number: int, read_me: dict, key_numbers: pd.DataFrame,
                   board_actions: pd.DataFrame, task_tabs: list, handoff: pd.DataFrame, receiver: str,
                   column_guide: dict, m9_inputs: pd.DataFrame = None) -> Path:
    """Write FINAL_M<number>_module_output.xlsx and return its path.

    read_me: {"question": str, "answer": [str, ...], "tasks": [(task, final file, what it holds), ...],
              "how_to_read": [str, ...]}
    task_tabs: [(sheet name ≤ 31 characters, csv path, one-line description), ...]
    column_guide: {column name: one plain sentence}; every column of every task tab must be described
                  (the build stops otherwise), and the guide is printed in the Read me tab.
    """
    module_dir = Path(module_dir)
    out = module_dir / "outputs" / f"FINAL_M{number}_module_output.xlsx"
    tab_columns = {name: list(pd.read_csv(path, nrows=1).columns) for name, path, _ in task_tabs}
    undescribed = sorted({c for cols in tab_columns.values() for c in cols if c not in column_guide})
    assert not undescribed, f"column guide is missing: {undescribed}"
    missing = [c for c in HANDOFF_COLUMNS if c not in handoff.columns]
    assert not missing, f"hand-off is missing columns {missing}"
    tabs_guide = [("1 Read me", "Everyone", "This page: the question, the answer, how to use the workbook"),
                  ("2 Key numbers", "Board, presenter, student", "The headline figures, each explained"),
                  ("3 Board actions", "Board, presenter", "What to do, the ₹ effect, the evidence")]
    tabs_guide += [(name, "Board, evaluator, " + receiver, about) for name, _, about in task_tabs]
    if m9_inputs is not None:
        miss9 = [c for c in M9_INPUT_COLUMNS if c not in m9_inputs.columns]
        assert not miss9, f"Module 9 inputs are missing columns {miss9}"
    tabs_guide += [("Hand-off", receiver, f"The figures {receiver} needs; each points to the tab, column(s) and rows behind it"),
                   *([("Module 9 inputs", "Module 9", "The standard fields for each business category: return per ₹, bad-year result, capacity, evidence, gaps, controls")]
                     if m9_inputs is not None else []),
                   ("Decisions", "Evaluator, student", "Every agreed decision: options, evidence, status"),
                   ("Evidence index", "Evaluator", "Every supporting output file and the notebook step that made it")]

    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        # 1 Read me
        rows = [("Question (brief, verbatim)", read_me["question"])]
        rows += [("Answer" if i == 0 else "", a) for i, a in enumerate(read_me["answer"])]
        rows += [("", "")] + [("Task final files", f"{t}: {f} — {w}") for t, f, w in read_me["tasks"]]
        rows += [("", "")] + [("Which tab to read", f"{n} → {who}: {about}") for n, who, about in tabs_guide]
        rows += [("", "")] + [("Status labels (Hand-off tab)", f"{s}: {m}") for s, m in STATUS_LEGEND]
        rows += [("", "")] + [("How to read", h) for h in read_me.get("how_to_read", [])]
        for name, cols in tab_columns.items():                       # the column guide, tab by tab
            rows += [("", "")] + [(f"Column guide: {name}" if i == 0 else "", f"{c}: {column_guide[c]}") for i, c in enumerate(cols)]
        _write_table(writer, "1 Read me", pd.DataFrame(rows, columns=["Section", "Text"]),
                     f"Module {number} — final output (numbers and short text; the module report has the full explanation)",
                     wide_cols={"Text"})
        writer.sheets["1 Read me"].column_dimensions["B"].width = 140
        # 2 Key numbers, 3 Board actions
        _write_table(writer, "2 Key numbers", key_numbers, "Key numbers",
                     "Each figure with what it means, whether high is good or bad, and how it was worked out",
                     wide_cols={"What it means", "How it was worked out"})
        _write_table(writer, "3 Board actions", board_actions, "What we recommend the Board does",
                     wide_cols={"Action", "Why (evidence)"})
        # Task tabs
        for name, path, about in task_tabs:
            df = pd.read_csv(path)
            _write_table(writer, name[:31], df, name, f"{about}  |  Source file: {Path(path).relative_to(module_dir)}"
                         .replace("\\", "/"),
                         wide_cols={c for c in df.columns if any(k in c for k in ("reason", "Reason", "words", "Why", "path"))})
        # Hand-off, Decisions, Evidence index
        _write_table(writer, "Hand-off", handoff[HANDOFF_COLUMNS], f"Hand-off to {receiver}",
                     "Each figure can be rebuilt from the named tab and column(s) by following 'How it comes from the rows'",
                     wide_cols={"How it comes from the rows", "How the receiving module should use it", "Figure"})
        if m9_inputs is not None:
            _write_table(writer, "Module 9 inputs", m9_inputs[M9_INPUT_COLUMNS], "Module 9 inputs (the same fields in every module)",
                         "Return and bad-year result are per ₹ deployed, a year; a blank or 'not in the data' is a true gap, filled in Module 9 by a stated assumption",
                         wide_cols={"What NovaFin would put money into", "How the bad year is defined", "Data gap or assumption", "Controls", "Detail column(s)"})
        dec = read_decisions(module_dir)
        _write_table(writer, "Decisions", dec, "Decisions (from docs/decisions.md)",
                     wide_cols={c for c in dec.columns if c in ("Chosen", "Evidence / reason", "Options considered")})
        ev = evidence_index(module_dir, exclude={out.name})
        _write_table(writer, "Evidence index", ev, "Supporting output files",
                     "Every other file the notebooks saved; the final files are the task tabs of this workbook")
    normalise_office_file(out)
    return out


def handoff_row(figure, value, unit, status, tab, columns, how, decision, use) -> dict:
    """One hand-off row with the agreed columns."""
    return dict(zip(HANDOFF_COLUMNS, [figure, value, unit, status, tab, columns, how, decision, use]))


def key_row(figure, value, unit, meaning, good, how, source) -> dict:
    """One key-numbers row."""
    return {"Figure": figure, "Value": value, "Unit": unit, "What it means": meaning, "Good or bad": good,
            "How it was worked out": how, "Source": source}


def action_row(number, action, effect, why, where) -> dict:
    """One board-action row."""
    return {"#": number, "Action": action, "₹ effect": effect, "Why (evidence)": why, "Where to look": where}

"""Module 9 handoff record (blueprint: "Module 9 handoff record").

Each notebook ends by writing results/<module>/handoff.json, so the allocation is built from numbers, not prose.
Percentages are in percent (12.5 means 12.5%). RAROC is computed here, never typed by hand.
"""
import json
import math

import pandas as pd

from .config import MODULES, RESULTS, use_module
from .finance import raroc

ML_EDGE = {"validated", "weak", "none"}


def make_line(business_line, capacity_cr, expected_return_pct, expected_loss_pct, capital_charge_pct,
              stress_loss_pct, ml_edge, evidence, key_risks, **extra):
    """One business line for Module 9.

    key_risks: two or three (risk, control) pairs. extra: anything else Module 9 should see (kept as is).
    """
    numbers = {"capacity_cr": capacity_cr, "expected_return_pct": expected_return_pct,
               "expected_loss_pct": expected_loss_pct, "capital_charge_pct": capital_charge_pct,
               "stress_loss_pct": stress_loss_pct}
    for name, value in numbers.items():
        if not math.isfinite(float(value)):
            raise ValueError(f"{name} must be a finite number, got {value!r}")
        numbers[name] = float(value)
    if numbers["capacity_cr"] < 0 or not 0 <= numbers["capital_charge_pct"] <= 100:
        raise ValueError("capacity_cr must be ≥ 0 and capital_charge_pct within 0-100")
    if ml_edge not in ML_EDGE:
        raise ValueError(f"ml_edge must be one of {sorted(ML_EDGE)}")
    if not 2 <= len(key_risks) <= 3:
        raise ValueError("name two or three key risks, each with its control")
    r = raroc(numbers["expected_return_pct"], numbers["expected_loss_pct"], numbers["capital_charge_pct"])
    return {
        "business_line": business_line,
        **numbers,
        "raroc_pct": None if math.isnan(r) else round(r * 100, 4),
        "ml_edge": ml_edge,
        "evidence": evidence,
        "key_risks": [{"risk": risk, "control": control} for risk, control in key_risks],
        **extra,
    }


def write_handoff(nb_id, lines, notes=""):
    """Save this module's lines to results/<module>/handoff.json and return the path."""
    res, _ = use_module(nb_id)
    path = res / "handoff.json"
    record = {"module": MODULES[nb_id], "lines": list(lines), "notes": notes}
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    return path


def read_handoffs(results_dir=RESULTS):
    """Every module's lines as one table, for the Module 9 allocation."""
    rows = []
    for path in sorted(results_dir.glob("*/handoff.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        rows += [{"module": record["module"], **line} for line in record["lines"]]
    return pd.DataFrame(rows)

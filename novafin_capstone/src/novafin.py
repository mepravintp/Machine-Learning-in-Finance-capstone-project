"""Shared helpers and assumptions for the NovaFin capstone notebooks.

Every notebook starts with:
    import sys; sys.path.insert(0, '../src')
    from novafin import *
"""
import json
import os
import warnings

# joblib tries to count CPU cores with 'wmic', which is missing on new Windows builds and prints a long
# (harmless) traceback. Setting the core count ourselves avoids that noise in every notebook.
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (roc_auc_score, average_precision_score,
                             roc_curve, precision_recall_curve, confusion_matrix)

warnings.filterwarnings("ignore")

# ----------------------------------------------------------------------------
# Shared assumptions (one place, so every module uses the same numbers)
# ----------------------------------------------------------------------------
SEED = 42
LAKH, CRORE = 1e5, 1e7          # money columns are in rupees; see notebook 00 for the reasoning
ASSUMPTIONS = {
    "LGD": 0.40,                 # given in the brief
    "DISCOUNT_RATE": 0.12,       # annual, used for NPV of strategic initiatives
    "RISK_FREE": 0.07,           # annual, used for Sharpe and Black-Scholes comparisons
    "VAR_CONFIDENCE": 0.99,
    "COST_OF_FUNDS": 0.06,       # annual funding cost used for lending margins
    "MAX_ECL_RATIO": 0.03,       # risk appetite: expected credit loss / approved exposure
    "FRAUD_MISS_COST": 10_000,   # rupees per missed fraud (given in the brief)
    "FRAUD_FALSE_POSITIVE_COST": 500,  # rupees per false alarm (given in the brief)
    "TOTAL_CAPITAL_CR": 1000,    # rupees crore to allocate (given in the brief)
    "RETENTION_BUDGET": 1000,    # customers the relationship team can contact (given)
}

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
def find_root():
    """Walk upwards until a folder containing data/ and src/ is found (works in Colab or locally)."""
    p = Path.cwd().resolve()
    for q in [p, *p.parents]:
        if (q / "data").exists() and (q / "src").exists():
            return q
    raise FileNotFoundError("Run the notebook from inside the novafin_capstone folder.")

ROOT = find_root()
DATA = ROOT / "data"
RESULTS = ROOT / "results"
FIGS = ROOT / "figures"
RESULTS.mkdir(exist_ok=True); FIGS.mkdir(exist_ok=True)

# ----------------------------------------------------------------------------
# Output folders per module: results/<folder>/ and figures/<folder>/
# Notebook number -> folder named "module number + name" (notebook 09 is an extra, notebook 10 is Module 9).
# ----------------------------------------------------------------------------
MODULE_FOLDERS = {
    "00": "Module_00_Setup",
    "01": "Module_01_Strategic_Initiatives",
    "02": "Module_02_Credit_Risk",
    "03": "Module_03_Fraud_Detection",
    "04": "Module_04_Churn_CLV",
    "05": "Module_05_Equity_Returns",
    "06": "Module_06_Portfolio_Optimisation",
    "07": "Module_07_HFT",
    "08": "Module_08_Derivatives",
    "09": "Extra_Liquidity_Reserve",
    "10": "Module_09_Integrated_Allocation",
}
_CTX = {"res": RESULTS, "fig": FIGS}      # current output folders (set by use_module)

def use_module(nb_id):
    """Point save_result() / savefig() at this module's folders. Returns (results_dir, figures_dir)."""
    folder = MODULE_FOLDERS[nb_id]
    _CTX["res"], _CTX["fig"] = RESULTS / folder, FIGS / folder
    _CTX["res"].mkdir(parents=True, exist_ok=True); _CTX["fig"].mkdir(parents=True, exist_ok=True)
    print(f"Outputs -> results/{folder}/ and figures/{folder}/")
    return _CTX["res"], _CTX["fig"]

def result_file(nb_id, filename):
    """Path of a file saved by another module, e.g. result_file('05', 'equity_predictions.csv')."""
    return RESULTS / MODULE_FOLDERS[nb_id] / filename

def load(name, **kw):
    """Load a dataset by short name, e.g. load('loans')."""
    files = {"initiatives": "strategic_initiatives.csv", "loans": "nova_loans.csv",
             "transactions": "nova_transactions.csv", "customers": "nova_customers.csv",
             "market": "nova_market_data.csv", "hft": "nova_hft_orderbook.csv",
             "options": "nova_options.csv", "liquidity": "nova_liquidity.csv"}
    return pd.read_csv(DATA / files[name], **kw)

def cr(x):
    """rupees -> crore"""
    return x / CRORE

# ----------------------------------------------------------------------------
# Results hand-off between notebooks (this is how the work converges)
# ----------------------------------------------------------------------------
def save_result(module, payload):
    """Save one module's allocation row and key numbers to results/<module>.json."""
    def clean(o):
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.floating,)): return float(o)
        if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)): return [clean(v) for v in o]
        return o
    path = _CTX["res"] / f"{module}.json"
    path.write_text(json.dumps(clean(payload), indent=2, default=str))
    print(f"saved {path.relative_to(ROOT).as_posix()}")

def load_result(module):
    """Find results/**/<module>.json in any module folder and load it."""
    hits = sorted(RESULTS.rglob(f"{module}.json"))
    if not hits:
        raise FileNotFoundError(f"results/**/{module}.json not found; run that module's notebook first")
    return json.loads(hits[0].read_text())

# ----------------------------------------------------------------------------
# Model comparison table: which model wins, and what do we gain by choosing it?
# ----------------------------------------------------------------------------
def compare_models(table, metric, higher_is_better=True, chosen=None, baseline=None, extra=None):
    """Rank models on one metric and show the benefit of each choice.

    table     : DataFrame with one row per model and a column `metric`
    chosen    : the model actually selected (marked in the 'Chosen' column)
    baseline  : reference model (e.g. the simplest or a no-skill rule); gains are measured against it
    extra     : other columns from `table` to keep for context
    Columns returned:
      Rank, metric, 'Gain vs baseline' (metric difference, signed so that + is better),
      'Gap to best' (how much worse than the top model; 0 for the best), 'Chosen' (✔)
    """
    t = table[[metric] + (extra or [])].copy()
    sign = 1 if higher_is_better else -1
    t = t.sort_values(metric, ascending=not higher_is_better)
    t.insert(0, "Rank", range(1, len(t) + 1))
    best_val = t[metric].iloc[0]
    if baseline is not None:
        t["Gain vs baseline"] = sign * (t[metric] - t.loc[baseline, metric])
    t["Gap to best"] = sign * (best_val - t[metric])
    t["Chosen"] = ["✔" if i == chosen else "" for i in t.index]
    return t

# ----------------------------------------------------------------------------
# Plot style
# ----------------------------------------------------------------------------
sns.set_theme(style="whitegrid", context="notebook", palette="deep")
plt.rcParams.update({"figure.dpi": 110, "axes.titlesize": 12, "axes.titleweight": "semibold",
                     "axes.spines.top": False, "axes.spines.right": False})

def savefig(name):
    """Save the current figure as figures/<module folder>/<name>.png."""
    plt.savefig(_CTX["fig"] / f"{name}.png", bbox_inches="tight", dpi=150)

# ----------------------------------------------------------------------------
# Classification metrics
# ----------------------------------------------------------------------------
def ks_stat(y, p):
    fpr, tpr, _ = roc_curve(y, p)
    return float(np.max(tpr - fpr))

def binary_report(y, p, name="model"):
    """ROC-AUC, Gini, KS, PR-AUC and calibration gap for predicted probabilities p.

    Calibration gap = average |predicted - observed| rate across probability deciles (the calibration curve
    taught in class, summarised in one number; 0 = perfectly calibrated)."""
    auc = roc_auc_score(y, p)
    return pd.Series({"ROC-AUC": auc, "Gini": 2 * auc - 1, "KS": ks_stat(y, p),
                      "PR-AUC": average_precision_score(y, p), "Calib. gap": calibration_gap(y, p),
                      "Mean predicted": float(np.mean(p)), "Actual rate": float(np.mean(y))}, name=name)

def calibration_table(y, p, bins=10):
    """Observed vs predicted rate by predicted-probability decile."""
    d = pd.DataFrame({"y": np.asarray(y), "p": np.asarray(p)})
    d["bin"] = pd.qcut(d.p, bins, duplicates="drop")
    t = d.groupby("bin", observed=True).agg(n=("y", "size"), predicted=("p", "mean"), observed=("y", "mean"))
    return t.reset_index(drop=True)

def calibration_gap(y, p, bins=10):
    """Mean absolute difference between predicted and observed rates across probability deciles."""
    t = calibration_table(y, p, bins)
    return float((t.predicted - t.observed).abs().mean())

def shap_importance(predict_fn, X_background, X_explain, max_evals=None):
    """Model-agnostic SHAP values for a probability function. Returns the shap Explanation."""
    import shap
    masker = shap.maskers.Independent(X_background, max_samples=100)
    explainer = shap.Explainer(predict_fn, masker, seed=SEED)
    return explainer(X_explain)

print(f"NovaFin helpers loaded. Root: {ROOT}")

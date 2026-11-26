"""Paths, data loading and the assumptions every module shares (blueprint: "Data audit and locked assumptions").

Every notebook starts with:
    import sys; sys.path.insert(0, "../src")
    from novakit import ...
"""
import os
from pathlib import Path

import pandas as pd

SEED = 42

# Locked assumptions. Each one is stated in the report with its sensitivity.
ASSUMPTIONS = {
    "TOTAL_CAPITAL_CR": 1000,                                 # ₹ crore to allocate (brief)
    "LGD": 0.40,                                              # brief; collateral-based LGD is the sensitivity
    "FUNDING_COST": 0.065,                                    # annual funding cost behind lending margins
    "FRAUD_MISS_COST": 10_000,                                # ₹ per missed fraud (brief)
    "FRAUD_ALERT_COST": 500,                                  # ₹ per false alarm (brief)
    "RETENTION_CONTACTS": 1000,                               # customers the RM team can contact (brief)
    "RISK_PREMIUM_PTS": {"Low": 3, "Medium": 5, "High": 8},   # Module 1 discount rate = Interest_Rate + premium
    "TERMINAL_GROWTH": 0.03,                                  # Module 1; 0% and 5% are the sensitivities
    "TRADING_COST_BPS": 10,                                   # per unit of turnover; rerun at 50 (TA9)
    "VAR_CONFIDENCE": 0.99,
    "CAPITAL_CHARGE": {"corporate": 1.00, "retail": 0.75, "equity": 1.00, "liquidity": 0.00},
    "MAX_LINE_SHARE": 0.35,                                   # no line above 35% of the ₹1,000 cr
    "MAX_HFT_SHARE": 0.03,
}

# Units: initiatives are in ₹ lakh, loans and customers in rupees, the liquidity file in ₹ crore (weakest assumption).
LAKH, CRORE = 1e5, 1e7

ROOT = Path(__file__).resolve().parents[2]                    # vineet/
DATA = Path(os.environ.get("NOVAFIN_DATA", ROOT.parent / "novafin_capstone" / "data"))   # shared, never edited
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

FILES = {
    "initiatives": "strategic_initiatives.csv",
    "loans": "nova_loans.csv",
    "transactions": "nova_transactions.csv",
    "customers": "nova_customers.csv",
    "market": "nova_market_data.csv",
    "hft": "nova_hft_orderbook.csv",
    "options": "nova_options.csv",
    "liquidity": "nova_liquidity.csv",
}

# Notebook number -> output folder. Same names as novafin_capstone/ so each module compares one-to-one.
MODULES = {
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


def load(name, **kw):
    """Load a dataset by short name, e.g. load("loans")."""
    return pd.read_csv(DATA / FILES[name], **kw)


def use_module(nb_id):
    """Create this module's output folders and return (results_dir, figures_dir)."""
    res, fig = RESULTS / MODULES[nb_id], FIGURES / MODULES[nb_id]
    res.mkdir(parents=True, exist_ok=True)
    fig.mkdir(parents=True, exist_ok=True)
    return res, fig

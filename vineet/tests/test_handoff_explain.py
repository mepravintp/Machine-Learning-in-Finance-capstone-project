import json

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from novakit import config, explain, handoff

RISKS = [("PD drift", "monthly PSI check"), ("Interest_Rate proxies the lender's score", "challenger without it")]


def test_make_line_computes_raroc():
    line = handoff.make_line("Retail lending", 120, 12, 3, 75, 6, "validated", "test AUC 0.75", RISKS)
    assert line["raroc_pct"] == pytest.approx(12.0)
    reserve = handoff.make_line("Liquidity reserve", 150, 6.5, 0, 0, 0, "weak", "ridge vs last value", RISKS)
    assert reserve["raroc_pct"] is None


@pytest.mark.parametrize("change", [{"ml_edge": "strong"}, {"key_risks": RISKS[:1]},
                                    {"capacity_cr": float("nan")}, {"capital_charge_pct": 120}])
def test_make_line_rejects_bad_records(change):
    args = dict(business_line="x", capacity_cr=1, expected_return_pct=1, expected_loss_pct=0,
                capital_charge_pct=100, stress_loss_pct=1, ml_edge="none", evidence="", key_risks=RISKS)
    with pytest.raises(ValueError):
        handoff.make_line(**{**args, **change})


def test_write_and_read_handoffs(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "RESULTS", tmp_path)
    line = handoff.make_line("Corporate lending", 200, 10, 2, 100, 8, "validated", "", RISKS, approved_loans=230)
    path = handoff.write_handoff("02", [line], notes="LGD 40%")
    assert path == tmp_path / "Module_02_Credit_Risk" / "handoff.json"
    assert json.loads(path.read_text())["lines"][0]["approved_loans"] == 230
    table = handoff.read_handoffs(tmp_path)
    assert table.loc[0, "module"] == "Module_02_Credit_Risk" and table.loc[0, "raroc_pct"] == pytest.approx(8.0)


def _toy_model():
    rng = np.random.default_rng(0)
    X = pd.DataFrame({"x1": rng.normal(size=400), "x2": rng.normal(size=400), "noise": rng.normal(size=400)})
    y = (2 * X["x1"] - X["x2"] + rng.normal(scale=0.5, size=400) > 0).astype(int)
    return X, make_pipeline(StandardScaler(), LogisticRegression()).fit(X, y)


def test_coefficient_table_orders_by_size():
    X, model = _toy_model()
    table = explain.coefficient_table(model, X.columns)
    assert table["feature"].tolist()[:2] == ["x1", "x2"]
    assert table.loc[0, "coefficient"] > 0 > table.loc[1, "coefficient"]


def test_shap_top_drivers_and_case():
    X, model = _toy_model()
    explanation = explain.shap_explanation(lambda d: model.predict_proba(d)[:, 1], X, X.iloc[:40])
    top = explain.top_drivers(explanation, n=3)
    assert top["feature"].tolist()[:2] == ["x1", "x2"]
    assert top["direction"].tolist()[:2] == ["+", "-"]
    assert len(explain.case_drivers(explanation, 0, n=2)) == 2

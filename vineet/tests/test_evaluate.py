import numpy as np
import pandas as pd
import pytest

from novakit import evaluate as ev


def test_classification_metrics_perfect_ranking():
    y = np.array([0, 0, 0, 1])
    m = ev.classification_metrics(y, [0.1, 0.2, 0.3, 0.9])
    assert m["roc_auc"] == 1 and m["ks"] == 1 and m["pr_auc"] == 1
    assert m["pr_lift"] == pytest.approx(4)                  # 1 ÷ the 25% base rate


def test_cost_curve_picks_the_cheapest_threshold():
    y, p = [0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8]
    curve = ev.cost_curve(y, p, cost_fn=10, cost_fp=1, thresholds=[0, 0.35, 0.5, 0.9])
    assert curve["cost"].tolist() == [2, 1, 10, 20]
    assert ev.best_threshold(curve) == 0.35


def test_best_threshold_tie_goes_to_fewer_alerts():
    curve = ev.cost_curve([0, 1], [0.6, 0.7], cost_fn=10, cost_fp=1, thresholds=[0.0, 0.05])
    assert ev.best_threshold(curve) == 0.05


def test_calibration_table_bins():
    rng = np.random.default_rng(0)
    p = rng.uniform(size=1000)
    table = ev.calibration_table(rng.uniform(size=1000) < p, p)
    assert len(table) == 10 and table["n"].sum() == 1000
    assert np.abs(table["mean_predicted"] - table["observed_rate"]).max() < 0.15


def test_regression_and_oos_r2():
    assert ev.regression_metrics([1, 2], [2, 4]) == {"rmse": pytest.approx(np.sqrt(2.5)), "mae": 1.5}
    assert ev.oos_r2([1, 2, 3], [1, 2, 3], [2, 2, 2]) == 1
    assert ev.oos_r2([1, 2, 3], [2, 2, 2], [2, 2, 2]) == 0


def test_rank_ic_and_summary():
    df = pd.DataFrame({"month": [1, 1, 1, 2, 2, 2], "pred": [1, 2, 3, 1, 2, 3], "real": [1, 2, 3, 3, 2, 1]})
    ic = ev.rank_ic(df, "pred", "real", "month")
    assert ic.tolist() == [1.0, -1.0]
    assert ev.ic_summary(ic)["positive_share"] == 0.5
    assert ev.hit_rate([1, -1, 1], [2, -3, -1]) == pytest.approx(2 / 3)

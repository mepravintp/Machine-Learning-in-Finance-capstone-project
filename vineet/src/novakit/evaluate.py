"""The evaluation standard for every model (blueprint: "Evaluation standard for every model")."""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score, roc_curve


def ks_statistic(y, p):
    """Kolmogorov-Smirnov: the largest gap between the score distributions of positives and negatives."""
    fpr, tpr, _ = roc_curve(y, p)
    return float(np.max(tpr - fpr))


def classification_metrics(y, p):
    """ROC-AUC, PR-AUC and its lift over the base rate ("x times random"), Brier score and KS."""
    y, p = np.asarray(y), np.asarray(p)
    base = y.mean()
    pr_auc = average_precision_score(y, p)
    return {
        "roc_auc": roc_auc_score(y, p),
        "pr_auc": pr_auc,
        "base_rate": base,
        "pr_lift": pr_auc / base,
        "brier": brier_score_loss(y, p),
        "ks": ks_statistic(y, p),
    }


def calibration_table(y, p, bins=10):
    """Mean predicted probability against the observed rate, by score decile."""
    df = pd.DataFrame({"y": np.asarray(y), "p": np.asarray(p)})
    df["bin"] = pd.qcut(df["p"], bins, duplicates="drop")
    return (df.groupby("bin", observed=True)
              .agg(n=("y", "size"), mean_predicted=("p", "mean"), observed_rate=("y", "mean"))
              .reset_index())


def regression_metrics(y, yhat):
    err = np.asarray(yhat) - np.asarray(y)
    return {"rmse": float(np.sqrt(np.mean(err ** 2))), "mae": float(np.mean(np.abs(err)))}


def oos_r2(y, yhat, benchmark):
    """Out-of-sample R² against a benchmark forecast (e.g. the historical mean): above 0 beats it."""
    y = np.asarray(y)
    return float(1 - np.sum((y - np.asarray(yhat)) ** 2) / np.sum((y - np.asarray(benchmark)) ** 2))


def error_by_segment(y, yhat, segment):
    df = pd.DataFrame({"err": np.asarray(yhat) - np.asarray(y), "segment": np.asarray(segment)})
    return df.groupby("segment").agg(
        n=("err", "size"),
        rmse=("err", lambda e: np.sqrt(np.mean(e ** 2))),
        mae=("err", lambda e: np.mean(np.abs(e))),
    )


def cost_curve(y, p, cost_fn, cost_fp, thresholds=None):
    """Expected cost at each threshold: cost_fn × missed positives + cost_fp × false alarms (flag when p ≥ t).

    Choose the threshold on validation data, then report cost_curve(y_test, p_test, ..., [chosen]) on test.
    """
    y, p = np.asarray(y).astype(bool), np.asarray(p)
    thresholds = np.linspace(0, 1, 201) if thresholds is None else np.asarray(thresholds)
    rows = []
    for t in thresholds:
        flag = p >= t
        tp, fp, fn = int(np.sum(flag & y)), int(np.sum(flag & ~y)), int(np.sum(~flag & y))
        rows.append({
            "threshold": t, "alerts": int(flag.sum()), "tp": tp, "fp": fp, "fn": fn,
            "recall": tp / max(y.sum(), 1), "precision": tp / max(flag.sum(), 1),
            "cost": cost_fn * fn + cost_fp * fp,
        })
    return pd.DataFrame(rows)


def best_threshold(curve):
    """Lowest-cost threshold; ties go to the higher threshold (fewer alerts)."""
    best = curve[curve["cost"] == curve["cost"].min()]
    return float(best["threshold"].max())


def rank_ic(df, pred, realised, by):
    """Spearman correlation of predicted and realised values within each period (the monthly rank IC)."""
    return df.groupby(by)[[pred, realised]].apply(lambda g: g[pred].corr(g[realised], method="spearman"))


def ic_summary(ic):
    """Mean IC, its t-statistic and the share of periods with a positive IC."""
    ic = pd.Series(ic).dropna()
    return {"mean_ic": ic.mean(), "t_stat": ic.mean() / (ic.std(ddof=1) / np.sqrt(len(ic))),
            "positive_share": (ic > 0).mean(), "periods": len(ic)}


def hit_rate(pred, realised):
    """Share of forecasts whose sign matches the outcome."""
    return float(np.mean(np.sign(np.asarray(pred)) == np.sign(np.asarray(realised))))

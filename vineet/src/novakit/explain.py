"""Explain or it can't be used (S8): global top drivers and individual cases for the board."""
import numpy as np
import pandas as pd

from .config import SEED


def coefficient_table(model, feature_names):
    """Coefficients of a fitted linear or logistic model (or a pipeline ending in one), largest first.

    Scale the inputs inside the pipeline so the sizes are comparable, and check each sign against theory (S12).
    """
    est = model.steps[-1][1] if hasattr(model, "steps") else model
    coef = np.atleast_2d(est.coef_)
    if coef.shape[0] > 1:                                     # multinomial: one column per class
        return pd.DataFrame(coef.T, index=feature_names, columns=est.classes_)
    table = pd.DataFrame({"feature": feature_names, "coefficient": coef[0]})
    return table.reindex(table["coefficient"].abs().sort_values(ascending=False).index).reset_index(drop=True)


def shap_explanation(predict_fn, background, X, max_background=200, seed=SEED):
    """SHAP values for any model, given a function of a DataFrame (e.g. lambda d: model.predict_proba(d)[:, 1]).

    Pass a sample as X: the model-agnostic explainer is slow on thousands of rows.
    """
    import shap
    bg = background.sample(min(max_background, len(background)), random_state=seed)
    return shap.Explainer(predict_fn, bg, seed=seed)(X)


def top_drivers(explanation, n=5):
    """Mean |SHAP| per feature, with the direction: + when higher values of the feature raise the score."""
    values, data = explanation.values, np.asarray(explanation.data, dtype=float)
    direction = [np.corrcoef(data[:, j], values[:, j])[0, 1] if data[:, j].std() > 0 else 0.0
                 for j in range(values.shape[1])]
    table = pd.DataFrame({
        "feature": explanation.feature_names,
        "mean_abs_shap": np.abs(values).mean(axis=0),
        "direction": np.where(np.asarray(direction) >= 0, "+", "-"),
    })
    return table.sort_values("mean_abs_shap", ascending=False).head(n).reset_index(drop=True)


def case_drivers(explanation, i, n=5):
    """The n features that moved one case's score most, for a reason code or a board example."""
    case = explanation[i]
    table = pd.DataFrame({"feature": case.feature_names, "value": case.data, "shap": case.values})
    return table.reindex(table["shap"].abs().sort_values(ascending=False).index).head(n).reset_index(drop=True)

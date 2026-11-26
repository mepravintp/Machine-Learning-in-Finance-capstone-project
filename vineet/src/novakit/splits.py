"""Splits that respect time (blueprint: "Splitting rules"). Each function returns boolean masks aligned to its input."""
import numpy as np
import pandas as pd
from sklearn.model_selection import RepeatedStratifiedKFold

from .config import SEED


def _as_datetimes(values):
    s = pd.Series(values).reset_index(drop=True)
    if not pd.api.types.is_datetime64_any_dtype(s):
        # Parsing is left to the caller: the order book's dates are day-first and would be misread here.
        raise TypeError("parse the dates first, e.g. pd.to_datetime(col, dayfirst=True)")
    return s


def repeated_cv(n_splits=5, n_repeats=5, seed=SEED):
    """Repeated stratified K-fold for the files with no time axis (initiatives, loans, customers)."""
    return RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=seed)


def time_split(times, fractions=(0.70, 0.15, 0.15)):
    """Train / validate / test masks by time (transactions).

    Cut points sit on distinct timestamps, so rows sharing a timestamp never straddle two sets.
    """
    if not np.isclose(sum(fractions), 1.0):
        raise ValueError("fractions must add to 1")
    t = _as_datetimes(times)
    ordered = np.sort(t.values)
    cut_val = ordered[int(len(ordered) * fractions[0])]
    cut_test = ordered[int(len(ordered) * (fractions[0] + fractions[1]))]
    train = (t < cut_val).values
    val = ((t >= cut_val) & (t < cut_test)).values
    test = (t >= cut_test).values
    return train, val, test


def day_block_split(days, n_train=14, n_val=3, n_test=3):
    """Whole-day train / validate / test masks (order book): no trading day is split across sets."""
    d = _as_datetimes(days)
    unique = np.sort(d.unique())
    if len(unique) != n_train + n_val + n_test:
        raise ValueError(f"expected {n_train + n_val + n_test} trading days, found {len(unique)}")
    train = d.isin(unique[:n_train]).values
    val = d.isin(unique[n_train:n_train + n_val]).values
    test = d.isin(unique[n_train + n_val:]).values
    return train, val, test


def walk_forward_months(dates, min_train_months=24, gap_days=21):
    """Expanding-window monthly walk-forward (market data). Yields (month, train_mask, test_mask).

    The test set is one calendar month. Training keeps only dates at least `gap_days` trading days before
    the month starts, so a label that looks `gap_days` ahead never reaches into the test month.
    """
    d = _as_datetimes(dates)
    trading_days = np.sort(d.unique())
    month = d.dt.to_period("M")
    for m in sorted(month.unique())[min_train_months:]:
        start = np.searchsorted(trading_days, d[month == m].min().to_datetime64())
        last_train = start - gap_days - 1
        if last_train < 0:
            continue
        yield m, (d <= trading_days[last_train]).values, (month == m).values

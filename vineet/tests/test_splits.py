import numpy as np
import pandas as pd
import pytest

from novakit import splits


def test_time_split_fractions_and_order():
    t = pd.Series(pd.date_range("2025-01-01", periods=100, freq="h")).sample(frac=1, random_state=0)
    train, val, test = splits.time_split(t)
    assert (train.sum(), val.sum(), test.sum()) == (70, 15, 15)
    values = t.reset_index(drop=True)
    assert values[train].max() < values[val].min() and values[val].max() < values[test].min()


def test_time_split_never_splits_a_timestamp():
    t = pd.Series(pd.to_datetime(["2025-01-01"] * 6 + ["2025-01-02"] * 4))
    train, val, test = splits.time_split(t, fractions=(0.5, 0.25, 0.25))
    for day in t.unique():
        rows = (t == day).values
        assert sum(mask[rows].any() for mask in (train, val, test)) == 1


def test_unparsed_dates_are_refused():
    with pytest.raises(TypeError):
        splits.time_split(pd.Series(["2025-01-01", "2025-01-02"]))


def test_day_block_split_uses_day_first_dates_in_calendar_order():
    days = pd.bdate_range("2026-01-05", periods=20)
    raw = pd.Series(np.repeat(days.strftime("%d-%m-%Y"), 3))     # the order book's format
    parsed = pd.to_datetime(raw, dayfirst=True)
    train, val, test = splits.day_block_split(parsed)
    assert (train.sum(), val.sum(), test.sum()) == (42, 9, 9)
    assert parsed[train].max() < parsed[val].min() and parsed[val].max() < parsed[test].min()
    with pytest.raises(ValueError):
        splits.day_block_split(parsed[parsed < days[19]])


def test_walk_forward_keeps_the_gap():
    days = pd.Series(pd.bdate_range("2021-01-01", "2024-12-31"))
    trading_days = list(days)
    folds = list(splits.walk_forward_months(days, min_train_months=12, gap_days=21))
    assert len(folds) == 48 - 12
    for month, train, test in folds:
        assert (days[test].dt.to_period("M") == month).all()
        last_train = trading_days.index(days[train].max())
        first_test = trading_days.index(days[test].min())
        assert first_test - last_train == 22          # 21 full trading days between them

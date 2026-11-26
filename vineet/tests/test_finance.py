import math

import numpy as np
import pytest

from novakit import finance as f


def test_black_scholes_textbook_values_and_parity():
    call = f.black_scholes(100, 100, 1, 0.05, 0.2, "Call")
    put = f.black_scholes(100, 100, 1, 0.05, 0.2, "put")
    assert call == pytest.approx(10.4506, abs=1e-4)
    assert put == pytest.approx(5.5735, abs=1e-4)
    assert call - put == pytest.approx(100 - 100 * math.exp(-0.05), abs=1e-9)


def test_black_scholes_is_vectorised_over_kind():
    prices = f.black_scholes([100, 100], 100, 1, 0.05, 0.2, ["Call", "Put"])
    assert prices == pytest.approx([10.4506, 5.5735], abs=1e-4)


def test_greeks():
    g = f.greeks(100, 100, 1, 0.05, 0.2, "Call")
    assert g["delta"] == pytest.approx(0.6368, abs=1e-4)
    assert g["gamma"] == pytest.approx(0.018762, abs=1e-6)
    assert g["vega"] == pytest.approx(37.524, abs=1e-3)
    assert f.greeks(100, 100, 1, 0.05, 0.2, "Put")["delta"] == pytest.approx(0.6368 - 1, abs=1e-4)


def test_implied_vol_round_trip_and_bounds():
    price = f.black_scholes([100, 90], [100, 100], [1, 0.5], 0.05, [0.2, 0.35], ["Call", "Put"])
    iv = f.implied_vol(price, [100, 90], [100, 100], [1, 0.5], 0.05, ["Call", "Put"])
    assert iv == pytest.approx([0.2, 0.35], abs=1e-6)
    assert np.isnan(f.implied_vol(150.0, 100, 100, 1, 0.05, "Call"))   # above the spot: no volatility fits


def test_npv_irr_and_terminal_value():
    assert f.npv([100, 100], 0.10, investment=150) == pytest.approx(100 / 1.1 + 100 / 1.21 - 150)
    assert f.npv([100], 0.10, terminal_growth=0.0) == pytest.approx(1000)   # a perpetuity of 100 at 10%
    with pytest.raises(ValueError):
        f.npv([100], 0.05, terminal_growth=0.05)
    assert f.irr([-100, 110]) == pytest.approx(0.10)
    assert math.isnan(f.irr([100, 100]))


def test_expected_npv_with_failure_loss():
    assert f.expected_npv(0.5, 100) == pytest.approx(50)
    assert f.expected_npv(0.5, 100, investment=200, failure_loss_share=0.5) == pytest.approx(0)


def test_credit_formulas():
    assert f.ecl(0.1, 0.4, 1000) == pytest.approx(40)
    assert f.collateral_lgd([2.0, 1.0, 0.3]).tolist() == [0.2, 0.4, 0.6]
    assert f.monthly_instalment(1200, 0, 12) == pytest.approx(100)
    assert f.monthly_instalment(100_000, 12, 12) == pytest.approx(8884.88, abs=0.01)


def test_clv():
    assert f.clv(100, 5, acquisition_cost=50) == pytest.approx(450)
    assert f.clv(100, 1, discount_rate=0.10) == pytest.approx(100 / 1.1)


def test_portfolio_statistics():
    assert f.max_drawdown([0.1, -0.5, 0.2]) == pytest.approx(-0.5)
    assert f.historical_var(np.arange(-50, 50), 0.99) == pytest.approx(49.01)
    assert f.annualised_return([0.01] * 252) == pytest.approx(1.01 ** 252 - 1)
    assert f.net_of_costs(0.01, 0.5, 10) == pytest.approx(0.0095)
    r = np.array([0.02, -0.01, 0.015, 0.0])
    assert f.sharpe(r, periods=12) == pytest.approx(r.mean() / r.std(ddof=1) * np.sqrt(12))


def test_raroc():
    assert f.raroc(12, 3, 75) == pytest.approx(0.12)
    assert math.isnan(f.raroc(6.5, 0, 0))

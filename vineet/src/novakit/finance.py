"""Finance formulas shared by the modules: NPV, ECL, CLV, portfolio statistics, VaR, Black-Scholes and RAROC."""
import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm


# ---------- Module 1: capital budgeting ----------

def npv(cash_flows, rate, investment=0.0, terminal_growth=None):
    """NPV of year-1..T cash flows at `rate`, less the up-front investment.

    With terminal_growth, adds a growing perpetuity on the year-T cash flow, discounted from year T.
    """
    cf = np.asarray(cash_flows, dtype=float)
    years = np.arange(1, len(cf) + 1)
    value = np.sum(cf / (1 + rate) ** years) - investment
    if terminal_growth is not None:
        if terminal_growth >= rate:
            raise ValueError("terminal growth must be below the discount rate")
        value += cf[-1] * (1 + terminal_growth) / (rate - terminal_growth) / (1 + rate) ** len(cf)
    return float(value)


def irr(cash_flows):
    """IRR of cash flows from year 0 (negative investment first). NaN when there is no sign change."""
    cf = np.asarray(cash_flows, dtype=float)
    years = np.arange(len(cf))
    f = lambda r: np.sum(cf / (1 + r) ** years)
    lo, hi = -0.99, 10.0
    if np.sign(f(lo)) == np.sign(f(hi)):
        return float("nan")
    return float(brentq(f, lo, hi))


def expected_npv(p_success, npv_value, investment=0.0, failure_loss_share=0.0):
    """eNPV = P(success) × NPV, as the brief defines it. failure_loss_share > 0 makes failure lose that share
    of the investment, since the brief's formula treats failure as costing nothing."""
    p = np.asarray(p_success, dtype=float)
    return p * np.asarray(npv_value) - (1 - p) * failure_loss_share * np.asarray(investment)


# ---------- Module 2: credit ----------

def ecl(pd_, lgd, ead):
    """Expected credit loss = PD × LGD × EAD."""
    return np.asarray(pd_) * np.asarray(lgd) * np.asarray(ead)


def collateral_lgd(cover, high_cover=0.20, base=0.40, low_cover=0.60):
    """LGD sensitivity: 20% when collateral cover ≥ 1.5, 60% when cover < 0.5, otherwise the 40% base."""
    cover = np.asarray(cover, dtype=float)
    return np.select([cover >= 1.5, cover < 0.5], [high_cover, low_cover], base)


def monthly_instalment(principal, annual_rate_pct, months):
    """Level monthly instalment of an amortising loan."""
    p, n = np.asarray(principal, dtype=float), np.asarray(months, dtype=float)
    r = np.asarray(annual_rate_pct, dtype=float) / 100 / 12
    with np.errstate(divide="ignore", invalid="ignore"):
        annuity = p * r / (1 - (1 + r) ** -n)
    return np.where(r == 0, p / n, annuity)


# ---------- Module 4: customers ----------

def clv(annual_margin, lifetime_years, acquisition_cost=0.0, discount_rate=0.0):
    """CLV = annual margin × lifetime − acquisition cost (S10); with a discount rate the margin is an annuity."""
    m, years = np.asarray(annual_margin, dtype=float), np.asarray(lifetime_years, dtype=float)
    factor = years if discount_rate == 0 else (1 - (1 + discount_rate) ** -years) / discount_rate
    return m * factor - acquisition_cost


# ---------- Modules 5, 6 and 9: portfolio and risk ----------

def annualised_return(returns, periods=252):
    r = np.asarray(returns, dtype=float)
    return float(np.prod(1 + r) ** (periods / len(r)) - 1)


def annualised_vol(returns, periods=252):
    return float(np.std(returns, ddof=1) * np.sqrt(periods))


def sharpe(returns, rf=0.0, periods=252):
    """Annualised Sharpe ratio; rf is the annual risk-free rate."""
    excess = np.asarray(returns, dtype=float) - rf / periods
    return float(excess.mean() / excess.std(ddof=1) * np.sqrt(periods))


def max_drawdown(returns):
    """Largest peak-to-trough fall of cumulative wealth, as a negative number (-0.25 is a 25% drawdown)."""
    wealth = np.cumprod(1 + np.asarray(returns, dtype=float))
    return float(np.min(wealth / np.maximum.accumulate(wealth) - 1))


def historical_var(pnl, confidence=0.99):
    """Historical VaR as a positive loss: the (1 − confidence) quantile of P&L or returns, sign flipped."""
    return float(-np.quantile(np.asarray(pnl, dtype=float), 1 - confidence))


def net_of_costs(gross_returns, turnover, cost_bps):
    """Returns after charging cost_bps per unit of turnover."""
    return np.asarray(gross_returns) - np.asarray(turnover) * cost_bps / 1e4


def raroc(expected_return, expected_loss, capital_charge):
    """(Expected return − expected loss) ÷ capital charge. NaN when no capital is charged (liquidity reserve)."""
    if capital_charge == 0:
        return float("nan")
    return (expected_return - expected_loss) / capital_charge


# ---------- Module 8: options ----------

def _d1_d2(S, K, T, r, sigma):
    S, K, T, r, sigma = (np.asarray(x, dtype=float) for x in (S, K, T, r, sigma))
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    return d1, d1 - sigma * np.sqrt(T)


def _is_call(kind):
    return np.char.lower(np.asarray(kind, dtype=str)) == "call"


def black_scholes(S, K, T, r, sigma, kind):
    """Black-Scholes price; kind is "Call" or "Put" (any case), scalar or array."""
    d1, d2 = _d1_d2(S, K, T, r, sigma)
    S, K, T, r = (np.asarray(x, dtype=float) for x in (S, K, T, r))
    disc = K * np.exp(-r * T)
    call = S * norm.cdf(d1) - disc * norm.cdf(d2)
    put = disc * norm.cdf(-d2) - S * norm.cdf(-d1)
    return np.where(_is_call(kind), call, put)


def greeks(S, K, T, r, sigma, kind):
    """Delta, gamma and vega (vega per 1.00 of volatility; divide by 100 for one vol point)."""
    d1, _ = _d1_d2(S, K, T, r, sigma)
    S, T, sigma = (np.asarray(x, dtype=float) for x in (S, T, sigma))
    return {
        "delta": np.where(_is_call(kind), norm.cdf(d1), norm.cdf(d1) - 1),
        "gamma": norm.pdf(d1) / (S * sigma * np.sqrt(T)),
        "vega": S * norm.pdf(d1) * np.sqrt(T),
    }


def implied_vol(price, S, K, T, r, kind, lo=1e-4, hi=5.0):
    """Volatility that makes Black-Scholes match `price`, per option. NaN outside the no-arbitrage bounds."""
    args = np.broadcast_arrays(*(np.asarray(x, dtype=float) for x in (price, S, K, T, r)),
                               np.asarray(kind, dtype=str))
    out = np.full(args[0].shape, np.nan)
    for i, (pr, s, k, t, rr, kd) in enumerate(zip(*(a.ravel() for a in args))):
        f = lambda v: float(black_scholes(s, k, t, rr, v, kd)) - pr
        if np.sign(f(lo)) != np.sign(f(hi)):
            out.flat[i] = brentq(f, lo, hi)
    return out

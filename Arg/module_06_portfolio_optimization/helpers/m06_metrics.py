"""
Module 6 — performance and risk measures
========================================

WHAT THIS FILE DOES
    Turns a series of daily portfolio returns into the numbers used to compare strategies.
    It is a helper because more than one notebook uses it: Part A (backtest), Part B (VaR and
    stress tests) and Module 9 (risk of the equity bucket) (project decision P-15).

    Measures (decisions M6-05, M6-10; formulas in docs/documentation.md section 9):
        CAGR              = (final value ÷ starting value) ^ (days a year ÷ number of days) − 1
        Volatility        = daily standard deviation × √(days a year)
        Sharpe            = (average daily return − daily risk-free) ÷ daily sd × √(days a year)
        Sortino           = same, dividing by the sd of the negative days only (downside risk)
        Maximum drawdown  = worst value of (value ÷ highest value so far − 1)
        Calmar            = CAGR ÷ |maximum drawdown|
        Tracking error    = sd of (strategy − benchmark) daily returns × √(days a year)
        Information ratio = (strategy CAGR − benchmark CAGR) ÷ tracking error
        VaR 95% (1 day)   = historical: −5th percentile of daily returns;
                            parametric: −(average − 1.645 × sd)
        CVaR 95% (1 day)  = average loss on the days worse than the historical VaR

    TRADING_DAYS = 261: this data has every weekday and no holidays (260–262 rows a year),
    so a year is 261 rows, not the US convention of 252 (decision M6-03).
    RISK_FREE_ANNUAL = 6.8%: a fixed assumption (the data's Interest_Rate column is random;
    decision M6-05).

HOW TO USE
    from m06_metrics import performance_table
    performance_table(daily_returns, benchmark=equal_weight_daily_returns)
"""
import numpy as np
import pandas as pd
from scipy.stats import norm

TRADING_DAYS = 261                      # rows a year in this data (decision M6-03)
RISK_FREE_ANNUAL = 0.068                # 6.8% a year (decision M6-05)


def daily_rate(annual: float) -> float:
    """Convert a yearly rate to the equivalent daily rate: (1 + annual) ^ (1 ÷ days a year) − 1."""
    return (1 + annual) ** (1 / TRADING_DAYS) - 1


def cagr(returns: pd.Series) -> float:
    """Steady yearly growth rate: (final value ÷ start) ^ (days a year ÷ days) − 1."""
    value = (1 + returns).prod()
    return value ** (TRADING_DAYS / len(returns)) - 1


def annual_volatility(returns: pd.Series) -> float:
    """Typical yearly swing: daily standard deviation × √(days a year)."""
    return returns.std() * np.sqrt(TRADING_DAYS)


def sharpe(returns: pd.Series, risk_free_annual: float = RISK_FREE_ANNUAL) -> float:
    """Return above the risk-free rate per unit of total risk (annualised)."""
    excess = returns - daily_rate(risk_free_annual)
    return excess.mean() / excess.std() * np.sqrt(TRADING_DAYS)


def sortino(returns: pd.Series, risk_free_annual: float = RISK_FREE_ANNUAL) -> float:
    """Like Sharpe, but only days below the risk-free rate count as risk (downside deviation)."""
    excess = returns - daily_rate(risk_free_annual)
    downside = np.sqrt((np.minimum(excess, 0) ** 2).mean())   # root-mean-square of the shortfalls
    return excess.mean() / downside * np.sqrt(TRADING_DAYS)


def max_drawdown(returns: pd.Series) -> float:
    """Worst fall from a previous high, as a negative fraction (−0.12 = −12%). Starts from a value of 1."""
    value = pd.concat([pd.Series([1.0]), (1 + returns).cumprod().reset_index(drop=True)])
    return float((value / value.cummax() - 1).min())


def calmar(returns: pd.Series) -> float:
    """CAGR per unit of worst fall."""
    return cagr(returns) / abs(max_drawdown(returns))


def tracking_error(returns: pd.Series, benchmark: pd.Series) -> float:
    """How far the strategy wanders from the benchmark: sd of the daily difference, annualised."""
    return (returns - benchmark).std() * np.sqrt(TRADING_DAYS)


def information_ratio(returns: pd.Series, benchmark: pd.Series) -> float:
    """Extra yearly return over the benchmark per unit of tracking error."""
    te = tracking_error(returns, benchmark)
    return np.nan if te == 0 else (cagr(returns) - cagr(benchmark)) / te


def var_historical(returns: pd.Series, level: float = 0.95) -> float:
    """Loss (positive fraction of value) not exceeded on `level` of days, from the actual days."""
    return float(-np.percentile(returns, (1 - level) * 100))


def var_parametric(returns: pd.Series, level: float = 0.95) -> float:
    """Same, assuming a bell curve: −(average + z × sd), z = −1.645 at 95%."""
    return float(-(returns.mean() + norm.ppf(1 - level) * returns.std()))


def cvar_historical(returns: pd.Series, level: float = 0.95) -> float:
    """Average loss on the days worse than the historical VaR (expected shortfall)."""
    cutoff = -var_historical(returns, level)
    return float(-returns[returns <= cutoff].mean())


def performance_table(returns: pd.Series, benchmark: pd.Series | None = None,
                      risk_free_annual: float = RISK_FREE_ANNUAL) -> dict:
    """Every measure for one strategy. Benchmark-relative measures only if a benchmark is given."""
    out = {
        "CAGR": cagr(returns),
        "Volatility": annual_volatility(returns),
        "Sharpe": sharpe(returns, risk_free_annual),
        "Sortino": sortino(returns, risk_free_annual),
        "Maximum drawdown": max_drawdown(returns),
        "Calmar": calmar(returns),
        "VaR 95% (1 day, historical)": var_historical(returns),
        "VaR 95% (1 day, parametric)": var_parametric(returns),
        "CVaR 95% (1 day)": cvar_historical(returns),
    }
    if benchmark is not None:
        out["Tracking error"] = tracking_error(returns, benchmark)
        out["Information ratio"] = information_ratio(returns, benchmark)
    return out


if __name__ == "__main__":
    # Self-test on simulated returns: 8% a year average, 16% a year volatility
    rng = np.random.default_rng(42)
    sample = pd.Series(rng.normal(0.08 / TRADING_DAYS, 0.16 / np.sqrt(TRADING_DAYS), TRADING_DAYS * 10))
    for key, value in performance_table(sample, benchmark=sample * 0.9).items():
        print(f"{key}: {value:.4f}")
    assert abs(annual_volatility(sample) - 0.16) < 0.01, "volatility check failed"
    assert abs(daily_rate(0.068) * TRADING_DAYS - 0.0658) < 0.001, "daily rate check failed"
    print("self-test passed")

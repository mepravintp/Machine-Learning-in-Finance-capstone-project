"""Module 8 — Black–Scholes prices and Greeks (European options, no dividends).

    d1 = [ln(S/K) + (r + σ²/2) T] / (σ √T),   d2 = d1 − σ √T
    Call = S N(d1) − K e^(−rT) N(d2);   Put = K e^(−rT) N(−d2) − S N(−d1)
    Delta call = N(d1); Delta put = N(d1) − 1; Gamma = n(d1) / (S σ √T); Vega = S n(d1) √T
    Theta call = −S n(d1) σ / (2√T) − r K e^(−rT) N(d2);  Theta put = −S n(d1) σ / (2√T) + r K e^(−rT) N(−d2)
"""
import numpy as np
import pandas as pd
from scipy.stats import norm


def _d1_d2(S, K, T, sigma, r):
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    return d1, d1 - sigma * np.sqrt(T)


def bs_price(S, K, T, sigma, r, is_call):
    d1, d2 = _d1_d2(S, K, T, sigma, r)
    call = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    put = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return np.where(is_call, call, put)


def greeks(S, K, T, sigma, r, is_call) -> pd.DataFrame:
    d1, d2 = _d1_d2(S, K, T, sigma, r)
    pdf = norm.pdf(d1)
    delta = np.where(is_call, norm.cdf(d1), norm.cdf(d1) - 1)
    gamma = pdf / (S * sigma * np.sqrt(T))
    vega = S * pdf * np.sqrt(T)
    common = -S * pdf * sigma / (2 * np.sqrt(T))
    theta = np.where(is_call, common - r * K * np.exp(-r * T) * norm.cdf(d2),
                     common + r * K * np.exp(-r * T) * norm.cdf(-d2))
    return pd.DataFrame({"Delta": delta, "Gamma": gamma,
                         "Vega_per_vol_point": vega / 100, "Theta_per_day": theta / 365})


def price_frame(df: pd.DataFrame) -> pd.Series:
    """Black–Scholes price for every row of nova_options.csv."""
    return pd.Series(bs_price(df["Spot"].to_numpy(), df["Strike"].to_numpy(), df["Time_to_Maturity"].to_numpy(),
                              df["Volatility"].to_numpy(), df["Interest_Rate"].to_numpy(),
                              (df["Option_Type"] == "Call").to_numpy()), index=df.index, name="BS_Price")


if __name__ == "__main__":
    from m08_data import load_options

    options = load_options()
    ours = price_frame(options)
    gap = (ours - options["Black_Scholes_Price"]).abs()
    print("Max |our BS − provided BS| (₹):", round(gap.max(), 4), "| mean:", round(gap.mean(), 4))
    print("Worked example (S 1500, K 1550, T 0.5, σ 0.25, r 0.07, call):",
          round(float(bs_price(1500, 1550, 0.5, 0.25, 0.07, True)), 2))

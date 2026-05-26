"""
Pandas-based technical indicators computed from OHLCV bar lists.

Each function accepts the list returned by get_ohlcv() and returns a
pandas Series indexed by date string, so results are easy to inspect
or pass back to the agent as JSON.
"""

import pandas as pd


def _close_series(bars: list[dict]) -> pd.Series:
    df = pd.DataFrame(bars)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")
    return df["close"].astype(float)


def sma(bars: list[dict], period: int = 20) -> pd.Series:
    """
    Simple Moving Average of closing prices over *period* days.

    Returns a Series indexed by date; the first (period-1) values are NaN.
    """
    return _close_series(bars).rolling(window=period).mean().rename(f"SMA_{period}")


def ema(bars: list[dict], period: int = 20) -> pd.Series:
    """
    Exponential Moving Average of closing prices over *period* days.

    Uses pandas ewm with adjust=False (standard EMA recurrence).
    Returns a Series indexed by date.
    """
    return (
        _close_series(bars)
        .ewm(span=period, adjust=False)
        .mean()
        .rename(f"EMA_{period}")
    )


def rsi(bars: list[dict], period: int = 14) -> pd.Series:
    """
    Relative Strength Index over *period* days (Wilder smoothing via ewm).

    Values range 0–100. Returns a Series indexed by date; the first
    *period* values are NaN.
    """
    close = _close_series(bars)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    alpha = 1 / period
    avg_gain = gain.ewm(alpha=alpha, adjust=False).mean()
    avg_loss = loss.ewm(alpha=alpha, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, float("inf"))
    return (100 - 100 / (1 + rs)).rename(f"RSI_{period}")

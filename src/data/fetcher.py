"""
Massive API data fetcher.

Loads MASSIVE_API_KEY from .env and exposes three functions:
  get_quote   – latest price / bid / ask for a ticker
  get_ohlcv   – daily OHLCV bars for the last N days
  get_volume  – most-recent single-day volume for a ticker
"""

import os
from datetime import date, timedelta

import requests
from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.environ["MASSIVE_API_KEY"]
_BASE_URL = "https://api.massiveapi.com/v1"  # adjust if the real base URL differs


def _headers() -> dict:
    return {"Authorization": f"Bearer {_API_KEY}", "Accept": "application/json"}


def _raise_for_status(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"Massive API error {response.status_code}: {response.text}"
        ) from exc


def get_quote(ticker: str) -> dict:
    """
    Return the latest real-time quote for *ticker*.

    Returns a dict with keys: ticker, price, bid, ask, change, change_pct,
    volume, timestamp.
    """
    url = f"{_BASE_URL}/quote"
    response = requests.get(url, headers=_headers(), params={"symbol": ticker}, timeout=10)
    _raise_for_status(response)
    return response.json()


def get_ohlcv(ticker: str, days: int = 30) -> list[dict]:
    """
    Return daily OHLCV bars for *ticker* covering the last *days* calendar days.

    Each element in the returned list is a dict with keys:
    date, open, high, low, close, volume.
    List is ordered oldest-first.
    """
    end = date.today()
    start = end - timedelta(days=days)
    url = f"{_BASE_URL}/historical"
    params = {
        "symbol": ticker,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "interval": "1d",
    }
    response = requests.get(url, headers=_headers(), params=params, timeout=10)
    _raise_for_status(response)
    data = response.json()
    # Normalise to a plain list regardless of wrapper key the API uses
    if isinstance(data, list):
        return data
    for key in ("data", "bars", "candles", "results"):
        if key in data:
            return data[key]
    return data


def get_volume(ticker: str) -> int:
    """
    Return the most-recent single-day trading volume for *ticker* as an integer.
    """
    bars = get_ohlcv(ticker, days=5)
    if not bars:
        raise ValueError(f"No OHLCV data returned for {ticker!r}")
    latest = bars[-1]
    return int(latest["volume"])

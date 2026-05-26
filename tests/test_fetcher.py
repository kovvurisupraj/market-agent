"""
Unit tests for src/data/fetcher.py.

All HTTP calls are mocked so no real network or API key is needed.
MASSIVE_API_KEY is patched via os.environ before the module is imported.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

# Provide a dummy key so the module-level os.environ["MASSIVE_API_KEY"] doesn't raise
os.environ.setdefault("MASSIVE_API_KEY", "test-key")

from src.data.fetcher import get_ohlcv, get_quote, get_volume  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

QUOTE_PAYLOAD = {
    "ticker": "AAPL",
    "price": 189.50,
    "bid": 189.48,
    "ask": 189.52,
    "change": 1.20,
    "change_pct": 0.64,
    "volume": 54_000_000,
    "timestamp": "2026-05-26T15:30:00Z",
}

BARS_PAYLOAD = [
    {"date": "2026-05-20", "open": 185.0, "high": 187.5, "low": 184.0, "close": 186.0, "volume": 50_000_000},
    {"date": "2026-05-21", "open": 186.0, "high": 190.0, "low": 185.5, "close": 189.5, "volume": 54_000_000},
]


def _mock_response(payload, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload
    resp.text = str(payload)
    if status_code >= 400:
        from requests import HTTPError
        resp.raise_for_status.side_effect = HTTPError(response=resp)
    else:
        resp.raise_for_status.return_value = None
    return resp


# ---------------------------------------------------------------------------
# get_quote
# ---------------------------------------------------------------------------

class TestGetQuote:
    def test_returns_quote_dict(self):
        with patch("src.data.fetcher.requests.get", return_value=_mock_response(QUOTE_PAYLOAD)) as mock_get:
            result = get_quote("AAPL")

        assert result["ticker"] == "AAPL"
        assert result["price"] == 189.50
        mock_get.assert_called_once()
        _, kwargs = mock_get.call_args
        assert kwargs["params"]["symbol"] == "AAPL"

    def test_ticker_uppercased_by_caller(self):
        with patch("src.data.fetcher.requests.get", return_value=_mock_response(QUOTE_PAYLOAD)) as mock_get:
            get_quote("aapl")

        _, kwargs = mock_get.call_args
        # fetcher itself does not uppercase — callers (tools) do; just confirm param is passed through
        assert kwargs["params"]["symbol"] == "aapl"

    def test_http_error_raises_runtime_error(self):
        with patch("src.data.fetcher.requests.get", return_value=_mock_response({}, status_code=401)):
            with pytest.raises(RuntimeError, match="Massive API error 401"):
                get_quote("AAPL")


# ---------------------------------------------------------------------------
# get_ohlcv
# ---------------------------------------------------------------------------

class TestGetOhlcv:
    def test_bare_list_response(self):
        with patch("src.data.fetcher.requests.get", return_value=_mock_response(BARS_PAYLOAD)):
            result = get_ohlcv("AAPL", days=7)

        assert isinstance(result, list)
        assert result[0]["date"] == "2026-05-20"

    @pytest.mark.parametrize("wrapper_key", ["data", "bars", "candles", "results"])
    def test_wrapped_response_keys(self, wrapper_key):
        payload = {wrapper_key: BARS_PAYLOAD}
        with patch("src.data.fetcher.requests.get", return_value=_mock_response(payload)):
            result = get_ohlcv("AAPL", days=7)

        assert result == BARS_PAYLOAD

    def test_date_range_params_sent(self):
        with patch("src.data.fetcher.requests.get", return_value=_mock_response(BARS_PAYLOAD)) as mock_get:
            get_ohlcv("TSLA", days=10)

        _, kwargs = mock_get.call_args
        assert kwargs["params"]["symbol"] == "TSLA"
        assert kwargs["params"]["interval"] == "1d"
        assert "start_date" in kwargs["params"]
        assert "end_date" in kwargs["params"]

    def test_http_error_raises_runtime_error(self):
        with patch("src.data.fetcher.requests.get", return_value=_mock_response({}, status_code=500)):
            with pytest.raises(RuntimeError, match="Massive API error 500"):
                get_ohlcv("AAPL")


# ---------------------------------------------------------------------------
# get_volume
# ---------------------------------------------------------------------------

class TestGetVolume:
    def test_returns_last_bar_volume(self):
        with patch("src.data.fetcher.requests.get", return_value=_mock_response(BARS_PAYLOAD)):
            vol = get_volume("AAPL")

        assert vol == 54_000_000

    def test_returns_int(self):
        float_bars = [{**BARS_PAYLOAD[-1], "volume": 54_000_000.0}]
        with patch("src.data.fetcher.requests.get", return_value=_mock_response(float_bars)):
            vol = get_volume("AAPL")

        assert isinstance(vol, int)

    def test_empty_bars_raises_value_error(self):
        with patch("src.data.fetcher.requests.get", return_value=_mock_response([])):
            with pytest.raises(ValueError, match="No OHLCV data"):
                get_volume("AAPL")

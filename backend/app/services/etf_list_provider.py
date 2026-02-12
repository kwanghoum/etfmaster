import csv
import io
import json
import logging

import httpx

from app.config import ALPHA_VANTAGE_API_KEY, DATA_DIR

logger = logging.getLogger(__name__)

FALLBACK_CSV = DATA_DIR / "etf_master_list.csv"


async def _fetch_from_nasdaq() -> list[str]:
    """Fetch ETF list from NASDAQ screener API."""
    url = "https://api.nasdaq.com/api/screener/etf?download=true"
    headers = {"User-Agent": "Mozilla/5.0"}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()

    data = resp.json()
    if "data" not in data or "data" not in data["data"]:
        return []

    rows = data["data"]["data"]["rows"]
    tickers = [row["symbol"] for row in rows if row.get("symbol")]
    return tickers


async def fetch_etf_tickers() -> list[str]:
    """Fetch ETF ticker list from NASDAQ. Falls back to Alpha Vantage, then local CSV."""
    try:
        tickers = await _fetch_from_nasdaq()
        if tickers:
            logger.info("Fetched %d ETF tickers from NASDAQ", len(tickers))
            return tickers
    except Exception:
        logger.exception("NASDAQ fetch failed, trying Alpha Vantage")

    try:
        tickers = await _fetch_from_alpha_vantage()
        if tickers:
            logger.info("Fetched %d ETF tickers from Alpha Vantage", len(tickers))
            return tickers
    except Exception:
        logger.exception("Alpha Vantage fetch failed, using fallback")

    tickers = _load_fallback_csv()
    logger.info("Loaded %d ETF tickers from fallback CSV", len(tickers))
    return tickers


async def _fetch_from_alpha_vantage() -> list[str]:
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "LISTING_STATUS",
        "apikey": ALPHA_VANTAGE_API_KEY,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()

    reader = csv.DictReader(io.StringIO(resp.text))
    tickers = []
    for row in reader:
        if row.get("assetType") == "ETF" and row.get("status") == "Active":
            tickers.append(row["symbol"])
    return tickers


def _load_fallback_csv() -> list[str]:
    if not FALLBACK_CSV.exists():
        logger.warning("Fallback CSV not found at %s", FALLBACK_CSV)
        return []
    with open(FALLBACK_CSV) as f:
        reader = csv.DictReader(f)
        return [row["ticker"] for row in reader if row.get("ticker")]

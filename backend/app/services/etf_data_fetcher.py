import logging
from datetime import datetime, timedelta

import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)


def fetch_etf_batch(tickers: list[str]) -> list[dict]:
    """Fetch ETF data for a batch of tickers using yfinance."""
    results = []
    for ticker in tickers:
        try:
            data = _fetch_single(ticker)
            if data:
                results.append(data)
        except Exception:
            logger.warning("Failed to fetch data for %s", ticker, exc_info=True)
    return results


def _fetch_single(ticker: str) -> dict | None:
    t = yf.Ticker(ticker)
    try:
        info = t.info
    except Exception:
        logger.warning("Could not get info for %s", ticker)
        return None

    if not info:
        return None

    # 상폐된 ETF는 quoteType이나 symbol이 없거나 이상함
    quote_type = info.get("quoteType")
    if quote_type not in ["ETF", "MUTUALFUND"]:
        logger.debug("Skipping %s - not an ETF (quoteType=%s)", ticker, quote_type)
        return None

    name = info.get("longName") or info.get("shortName")
    description = info.get("longBusinessSummary")
    exchange = info.get("exchange")
    price = info.get("regularMarketPrice") or info.get("previousClose")
    volume = info.get("volume") or info.get("averageVolume")

    market_cap = info.get("totalAssets") or info.get("marketCap")
    net_assets = info.get("netAssets")
    inception_date = info.get("firstTradeDateMilliseconds")

    expense_ratio = info.get("netExpenseRatio") or info.get("annualReportExpenseRatio")
    if expense_ratio is not None:
        expense_ratio = round(expense_ratio, 4)

    # yfinance: 'yield' is decimal (0.0105), 'dividendYield' is percent (1.05)
    dividend_yield = info.get("yield") or info.get("dividendYield")
    if dividend_yield is not None:
        # If using 'yield', convert to percent; if 'dividendYield', it's already percent
        if info.get("yield") is not None:
            dividend_yield = round(dividend_yield * 100, 4)
        else:
            dividend_yield = round(dividend_yield, 4)

    ex_dividend_date = info.get("exDividendDate")

    category = info.get("category")
    underlying_index = info.get("benchmark") or info.get("indexName")

    issuer_raw = info.get("fundFamily") or ""
    issuer = issuer_raw.strip() if issuer_raw else None

    # 3년/5년 평균 수익률 (yfinance에서 연평균으로 제공)
    return_3y_avg = info.get("threeYearAverageReturn")
    if return_3y_avg is not None:
        return_3y_avg = round(return_3y_avg * 100, 2)

    return_5y_avg = info.get("fiveYearAverageReturn")
    if return_5y_avg is not None:
        return_5y_avg = round(return_5y_avg * 100, 2)

    return {
        "ticker": ticker,
        "name": name,
        "description": description,
        "issuer": issuer,
        "category": category,
        "underlying_index": underlying_index,
        "exchange": exchange,
        "price": price,
        "volume": int(volume) if volume else None,
        "market_cap": int(market_cap) if market_cap else None,
        "net_assets": int(net_assets) if net_assets else None,
        "inception_date": int(inception_date) if inception_date else None,
        "expense_ratio": expense_ratio,
        "dividend_yield": dividend_yield,
        "ex_dividend_date": int(ex_dividend_date) if ex_dividend_date else None,
        "return_3y_avg": return_3y_avg,
        "return_5y_avg": return_5y_avg,
        "data_updated_at": datetime.utcnow(),
    }


def compute_returns(tickers: list[str]) -> dict[str, dict]:
    """Compute 1m, 1y, 3y, 5y returns for a list of tickers using bulk download."""
    if not tickers:
        return {}

    end = datetime.utcnow()
    start_5y = end - timedelta(days=365 * 5 + 30)

    try:
        df = yf.download(tickers, start=start_5y.strftime("%Y-%m-%d"),
                         end=end.strftime("%Y-%m-%d"), progress=False, threads=True)
    except Exception:
        logger.exception("Bulk download failed")
        return {}

    if df.empty:
        return {}

    close = df["Close"] if "Close" in df.columns else df.get("Adj Close", pd.DataFrame())
    if close.empty:
        return {}

    if isinstance(close, pd.Series):
        close = close.to_frame(name=tickers[0])

    results = {}
    now = close.index[-1]
    for t in tickers:
        if t not in close.columns:
            continue
        series = close[t].dropna()
        if len(series) < 2:
            continue
        current = series.iloc[-1]
        r = {}

        idx_1m = series.index[series.index >= now - pd.Timedelta(days=35)]
        if len(idx_1m) > 0:
            p = series.loc[idx_1m[0]]
            r["return_1m"] = round(((current - p) / p) * 100, 2)

        idx_1y = series.index[series.index >= now - pd.Timedelta(days=370)]
        if len(idx_1y) > 0:
            p = series.loc[idx_1y[0]]
            r["return_1y"] = round(((current - p) / p) * 100, 2)

        idx_3y = series.index[series.index >= now - pd.Timedelta(days=365 * 3 + 30)]
        if len(idx_3y) > 0:
            p = series.loc[idx_3y[0]]
            r["return_3y"] = round(((current - p) / p) * 100, 2)

        idx_5y = series.index[series.index >= now - pd.Timedelta(days=365 * 5 + 30)]
        if len(idx_5y) > 0:
            p = series.loc[idx_5y[0]]
            r["return_5y"] = round(((current - p) / p) * 100, 2)

        if r:
            results[t] = r

    return results

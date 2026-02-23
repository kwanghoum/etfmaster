import logging
import time
from datetime import datetime, timedelta

import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)

_DOWNLOAD_SUB_BATCH = 10  # yf.download()에 한 번에 넘길 최대 ticker 수


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
        time.sleep(0.5)  # 개별 ticker 간 딜레이 (429 방지)
    return results


def _fetch_single(ticker: str) -> dict | None:
    """단일 ticker 정보 조회. 429 발생 시 최대 2회 재시도."""
    info = None
    for attempt in range(3):
        try:
            t = yf.Ticker(ticker)
            info = t.info
            break  # 성공 시 루프 종료
        except Exception as e:
            err = str(e)
            if "429" in err or "Too Many Requests" in err:
                wait = 60 * (attempt + 1)  # 60s, 120s, 180s
                logger.warning("429 for %s (attempt %d), waiting %ds", ticker, attempt + 1, wait)
                time.sleep(wait)
            elif "Expecting value" in err or "char 0" in err:
                # 빈 응답 (일시적 차단) - 짧게 기다리고 1회 재시도
                if attempt == 0:
                    time.sleep(10)
                else:
                    logger.warning("Empty response for %s, skipping", ticker)
                    return None
            else:
                logger.warning("Could not get info for %s: %s", ticker, err)
                return None

    if not info:
        return None

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

    dividend_yield = info.get("yield") or info.get("dividendYield")
    if dividend_yield is not None:
        if info.get("yield") is not None:
            dividend_yield = round(dividend_yield * 100, 4)
        else:
            dividend_yield = round(dividend_yield, 4)

    ex_dividend_date = info.get("exDividendDate")
    category = info.get("category")
    underlying_index = info.get("benchmark") or info.get("indexName")

    issuer_raw = info.get("fundFamily") or ""
    issuer = issuer_raw.strip() if issuer_raw else None

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
    """Compute 1m, 1y, 3y, 5y returns. 10개씩 소분할하여 rate limit 완화."""
    if not tickers:
        return {}

    end = datetime.utcnow()
    start_5y = end - timedelta(days=365 * 5 + 30)
    all_results = {}

    for i in range(0, len(tickers), _DOWNLOAD_SUB_BATCH):
        sub = tickers[i: i + _DOWNLOAD_SUB_BATCH]
        try:
            df = yf.download(
                sub,
                start=start_5y.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
                progress=False,
                threads=False,
            )
        except Exception:
            logger.warning("Bulk download failed for sub-batch %s", sub)
            df = pd.DataFrame()

        if not df.empty:
            close = df["Close"] if "Close" in df.columns else df.get("Adj Close", pd.DataFrame())
            if isinstance(close, pd.Series):
                close = close.to_frame(name=sub[0])

            if not close.empty:
                now = close.index[-1]
                for t in sub:
                    if t not in close.columns:
                        continue
                    series = close[t].dropna()
                    if len(series) < 2:
                        continue
                    current = series.iloc[-1]
                    r = {}

                    for days, key in [(35, "return_1m"), (370, "return_1y"),
                                      (365 * 3 + 30, "return_3y"), (365 * 5 + 30, "return_5y")]:
                        idx = series.index[series.index >= now - pd.Timedelta(days=days)]
                        if len(idx) > 0:
                            p = series.loc[idx[0]]
                            r[key] = round(((current - p) / p) * 100, 2)

                    if r:
                        all_results[t] = r

        if i + _DOWNLOAD_SUB_BATCH < len(tickers):
            time.sleep(2)  # 서브 배치 간 딜레이

    return all_results

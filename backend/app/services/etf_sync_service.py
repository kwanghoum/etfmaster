import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import BATCH_SIZE, BATCH_DELAY_SECONDS
from app.database import SessionLocal
from app.models.etf import ETF
from app.services.etf_data_fetcher import compute_returns, fetch_etf_batch
from app.services.etf_list_provider import fetch_etf_tickers

logger = logging.getLogger(__name__)

_sync_running = False


async def run_full_sync() -> str:
    """Run a full ETF data synchronization."""
    global _sync_running
    if _sync_running:
        return "Sync already in progress"
    _sync_running = True
    try:
        return await _do_sync()
    finally:
        _sync_running = False


async def _do_sync() -> str:
    tickers = await fetch_etf_tickers()
    if not tickers:
        return "No tickers found"

    logger.info("Starting sync for %d tickers", len(tickers))
    total_updated = 0

    for i in range(0, len(tickers), BATCH_SIZE):
        batch = tickers[i : i + BATCH_SIZE]
        logger.info("Processing batch %d-%d of %d", i, i + len(batch), len(tickers))

        etf_data_list = await asyncio.to_thread(fetch_etf_batch, batch)
        returns = await asyncio.to_thread(compute_returns, batch)

        for data in etf_data_list:
            t = data["ticker"]
            if t in returns:
                data.update(returns[t])

        db = SessionLocal()
        try:
            for data in etf_data_list:
                _upsert_etf(db, data)
            db.commit()
            total_updated += len(etf_data_list)
        except Exception:
            db.rollback()
            logger.exception("DB error on batch %d", i)
        finally:
            db.close()

        if i + BATCH_SIZE < len(tickers):
            await asyncio.sleep(BATCH_DELAY_SECONDS)

    msg = f"Sync complete: {total_updated}/{len(tickers)} ETFs updated"
    logger.info(msg)
    return msg


def _upsert_etf(db: Session, data: dict) -> None:
    etf = db.query(ETF).filter(ETF.ticker == data["ticker"]).first()
    if etf:
        for k, v in data.items():
            if v is not None:
                setattr(etf, k, v)
        etf.data_updated_at = datetime.now(timezone.utc)
    else:
        etf = ETF(**data)
        db.add(etf)

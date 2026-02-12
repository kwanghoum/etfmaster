import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from app.config import PRICE_UPDATE_INTERVAL_HOURS, SYNC_HOUR, SYNC_MINUTE
from app.services.etf_sync_service import run_full_sync

logger = logging.getLogger(__name__)

# 한국 시간대 설정
KST = timezone('Asia/Seoul')
scheduler = AsyncIOScheduler(timezone=KST)


def _run_sync():
    logger.info("Scheduled sync triggered at %s", datetime.now(KST))
    asyncio.ensure_future(run_full_sync())


def start_scheduler():
    daily_job = scheduler.add_job(
        _run_sync,
        "cron",
        hour=SYNC_HOUR,
        minute=SYNC_MINUTE,
        id="daily_full_sync",
        replace_existing=True,
    )
    interval_job = scheduler.add_job(
        _run_sync,
        "interval",
        hours=PRICE_UPDATE_INTERVAL_HOURS,
        id="periodic_price_update",
        replace_existing=True,
    )
    scheduler.start()

    logger.info("Scheduler started (timezone: %s)", KST)
    logger.info("Daily full sync scheduled at %02d:%02d KST - Next run: %s",
                SYNC_HOUR, SYNC_MINUTE, daily_job.next_run_time)
    logger.info("Periodic price update every %d hours - Next run: %s",
                PRICE_UPDATE_INTERVAL_HOURS, interval_job.next_run_time)


def stop_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")

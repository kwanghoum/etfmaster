import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.routers.chat import router as chat_router
from app.routers.etfs import router as etfs_router
from app.services.etf_sync_service import run_full_sync
from app.tasks.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_scheduler()

    # DB가 비어있거나 스키마 변경 후 재sync 필요 시 자동 실행
    db = SessionLocal()
    try:
        from datetime import datetime, timedelta, timezone

        from app.models.etf import ETF
        count = db.query(ETF).count()

        needs_resync = False
        reason = ""

        if count < 10:
            needs_resync = True
            reason = f"DB has only {count} ETFs"
        else:
            # 최근 업데이트 시각 확인 - 24시간 이상 지났으면 재sync
            from sqlalchemy import func
            latest = db.query(func.max(ETF.data_updated_at)).scalar()
            if latest is None:
                needs_resync = True
                reason = "No data_updated_at found"
            else:
                # SQLite는 timezone-naive datetime을 반환할 수 있음
                if latest.tzinfo is None:
                    latest = latest.replace(tzinfo=timezone.utc)
                age = datetime.now(timezone.utc) - latest
                if age > timedelta(hours=24):
                    needs_resync = True
                    reason = f"Data is {age.days}d {age.seconds//3600}h old (last update: {latest})"

        if needs_resync:
            logger.info("Starting sync — reason: %s", reason)
            asyncio.ensure_future(run_full_sync())
        else:
            logger.info("DB has %d ETFs, data is fresh — skipping initial sync", count)
    finally:
        db.close()

    yield
    stop_scheduler()


app = FastAPI(title="ETF Master", version="0.1.0", lifespan=lifespan)

import os

# 환경에 따라 CORS 설정
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(etfs_router)
app.include_router(chat_router)

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
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
        from app.models.etf import ETF
        count = db.query(ETF).count()

        # ex_dividend_date 필드가 없는 데이터가 있으면 재sync
        needs_resync = False
        if count > 0:
            sample = db.query(ETF).first()
            if not hasattr(sample, 'ex_dividend_date'):
                logger.info("Schema changed — need to resync all ETFs")
                needs_resync = True

        if count < 10 or needs_resync:
            logger.info("DB has %d ETFs — starting initial sync in background", count)
            asyncio.ensure_future(run_full_sync())
        else:
            logger.info("DB has %d ETFs — skipping initial sync", count)
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

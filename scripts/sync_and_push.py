#!/usr/bin/env python3
"""Standalone ETF sync script — GitHub Actions에서 실행.

GitHub Actions 러너에서 yfinance로 ETF 데이터를 가져온 뒤
Railway PostgreSQL에 직접 upsert합니다 (HTTP/CDN 레이어 완전 우회).

필수 환경변수:
    DATABASE_URL   Railway PostgreSQL public URL
                   예) postgresql://postgres:pass@mainline.proxy.rlwy.net:12345/railway

사용:
    DATABASE_URL=postgresql://... python scripts/sync_and_push.py
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# backend/ 를 sys.path 에 추가해 app 모듈 임포트 가능하게 함
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.models.etf import ETF, Base
from app.services.etf_data_fetcher import compute_returns, fetch_etf_batch
from app.services.etf_list_provider import fetch_etf_tickers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "")
SYNC_BATCH_SIZE = 50    # yfinance 요청 배치 크기
BATCH_DELAY_SECONDS = 5  # 배치 간 딜레이 (rate limit 완화)
DB_WRITE_EVERY = 200    # 몇 건마다 DB에 flush할지


def upsert_batch(session: Session, records: list[dict]) -> int:
    """ETF 데이터를 DB에 upsert. 업데이트 건수 반환."""
    count = 0
    for data in records:
        if not data.get("ticker"):
            continue
        etf = session.query(ETF).filter(ETF.ticker == data["ticker"]).first()
        if etf:
            for k, v in data.items():
                if v is not None and hasattr(ETF, k):
                    setattr(etf, k, v)
        else:
            filtered = {k: v for k, v in data.items() if hasattr(ETF, k)}
            session.add(ETF(**filtered))
        count += 1
    return count


async def main() -> None:
    if not DATABASE_URL:
        logger.error("DATABASE_URL 환경변수가 설정되지 않았습니다.")
        sys.exit(1)

    # PostgreSQL 연결 (SSL 필수)
    connect_args = {}
    if DATABASE_URL.startswith("postgresql"):
        connect_args = {"sslmode": "require"}

    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    Base.metadata.create_all(bind=engine)
    logger.info("DB 연결 성공")

    logger.info("ETF 티커 목록 가져오는 중...")
    tickers = await fetch_etf_tickers()
    logger.info("총 %d개 티커 확인", len(tickers))

    pending: list[dict] = []
    total_written = 0

    for i in range(0, len(tickers), SYNC_BATCH_SIZE):
        batch = tickers[i: i + SYNC_BATCH_SIZE]
        logger.info("배치 처리 중: %d-%d / %d", i, i + len(batch), len(tickers))

        etf_data_list = await asyncio.to_thread(fetch_etf_batch, batch)
        returns = await asyncio.to_thread(compute_returns, batch)

        for data in etf_data_list:
            t = data["ticker"]
            if t in returns:
                data.update(returns[t])
            pending.append(data)

        # DB_WRITE_EVERY 건마다 flush
        if len(pending) >= DB_WRITE_EVERY:
            with Session(engine) as session:
                n = upsert_batch(session, pending)
                session.commit()
            total_written += n
            logger.info("DB 저장: %d건 (누적 %d건)", n, total_written)
            pending = []

        if i + SYNC_BATCH_SIZE < len(tickers):
            await asyncio.sleep(BATCH_DELAY_SECONDS)

    # 남은 데이터 저장
    if pending:
        with Session(engine) as session:
            n = upsert_batch(session, pending)
            session.commit()
        total_written += n
        logger.info("DB 저장 (최종): %d건 (누적 %d건)", n, total_written)

    logger.info("완료. 총 %d건 저장.", total_written)


if __name__ == "__main__":
    asyncio.run(main())

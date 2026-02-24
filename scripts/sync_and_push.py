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

# ── 1. DATABASE_URL 을 SSL 포함으로 정규화 (app 모듈 임포트 전에 수행) ──
_db_url = os.environ.get("DATABASE_URL", "")
if not _db_url:
    print("ERROR: DATABASE_URL 환경변수가 설정되지 않았습니다.")
    sys.exit(1)

# postgresql:// → psycopg2 드라이버 명시, SSL + search_path 강제
if _db_url.startswith("postgresql://") or _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    _sep = "&" if "?" in _db_url else "?"
    if "sslmode" not in _db_url:
        _db_url += f"{_sep}sslmode=require"
        _sep = "&"
    if "options" not in _db_url:
        _db_url += f"{_sep}options=-c+search_path%3Dpublic"

# app.config 가 os.environ 에서 읽으므로 미리 세팅
os.environ["DATABASE_URL"] = _db_url

# ── 2. backend/ 경로 추가 후 app 모듈 임포트 ──
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.orm import Session  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models.etf import ETF  # noqa: E402
from app.services.etf_data_fetcher import compute_returns, fetch_etf_batch  # noqa: E402
from app.services.etf_list_provider import fetch_etf_tickers  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

SYNC_BATCH_SIZE = 50     # yfinance 요청 배치 크기
BATCH_DELAY_SECONDS = 5  # 배치 간 딜레이
DB_WRITE_EVERY = 200     # 몇 건마다 DB flush 할지

_ETF_COLS = {c.key for c in ETF.__table__.columns} - {"id", "created_at"}


def upsert_batch(session: Session, records: list[dict]) -> int:
    count = 0
    for data in records:
        if not data.get("ticker"):
            continue
        row = {k: v for k, v in data.items() if k in _ETF_COLS}
        etf = session.query(ETF).filter(ETF.ticker == row["ticker"]).first()
        if etf:
            for k, v in row.items():
                if v is not None:
                    setattr(etf, k, v)
        else:
            session.add(ETF(**row))
        count += 1
    return count


async def main() -> None:
    # DB 연결 확인 및 테이블 생성
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("DB 연결 성공 (URL: %s)", _db_url.split("@")[-1])
    except Exception as e:
        logger.error("DB 연결 실패: %s", e)
        sys.exit(1)

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

        if len(pending) >= DB_WRITE_EVERY:
            try:
                with SessionLocal() as session:
                    n = upsert_batch(session, pending)
                    session.commit()
                total_written += n
                logger.info("DB 저장: %d건 (누적 %d건)", n, total_written)
            except Exception as e:
                logger.error("DB 저장 실패: %s", e, exc_info=True)
                sys.exit(1)
            pending = []

        if i + SYNC_BATCH_SIZE < len(tickers):
            await asyncio.sleep(BATCH_DELAY_SECONDS)

    if pending:
        try:
            with SessionLocal() as session:
                n = upsert_batch(session, pending)
                session.commit()
            total_written += n
            logger.info("DB 저장 (최종): %d건 (누적 %d건)", n, total_written)
        except Exception as e:
            logger.error("DB 저장 실패: %s", e, exc_info=True)
            sys.exit(1)

    logger.info("완료. 총 %d건 저장.", total_written)


if __name__ == "__main__":
    asyncio.run(main())

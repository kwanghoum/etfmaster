#!/usr/bin/env python3
"""Standalone ETF sync script — GitHub Actions에서 실행.

로컬(또는 GitHub Actions 러너)에서 yfinance로 ETF 데이터를 가져온 뒤
Railway 서버의 /api/admin/bulk-update 엔드포인트로 전송합니다.

필수 환경변수:
    RAILWAY_URL   예) https://your-app.up.railway.app
    ADMIN_API_KEY Railway 서버와 동일한 값

사용:
    RAILWAY_URL=https://... ADMIN_API_KEY=secret python scripts/sync_and_push.py
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

# backend/ 를 sys.path 에 추가해 app.services 임포트 가능하게 함
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.etf_data_fetcher import compute_returns, fetch_etf_batch
from app.services.etf_list_provider import fetch_etf_tickers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

RAILWAY_URL = os.environ.get("RAILWAY_URL", "").rstrip("/")
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "")

SYNC_BATCH_SIZE = 50       # yfinance 요청 배치 크기
PUSH_BATCH_SIZE = 500      # Railway API 전송 배치 크기
BATCH_DELAY_SECONDS = 5    # 배치 간 딜레이 (rate limit 완화)


def _serialize(data: dict) -> dict:
    """datetime → ISO 문자열 변환."""
    out = {}
    for k, v in data.items():
        if isinstance(v, datetime):
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


async def push_to_railway(client: httpx.AsyncClient, records: list[dict]) -> None:
    for i in range(0, len(records), PUSH_BATCH_SIZE):
        batch = [_serialize(r) for r in records[i: i + PUSH_BATCH_SIZE]]
        resp = await client.post(
            f"{RAILWAY_URL}/api/admin/bulk-update",
            json=batch,
            headers={"x-admin-key": ADMIN_API_KEY},
            timeout=120,
        )
        resp.raise_for_status()
        result = resp.json()
        logger.info(
            "Pushed records %d-%d → Railway updated=%s",
            i, i + len(batch), result.get("updated"),
        )


async def main() -> None:
    if not RAILWAY_URL:
        logger.error("RAILWAY_URL 환경변수가 설정되지 않았습니다.")
        sys.exit(1)
    if not ADMIN_API_KEY:
        logger.error("ADMIN_API_KEY 환경변수가 설정되지 않았습니다.")
        sys.exit(1)

    logger.info("ETF 티커 목록 가져오는 중...")
    tickers = await fetch_etf_tickers()
    logger.info("총 %d개 티커 확인", len(tickers))

    all_data: list[dict] = []

    async with httpx.AsyncClient() as client:
        for i in range(0, len(tickers), SYNC_BATCH_SIZE):
            batch = tickers[i: i + SYNC_BATCH_SIZE]
            logger.info("배치 처리 중: %d-%d / %d", i, i + len(batch), len(tickers))

            etf_data_list = await asyncio.to_thread(fetch_etf_batch, batch)
            returns = await asyncio.to_thread(compute_returns, batch)

            for data in etf_data_list:
                t = data["ticker"]
                if t in returns:
                    data.update(returns[t])
                all_data.append(data)

            # 일정량 쌓이면 중간 전송 (메모리 절약 + 진행 상황 저장)
            if len(all_data) >= PUSH_BATCH_SIZE * 2:
                logger.info("중간 전송: %d건", len(all_data))
                await push_to_railway(client, all_data)
                all_data = []

            if i + SYNC_BATCH_SIZE < len(tickers):
                await asyncio.sleep(BATCH_DELAY_SECONDS)

        # 남은 데이터 전송
        if all_data:
            logger.info("최종 전송: %d건", len(all_data))
            await push_to_railway(client, all_data)

    logger.info("완료.")


if __name__ == "__main__":
    asyncio.run(main())

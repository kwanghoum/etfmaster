import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "etfmaster.db"

# Railway가 DATABASE_URL 환경변수를 자동으로 설정하면 사용, 없으면 로컬 SQLite
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")

BATCH_SIZE = 100
BATCH_DELAY_SECONDS = 1

SYNC_HOUR = 6
SYNC_MINUTE = 0
PRICE_UPDATE_INTERVAL_HOURS = 2

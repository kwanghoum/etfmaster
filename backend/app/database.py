from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import DATABASE_URL, DATA_DIR

# SQLite 사용 시에만 디렉토리 생성
if DATABASE_URL.startswith("sqlite"):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # PostgreSQL 사용 시. Neon 등 서버리스 DB는 유휴 연결을 수 분 만에 끊으므로
    # pre_ping으로 죽은 연결을 감지해 자동 재연결한다.
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=240)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

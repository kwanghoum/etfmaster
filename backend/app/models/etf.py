from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ETF(Base):
    __tablename__ = "etfs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(16), unique=True, index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(256))
    description: Mapped[str | None] = mapped_column(String(2048))
    issuer: Mapped[str | None] = mapped_column(String(128))
    category: Mapped[str | None] = mapped_column(String(128))
    underlying_index: Mapped[str | None] = mapped_column(String(256))
    exchange: Mapped[str | None] = mapped_column(String(32))
    price: Mapped[float | None] = mapped_column(Float)
    volume: Mapped[int | None] = mapped_column(BigInteger)
    market_cap: Mapped[int | None] = mapped_column(BigInteger)
    net_assets: Mapped[int | None] = mapped_column(BigInteger)
    inception_date: Mapped[int | None] = mapped_column(BigInteger)
    expense_ratio: Mapped[float | None] = mapped_column(Float)
    dividend_yield: Mapped[float | None] = mapped_column(Float)
    ex_dividend_date: Mapped[int | None] = mapped_column(BigInteger)
    return_1m: Mapped[float | None] = mapped_column(Float)
    return_1y: Mapped[float | None] = mapped_column(Float)
    return_3y: Mapped[float | None] = mapped_column(Float)
    return_3y_avg: Mapped[float | None] = mapped_column(Float)
    return_5y: Mapped[float | None] = mapped_column(Float)
    return_5y_avg: Mapped[float | None] = mapped_column(Float)
    data_updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

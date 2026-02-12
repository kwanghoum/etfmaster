from datetime import datetime, timezone

from pydantic import BaseModel, field_serializer


class ETFResponse(BaseModel):
    model_config = {"from_attributes": True}

    ticker: str
    name: str | None = None
    description: str | None = None
    issuer: str | None = None
    category: str | None = None
    underlying_index: str | None = None
    exchange: str | None = None
    price: float | None = None
    volume: int | None = None
    market_cap: int | None = None
    net_assets: int | None = None
    inception_date: int | None = None
    expense_ratio: float | None = None
    dividend_yield: float | None = None
    ex_dividend_date: int | None = None
    return_1m: float | None = None
    return_1y: float | None = None
    return_3y: float | None = None
    return_3y_avg: float | None = None
    return_5y: float | None = None
    return_5y_avg: float | None = None
    data_updated_at: datetime | None = None

    @field_serializer('data_updated_at')
    def serialize_datetime(self, dt: datetime | None, _info):
        if dt is None:
            return None
        # Ensure timezone-aware datetime with UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


class ETFListResponse(BaseModel):
    items: list[ETFResponse]
    total: int


class FilterOptions(BaseModel):
    categories: list[str]
    issuers: list[str]


class SyncStatus(BaseModel):
    status: str
    message: str

import asyncio
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.etf import ETF
from app.schemas.etf import ETFListResponse, ETFResponse, FilterOptions, SyncStatus
from app.services.etf_sync_service import run_full_sync

router = APIRouter(prefix="/api")

SORT_COLUMNS = {
    "ticker": ETF.ticker,
    "name": ETF.name,
    "issuer": ETF.issuer,
    "category": ETF.category,
    "exchange": ETF.exchange,
    "price": ETF.price,
    "volume": ETF.volume,
    "market_cap": ETF.market_cap,
    "net_assets": ETF.net_assets,
    "inception_date": ETF.inception_date,
    "expense_ratio": ETF.expense_ratio,
    "dividend_yield": ETF.dividend_yield,
    "ex_dividend_date": ETF.ex_dividend_date,
    "return_1m": ETF.return_1m,
    "return_1y": ETF.return_1y,
    "return_3y_avg": ETF.return_3y_avg,
    "return_5y": ETF.return_5y,
    "return_5y_avg": ETF.return_5y_avg,
    "data_updated_at": ETF.data_updated_at,
}


@router.get("/etfs", response_model=ETFListResponse)
def list_etfs(
    sort_by: str = Query("ticker", enum=list(SORT_COLUMNS.keys())),
    sort_dir: Literal["asc", "desc"] = Query("asc"),
    search: str | None = Query(None),
    category: str | None = Query(None),
    issuer: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(0, ge=0, le=5000),
    db: Session = Depends(get_db),
):
    q = db.query(ETF)

    if search:
        term = f"%{search}%"
        q = q.filter((ETF.ticker.ilike(term)) | (ETF.name.ilike(term)))

    if category:
        q = q.filter(ETF.category == category)
    if issuer:
        q = q.filter(ETF.issuer == issuer)

    total = q.count()

    col = SORT_COLUMNS.get(sort_by, ETF.ticker)
    order = col.desc() if sort_dir == "desc" else col.asc()
    q = q.order_by(order)

    if per_page > 0:
        q = q.offset((page - 1) * per_page).limit(per_page)

    items = [ETFResponse.model_validate(e) for e in q.all()]
    return ETFListResponse(items=items, total=total)


@router.get("/etfs/filters", response_model=FilterOptions)
def get_filters(db: Session = Depends(get_db)):
    categories = [
        r[0]
        for r in db.query(ETF.category).filter(ETF.category.isnot(None)).distinct().order_by(ETF.category).all()
    ]
    issuers = [
        r[0]
        for r in db.query(ETF.issuer).filter(ETF.issuer.isnot(None)).distinct().order_by(ETF.issuer).all()
    ]
    return FilterOptions(categories=categories, issuers=issuers)


@router.get("/etfs/{ticker}", response_model=ETFResponse | None)
def get_etf(ticker: str, db: Session = Depends(get_db)):
    etf = db.query(ETF).filter(func.upper(ETF.ticker) == ticker.upper()).first()
    if not etf:
        return None
    return ETFResponse.model_validate(etf)


@router.post("/admin/sync", response_model=SyncStatus)
async def trigger_sync():
    asyncio.ensure_future(run_full_sync())
    return SyncStatus(status="started", message="Sync started in background")

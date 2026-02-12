# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ETF Master is a full-stack web application for browsing and analyzing US-listed ETFs (~4400+ ETFs). It features a real-time dashboard with sortable columns, search, and live data synchronization from financial APIs.

**Tech Stack:**
- **Backend:** Python FastAPI + SQLAlchemy + SQLite
- **Frontend:** Next.js 16 (App Router) + TypeScript + Tailwind CSS
- **Data Sources:** NASDAQ API (ETF list), yfinance (ETF data)
- **UI Libraries:** TanStack Table (sorting), TanStack Virtual (row virtualization), TanStack React Query (data fetching)

## Development Commands

### Running the Application

```bash
# Run both backend and frontend concurrently (from project root)
npm run dev

# Run backend only (from backend/)
uvicorn app.main:app --reload --port 8000

# Run frontend only (from frontend/)
npm run dev
```

### Backend Setup

```bash
# Install dependencies (from backend/)
pip install fastapi uvicorn sqlalchemy pydantic yfinance apscheduler httpx pandas

# Manual sync trigger (after backend is running)
curl -X POST http://localhost:8000/api/admin/sync

# Access API docs
# http://localhost:8000/docs (Swagger UI)
```

### Frontend Setup

```bash
# Install dependencies (from frontend/)
npm install

# Build for production
npm run build
```

### Database Management

```bash
# Reset database (delete and recreate)
rm -f backend/data/etfmaster.db
# Then restart the server - it will auto-sync if DB has < 10 ETFs
```

## Architecture

### Data Flow Pipeline

1. **ETF List Acquisition** (on startup if DB empty):
   - Primary: NASDAQ API → ~4433 active ETFs
   - Fallback: Alpha Vantage API → filtered for active ETFs

2. **Data Synchronization** (`etf_sync_service.py`):
   - Batches of 100 tickers with 1-second delay between batches
   - For each ticker: `yfinance` fetches price, volume, AUM, expense ratio, dividend yield, description
   - Bulk download historical prices via `yf.download()` for return calculations
   - Filters out non-ETFs (checks `quoteType == "ETF"`)
   - Upserts to SQLite DB with `data_updated_at` timestamp

3. **Scheduled Updates** (APScheduler):
   - Daily full sync: 6:00 AM
   - Price updates: Every 2 hours
   - Auto-starts on backend lifespan

4. **API Layer** (`routers/etfs.py`):
   - `GET /api/etfs` - List ETFs with server-side filtering/pagination support (but frontend uses client-side)
   - `GET /api/etfs/{ticker}` - Single ETF detail
   - `GET /api/etfs/filters` - Available categories/issuers
   - `POST /api/admin/sync` - Manual sync trigger

5. **Frontend Data Flow**:
   - React Query fetches all ETFs once (`per_page=0`)
   - Client-side filtering/sorting via TanStack Table (no network round-trips)
   - Virtual scrolling renders ~40 visible rows out of 4400+
   - Auto-refresh every 5 minutes

### Key Backend Components

- **`app/models/etf.py`**: SQLAlchemy ORM model (17 fields including ticker, price, returns, dividend_yield, description)
- **`app/services/etf_list_provider.py`**: ETF ticker list fetching with fallback chain
- **`app/services/etf_data_fetcher.py`**: Individual ETF data fetching + return calculations
- **`app/services/etf_sync_service.py`**: Orchestrates batch processing with rate limiting
- **`app/tasks/scheduler.py`**: APScheduler configuration for periodic syncs
- **`app/database.py`**: SQLAlchemy engine/session management

### Key Frontend Components

- **`components/EtfDashboard.tsx`**: Root component managing search/sorting state
- **`components/EtfTable.tsx`**: Virtualized table with TanStack Table + TanStack Virtual
- **`components/EtfTableColumns.tsx`**: Column definitions (16 columns) with custom formatters and sorting
- **`components/Tooltip.tsx`**: Radix UI tooltip for ETF descriptions on name hover
- **`hooks/useEtfData.ts`**: React Query hook for ETF data fetching
- **`lib/formatters.ts`**: Number/date formatting utilities (price, volume, market cap, returns, Korean timezone)
- **`lib/api.ts`**: API client functions

### Database Schema

**Table: `etfs`**
- `ticker` (VARCHAR(16), UNIQUE) - Primary identifier
- `name`, `description` (VARCHAR) - ETF name and long business summary
- `exchange`, `issuer`, `category` (VARCHAR) - Classification fields
- `price`, `volume` (FLOAT/BIGINT) - Market data
- `market_cap` (BIGINT) - Total assets (AUM)
- `expense_ratio`, `dividend_yield` (FLOAT) - Cost/yield percentages
- `return_1m`, `return_1y`, `return_3y_avg`, `return_5y`, `return_5y_avg` (FLOAT) - Performance metrics
- `data_updated_at` (DATETIME) - Last sync timestamp (displayed in Korean timezone)
- `created_at` (DATETIME) - Record creation time

### Important Behavioral Notes

**Backend:**
- Initial sync runs automatically on startup if DB has < 10 ETFs
- Sync is blocking with global `_sync_running` flag to prevent concurrent syncs
- yfinance can fail for delisted ETFs - these are filtered out via `quoteType` check
- Expense ratio and dividend yield are stored as percentages (0.09 = 0.09%, not 9%)
- Returns are stored as percentages (5.0 = +5.0%)

**Frontend:**
- All 4400+ ETFs loaded at once for instant client-side sorting/filtering
- Ticker column links to Yahoo Finance (`https://finance.yahoo.com/quote/{ticker}/`)
- Name column shows description tooltip on hover (Radix UI)
- Date/time formatted in Korean timezone (`ko-KR`, `Asia/Seoul`)
- Sorting state managed by TanStack Table, uses `table.getRowModel()` for final sorted+filtered rows
- Virtual scrolling estimates 40px row height

**Configuration (`backend/app/config.py`):**
- `BATCH_SIZE = 100` - Tickers per batch
- `BATCH_DELAY_SECONDS = 1` - Delay between batches (rate limiting)
- `SYNC_HOUR = 6`, `SYNC_MINUTE = 0` - Daily sync time
- `PRICE_UPDATE_INTERVAL_HOURS = 2` - Price refresh frequency

## Common Issues

**"DB deleted. Restart to add description field."** - Schema changed, need to drop and recreate DB.

**Sorting not working** - Ensure `table.getRowModel()` is used (not `getFilteredRowModel()` alone).

**Cannot update component while rendering** - State updates must be in `useEffect`, not during render.

**Sync taking too long** - 4433 ETFs × 100 batch size = ~45 batches × ~10 sec/batch = ~7-10 minutes. This is expected for initial sync.

**Few ETFs showing** - Check if API fetching failed. Review logs for "Fetched X ETF tickers from NASDAQ" or "Alpha Vantage fetch failed".

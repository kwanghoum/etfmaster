# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ETF Master is a full-stack web application for browsing and analyzing US-listed ETFs (~4400+ ETFs). It features a dashboard with sortable columns, search, and daily data synchronization from financial APIs.

**Tech Stack:**
- **Frontend + Production API:** Next.js 16 (App Router) + TypeScript + Tailwind CSS; route handlers query PostgreSQL directly via `pg`
- **Backend (local dev only):** Python FastAPI + SQLAlchemy + SQLite
- **Data Sources:** NASDAQ API (ETF list), yfinance (ETF data)
- **UI Libraries:** TanStack Table (sorting), TanStack Virtual (row virtualization), TanStack React Query (data fetching)

**Production Deployment (free tier, see DEPLOYMENT.md):**
- **Vercel** (https://etfmaster.vercel.app): Next.js frontend + read-only API (`frontend/src/app/api/etfs/*`), function region pinned to `sin1` via `frontend/vercel.json`
- **Neon:** Free PostgreSQL (Singapore region)
- **GitHub Actions:** Daily sync at 06:00 KST (`.github/workflows/etf-sync.yml` → `scripts/sync_and_push.py` upserts to PostgreSQL; imports `backend/` modules, so keep `backend/` even though it is not deployed)
- `frontend/src/lib/api.ts` targets `localhost:8000` in dev mode and same-origin `/api` in production (override with `NEXT_PUBLIC_API_URL`)

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
pip install -r requirements.txt

# Manual sync trigger (after backend is running)
curl -X POST http://localhost:8000/api/admin/sync

# Access API docs (local only)
# http://localhost:8000/docs (Swagger UI)
```

### Frontend Setup

```bash
# Install dependencies (from frontend/)
npm install

# Build for production
npm run build
```

### Database Management (local SQLite)

```bash
# Reset database (delete and recreate)
npm run db:reset
# Then restart the server - it will auto-sync if DB has < 10 ETFs
```

### Production Data Sync

```bash
gh workflow run etf-sync.yml                     # trigger manually
gh run list --workflow=etf-sync.yml --limit 1    # check status
```

## Architecture

### Production Data Flow

1. **GitHub Actions** (daily 06:00 KST or manual dispatch) runs `scripts/sync_and_push.py`:
   - Fetches ticker list (NASDAQ API, Alpha Vantage fallback)
   - yfinance batches of 50 tickers with 5-second delay; upserts to Neon PostgreSQL every 200 records
   - Creates the `etfs` table automatically on first run
2. **Vercel route handlers** (`frontend/src/app/api/etfs/*`) serve read-only queries from Neon via `pg`
3. **Frontend** loads all ETFs once (`per_page=0`), then filters/sorts client-side

### Local Dev Data Flow

1. FastAPI starts; if SQLite DB has < 10 ETFs, full sync runs automatically on startup
2. APScheduler: daily full sync 6:00 AM, price updates every 2 hours
3. Frontend (dev mode) calls FastAPI at `localhost:8000`

### API Endpoints

Same paths in both environments (FastAPI locally, Next.js route handlers in production):
- `GET /api/etfs` - List with search/category/issuer filtering, sorting, pagination (frontend uses `per_page=0` = all)
- `GET /api/etfs/{ticker}` - Single ETF (case-insensitive; returns `null` if not found)
- `GET /api/etfs/filters` - Distinct categories/issuers
- FastAPI only: `POST /api/admin/sync` (local sync trigger), `POST /api/admin/bulk-update` (upsert with `X-Admin-Key`)

### Key Backend Components

- **`app/models/etf.py`**: SQLAlchemy ORM model
- **`app/services/etf_list_provider.py`**: ETF ticker list fetching with fallback chain
- **`app/services/etf_data_fetcher.py`**: Individual ETF data fetching + return calculations
- **`app/services/etf_sync_service.py`**: Batch orchestration for local FastAPI sync
- **`app/tasks/scheduler.py`**: APScheduler configuration (local only)
- **`app/database.py`**: Engine/session management; `pool_pre_ping=True` for PostgreSQL (Neon kills idle connections)
- **`scripts/sync_and_push.py`**: Standalone sync for GitHub Actions (writes to `DATABASE_URL`)

### Key Frontend Components

- **`src/app/api/etfs/`**: Production API route handlers (`route.ts`, `filters/route.ts`, `[ticker]/route.ts`)
- **`src/lib/db.ts`**: `pg` pool singleton + shared SELECT field list (BIGINT→float8 casts, UTC ISO timestamp formatting to match FastAPI serialization)
- **`src/components/EtfDashboard.tsx`**: Root component managing search/sorting state
- **`src/components/EtfTable.tsx`**: Virtualized table with TanStack Table + TanStack Virtual
- **`src/components/EtfTableColumns.tsx`**: Column definitions with custom formatters and sorting
- **`src/components/Tooltip.tsx`**: Radix UI tooltip for ETF descriptions on name hover
- **`src/hooks/useEtfData.ts`**: React Query hooks for ETF data fetching
- **`src/lib/formatters.ts`**: Number/date formatting utilities (Korean timezone)
- **`src/lib/api.ts`**: API client (base URL selection per environment)

### Database Schema

**Table: `etfs`** (same schema in SQLite and PostgreSQL; see `app/models/etf.py`)
- `ticker` (VARCHAR(16), UNIQUE) - Primary identifier
- `name`, `description`, `issuer`, `category`, `underlying_index`, `exchange` (VARCHAR)
- `price` (FLOAT), `volume`, `market_cap`, `net_assets` (BIGINT)
- `inception_date`, `ex_dividend_date` (BIGINT, unix timestamps)
- `expense_ratio`, `dividend_yield` (FLOAT) - percentages
- `return_1m`, `return_1y`, `return_3y`, `return_3y_avg`, `return_5y`, `return_5y_avg` (FLOAT) - percentages
- `data_updated_at` (DATETIME, UTC) - Last sync timestamp (displayed in Korean timezone)
- `created_at` (DATETIME)

## Important Behavioral Notes

**Data:**
- yfinance can fail for delisted ETFs - these are filtered out via `quoteType == "ETF"` check
- Expense ratio and dividend yield are stored as percentages (0.09 = 0.09%, not 9%)
- Returns are stored as percentages (5.0 = +5.0%)

**Production API (route handlers):**
- `sort_by` is validated against a column whitelist; BIGINT columns are cast to float8 so `pg` returns numbers, not strings
- `data_updated_at` is formatted in SQL to `YYYY-MM-DDTHH:MI:SS+00:00` for parity with FastAPI's Pydantic serialization

**Frontend:**
- All 4400+ ETFs loaded at once for instant client-side sorting/filtering
- Ticker column links to Yahoo Finance (`https://finance.yahoo.com/quote/{ticker}/`)
- Date/time formatted in Korean timezone (`ko-KR`, `Asia/Seoul`)
- Sorting state managed by TanStack Table, uses `table.getRowModel()` for final sorted+filtered rows
- Virtual scrolling estimates 40px row height

**Configuration:**
- Local sync (`backend/app/config.py`): `BATCH_SIZE=100`, `BATCH_DELAY_SECONDS=1`, `SYNC_HOUR=6`, `PRICE_UPDATE_INTERVAL_HOURS=2`
- Actions sync (`scripts/sync_and_push.py`): `SYNC_BATCH_SIZE=50`, `BATCH_DELAY_SECONDS=5`, `DB_WRITE_EVERY=200`

## Common Issues

**Production API returns `{"detail":"Database query failed"}`** - Check Vercel `DATABASE_URL` (must start with `postgresql://`, pooler host), redeploy after env changes, check Vercel runtime logs. See DEPLOYMENT.md.

**Sync fails with "SSL connection has been closed unexpectedly"** - Neon closes idle connections; fixed by `pool_pre_ping=True` in `app/database.py`.

**Scheduled sync not running** - GitHub disables scheduled workflows after 60 days of repo inactivity: `gh workflow enable etf-sync.yml`.

**Sorting not working** - Ensure `table.getRowModel()` is used (not `getFilteredRowModel()` alone).

**Cannot update component while rendering** - State updates must be in `useEffect`, not during render.

**Full sync duration** - GitHub Actions: 1-2 hours (rate-limited yfinance batches). Local FastAPI initial sync: ~7-10 minutes.

**Few ETFs showing** - Check sync logs for "Fetched X ETF tickers from NASDAQ" or "Alpha Vantage fetch failed".

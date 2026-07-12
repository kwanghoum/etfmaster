# ETF Master

미국 상장 ETF(~4,400개 이상)를 조회하고 분석할 수 있는 풀스택 웹 애플리케이션입니다.

**라이브 데모**: https://etfmaster.vercel.app

## 주요 기능

- **ETF 데이터**: 4,400개 이상의 미국 상장 ETF 정보 제공 (매일 06:00 KST 자동 업데이트)
- **정렬 및 검색**: 모든 컬럼에 대한 정렬 및 실시간 검색 기능
- **성능 최적화**: 가상 스크롤링으로 수천 개의 데이터를 부드럽게 표시
- **상세 정보**: 가격, 수익률(1개월~5년), 배당률, 운용비용, 자산규모(AUM), 상장일 등

## 기술 스택

### 프로덕션 (무료 운영 — [DEPLOYMENT.md](./DEPLOYMENT.md) 참고)
- **Vercel** - Next.js 프론트엔드 + API 라우트 (읽기 전용, `pg`로 PostgreSQL 직접 조회)
- **Neon** - 무료 PostgreSQL 데이터베이스
- **GitHub Actions** - 매일 yfinance 데이터 동기화

### Frontend
- **Next.js 16** (App Router) + **TypeScript** + **Tailwind CSS**
- **TanStack Table / Virtual / React Query** - 정렬·가상 스크롤·서버 상태 관리

### Backend (로컬 개발 전용)
- **Python FastAPI** + **SQLAlchemy** + **SQLite**
- **APScheduler** - 주기적 동기화 스케줄러
- **yfinance** - Yahoo Finance 데이터 수집

## 빠른 시작 (로컬 개발)

### 사전 요구사항

- Python 3.11 이상
- Node.js 18 이상

### 설치 및 실행

```bash
git clone <repository-url>
cd etfmaster

# 루트 의존성 (concurrently)
npm install

# 백엔드 의존성
cd backend && pip install -r requirements.txt && cd ..

# 프론트엔드 의존성
cd frontend && npm install && cd ..

# 백엔드 + 프론트엔드 동시 실행
npm run dev
```

- 백엔드: http://localhost:8000 (Swagger UI: `/docs`)
- 프론트엔드: http://localhost:3000

로컬 개발은 SQLite를 사용하며 프로덕션 DB를 건드리지 않습니다. 첫 실행 시 DB가 비어 있으면 자동으로 전체 동기화가 시작됩니다 (~7-10분).

## 데이터 동기화

### 프로덕션 (GitHub Actions → Neon PostgreSQL)
- **자동**: 매일 06:00 KST (`.github/workflows/etf-sync.yml`)
- **수동**: `gh workflow run etf-sync.yml` (전체 동기화 1~2시간 소요)

### 로컬 (FastAPI → SQLite)
```bash
npm run sync          # 백엔드 실행 중일 때
npm run db:reset      # DB 초기화 (이후 서버 재시작 시 재동기화)
```

## API 엔드포인트

프로덕션과 로컬이 같은 경로를 사용합니다:

- `GET /api/etfs` - ETF 목록 (검색/필터/정렬/페이지네이션 지원)
- `GET /api/etfs/{ticker}` - 특정 ETF 상세 정보
- `GET /api/etfs/filters` - 카테고리/발행사 목록
- `POST /api/admin/sync` - 수동 동기화 (로컬 FastAPI 전용)

## 프로젝트 구조

```
etfmaster/
├── .github/workflows/
│   └── etf-sync.yml            # 매일 데이터 동기화 (프로덕션)
├── scripts/
│   └── sync_and_push.py        # GitHub Actions용 동기화 스크립트
├── backend/                    # FastAPI (로컬 개발 전용)
│   └── app/
│       ├── main.py             # 애플리케이션 진입점
│       ├── config.py           # 설정 (배치 크기, 동기화 시간 등)
│       ├── database.py         # DB 연결 (SQLite/PostgreSQL)
│       ├── models/etf.py       # SQLAlchemy 모델
│       ├── schemas/etf.py      # Pydantic 스키마
│       ├── routers/etfs.py     # API 라우터
│       ├── services/           # 티커 수집·데이터 fetch·동기화 로직
│       └── tasks/scheduler.py  # APScheduler 설정
├── frontend/                   # Next.js (프로덕션 배포 대상)
│   ├── vercel.json             # 함수 리전 고정 (sin1)
│   └── src/
│       ├── app/
│       │   ├── page.tsx        # 메인 페이지
│       │   └── api/etfs/       # 프로덕션 API 라우트 (PostgreSQL 조회)
│       ├── components/         # 대시보드·테이블·검색 컴포넌트
│       ├── hooks/useEtfData.ts # React Query 훅
│       └── lib/
│           ├── api.ts          # API 클라이언트
│           ├── db.ts           # pg 커넥션 풀
│           └── formatters.ts   # 숫자/날짜 포맷터
├── DEPLOYMENT.md               # 배포·운영 가이드
├── CLAUDE.md                   # AI 개발 가이드
└── README.md                   # 이 파일
```

## 데이터베이스 스키마

**테이블: `etfs`** (SQLite/PostgreSQL 동일)

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| ticker | VARCHAR(16) | 티커 심볼 (UNIQUE) |
| name / description | VARCHAR | 이름 / 상세 설명 |
| issuer / category / exchange | VARCHAR | 발행사 / 카테고리 / 거래소 |
| underlying_index | VARCHAR | 추종 지수 |
| price | FLOAT | 현재 가격 |
| volume | BIGINT | 거래량 |
| market_cap / net_assets | BIGINT | 자산규모 (AUM) / 순자산 |
| inception_date / ex_dividend_date | BIGINT | 상장일 / 배당락일 (unix timestamp) |
| expense_ratio / dividend_yield | FLOAT | 운용비용 / 배당수익률 (%) |
| return_1m, return_1y, return_3y, return_3y_avg, return_5y, return_5y_avg | FLOAT | 수익률 (%) |
| data_updated_at | DATETIME | 데이터 업데이트 시각 (UTC 저장, 한국시간 표시) |
| created_at | DATETIME | 생성 시각 |

## 문제 해결

- **프로덕션 API 오류 / 동기화 실패** → [DEPLOYMENT.md](./DEPLOYMENT.md)의 문제 해결 섹션 참고
- **로컬 스키마 변경 후**: `npm run db:reset` 후 서버 재시작
- **정렬이 작동하지 않음**: `EtfTable.tsx`에서 `table.getRowModel()`을 사용하는지 확인

## 라이선스

MIT

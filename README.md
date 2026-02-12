# ETF Master

미국 상장 ETF(~4,400개 이상)를 실시간으로 조회하고 분석할 수 있는 풀스택 웹 애플리케이션입니다.

## 주요 기능

- **실시간 ETF 데이터**: 4,400개 이상의 미국 상장 ETF 정보 제공
- **정렬 및 검색**: 모든 컬럼에 대한 정렬 및 실시간 검색 기능
- **성능 최적화**: 가상 스크롤링으로 수천 개의 데이터를 부드럽게 표시
- **자동 동기화**: 매일 오전 6시 자동 데이터 업데이트
- **상세 정보**: 각 ETF의 가격, 수익률, 배당률, 운용비용, 자산규모(AUM) 등 제공

## 기술 스택

### Backend
- **Python FastAPI** - 고성능 비동기 웹 프레임워크
- **SQLAlchemy** - ORM (Object-Relational Mapping)
- **SQLite** - 경량 데이터베이스
- **APScheduler** - 주기적 작업 스케줄러
- **yfinance** - Yahoo Finance API 래퍼

### Frontend
- **Next.js 16** - App Router 기반 React 프레임워크
- **TypeScript** - 타입 안정성
- **Tailwind CSS** - 유틸리티 우선 CSS 프레임워크
- **TanStack Table** - 테이블 정렬 및 필터링
- **TanStack Virtual** - 가상 스크롤링
- **TanStack React Query** - 서버 상태 관리

## 빠른 시작

### 사전 요구사항

- Python 3.9 이상
- Node.js 18 이상
- npm 또는 yarn

### 설치 및 실행

1. **프로젝트 클론**
```bash
git clone <repository-url>
cd etfmaster
```

2. **루트 의존성 설치**
```bash
npm install
```

3. **백엔드 의존성 설치**
```bash
cd backend
pip install fastapi uvicorn sqlalchemy pydantic yfinance apscheduler httpx pandas
cd ..
```

4. **프론트엔드 의존성 설치**
```bash
cd frontend
npm install
cd ..
```

5. **애플리케이션 실행 (백엔드 + 프론트엔드 동시 실행)**
```bash
npm run dev
```

백엔드는 `http://localhost:8000`에서, 프론트엔드는 `http://localhost:3000`에서 실행됩니다.

### 개별 실행

**백엔드만 실행**
```bash
npm run dev:backend
# 또는
cd backend
uvicorn app.main:app --reload --port 8000
```

**프론트엔드만 실행**
```bash
npm run dev:frontend
# 또는
cd frontend
npm run dev
```

## 데이터 동기화

### 자동 동기화
- **초기 동기화**: 서버 시작 시 데이터베이스에 ETF가 10개 미만이면 자동으로 전체 동기화 실행
- **일일 동기화**: 매일 오전 6시에 전체 동기화

### 수동 동기화
```bash
# 백엔드가 실행 중일 때
npm run sync
# 또는
curl -X POST http://localhost:8000/api/admin/sync
```

**참고**: 초기 전체 동기화는 약 7-10분 정도 소요됩니다 (4,400개 ETF).

## 데이터베이스 관리

### 데이터베이스 삭제
```bash
npm run db:delete
```

### 데이터베이스 리셋 (삭제 후 재생성)
```bash
npm run db:reset
# 이후 서버 재시작 (npm run dev)
```

데이터베이스 스키마가 변경되었거나 데이터를 완전히 새로 받고 싶을 때 사용합니다.

## API 문서

백엔드 실행 후 Swagger UI를 통해 API 문서를 확인할 수 있습니다:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 주요 엔드포인트

- `GET /api/etfs` - ETF 목록 조회 (필터링/페이지네이션 지원)
- `GET /api/etfs/{ticker}` - 특정 ETF 상세 정보
- `GET /api/etfs/filters` - 사용 가능한 카테고리/발행사 목록
- `POST /api/admin/sync` - 수동 데이터 동기화 트리거

## 프로젝트 구조

```
etfmaster/
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py         # 애플리케이션 진입점
│   │   ├── config.py       # 설정 (배치 크기, 동기화 시간 등)
│   │   ├── database.py     # 데이터베이스 연결 설정
│   │   ├── models/         # SQLAlchemy 모델
│   │   │   └── etf.py      # ETF 모델 (17개 필드)
│   │   ├── schemas/        # Pydantic 스키마
│   │   │   └── etf.py      # ETF 요청/응답 스키마
│   │   ├── routers/        # API 라우터
│   │   │   └── etfs.py     # ETF 엔드포인트
│   │   ├── services/       # 비즈니스 로직
│   │   │   ├── etf_list_provider.py    # ETF 티커 목록 가져오기
│   │   │   ├── etf_data_fetcher.py     # yfinance로 ETF 데이터 가져오기
│   │   │   └── etf_sync_service.py     # 배치 동기화 오케스트레이션
│   │   └── tasks/          # 백그라운드 작업
│   │       └── scheduler.py # APScheduler 설정
│   └── data/               # SQLite 데이터베이스 저장 위치
│
├── frontend/               # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx    # 메인 페이지
│   │   │   └── globals.css # 글로벌 스타일
│   │   ├── components/
│   │   │   ├── EtfDashboard.tsx        # 대시보드 루트 컴포넌트
│   │   │   ├── EtfTable.tsx            # 가상화된 테이블 컴포넌트
│   │   │   ├── EtfTableColumns.tsx     # 컬럼 정의 (16개 컬럼)
│   │   │   └── Tooltip.tsx             # ETF 설명 툴팁
│   │   ├── hooks/
│   │   │   └── useEtfData.ts           # React Query 훅
│   │   └── lib/
│   │       ├── api.ts      # API 클라이언트 함수
│   │       └── formatters.ts # 숫자/날짜 포맷터
│   └── package.json
│
├── package.json            # 루트 스크립트
├── CLAUDE.md              # AI 개발 가이드
└── README.md              # 이 파일
```

## 데이터 흐름

1. **ETF 목록 수집** (서버 시작 시, DB가 비어있을 때)
   - NASDAQ API에서 ~4,433개 활성 ETF 목록 가져오기
   - 실패 시 Alpha Vantage API로 폴백

2. **데이터 동기화** (`etf_sync_service.py`)
   - 100개씩 배치 처리, 배치 간 1초 지연 (API 레이트 리밋 준수)
   - 각 티커마다 yfinance로 데이터 가져오기:
     - 가격, 거래량, 자산규모(AUM)
     - 운용비용, 배당수익률
     - 설명(description)
   - 과거 가격으로 수익률 계산 (1개월, 1년, 3년, 5년)
   - ETF가 아닌 종목 필터링 (`quoteType == "ETF"`)
   - SQLite에 upsert (업데이트 또는 삽입)

3. **주기적 업데이트** (APScheduler)
   - 매일 오전 6시: 전체 동기화

4. **프론트엔드 데이터 흐름**
   - React Query로 전체 ETF 데이터 한 번에 로드 (`per_page=0`)
   - TanStack Table로 클라이언트 측 필터링/정렬 (네트워크 요청 없음)
   - TanStack Virtual로 가상 스크롤링 (~40개 행만 렌더링)
   - 5분마다 자동 새로고침

## 데이터베이스 스키마

**테이블: `etfs`**

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| ticker | VARCHAR(16) | 티커 심볼 (기본키) |
| name | VARCHAR | ETF 이름 |
| description | TEXT | 상세 설명 |
| exchange | VARCHAR | 거래소 (NASDAQ, NYSE 등) |
| issuer | VARCHAR | 발행사 |
| category | VARCHAR | 카테고리 |
| price | FLOAT | 현재 가격 |
| volume | BIGINT | 거래량 |
| market_cap | BIGINT | 자산규모 (AUM) |
| expense_ratio | FLOAT | 운용비용 (%) |
| dividend_yield | FLOAT | 배당수익률 (%) |
| return_1m | FLOAT | 1개월 수익률 (%) |
| return_1y | FLOAT | 1년 수익률 (%) |
| return_3y_avg | FLOAT | 3년 평균 수익률 (%) |
| return_5y | FLOAT | 5년 수익률 (%) |
| return_5y_avg | FLOAT | 5년 평균 수익률 (%) |
| data_updated_at | DATETIME | 데이터 업데이트 시각 |
| created_at | DATETIME | 생성 시각 |

## 주요 설정

설정은 `backend/app/config.py`에서 변경할 수 있습니다:

```python
BATCH_SIZE = 100                    # 배치당 티커 수
BATCH_DELAY_SECONDS = 1             # 배치 간 지연 시간 (초)
SYNC_HOUR = 6                       # 일일 동기화 시각 (시)
SYNC_MINUTE = 0                     # 일일 동기화 시각 (분)
```

## 프론트엔드 주요 기능

### 정렬
- 모든 컬럼 클릭으로 정렬 가능
- 오름차순/내림차순 토글
- 클라이언트 측 정렬로 즉시 반영

### 검색
- 실시간 검색 (티커, 이름에 대해)
- 대소문자 구분 없음

### 가상 스크롤링
- 4,400개 ETF를 부드럽게 스크롤
- 화면에 보이는 ~40개 행만 렌더링
- 메모리 효율적

### 상세 정보
- ETF 이름에 마우스 호버 시 설명 툴팁 표시
- 티커 클릭 시 Yahoo Finance 페이지로 이동
- 한국 시간대(Asia/Seoul)로 날짜/시간 표시

## 문제 해결

### 데이터베이스 스키마 변경
```bash
npm run db:reset
npm run dev
```

### 동기화가 너무 오래 걸림
초기 전체 동기화는 7-10분 정도 소요됩니다. 이는 정상입니다.
- 4,433 ETF ÷ 100 (배치 크기) = ~45 배치
- 각 배치 ~10초 소요

### ETF 개수가 너무 적게 표시됨
API 요청 실패일 수 있습니다. 백엔드 로그를 확인하세요:
```bash
# "Fetched X ETF tickers from NASDAQ" 메시지 확인
```

### 정렬이 작동하지 않음
`EtfTable.tsx`에서 `table.getRowModel()`을 사용하고 있는지 확인하세요.

## 개발 팁

- 백엔드 로그: 터미널에서 FastAPI 서버 로그 확인
- 프론트엔드 로그: 브라우저 개발자 도구 콘솔 확인
- API 테스트: http://localhost:8000/docs 에서 Swagger UI 사용
- 데이터베이스 확인: SQLite 클라이언트로 `backend/data/etfmaster.db` 열기

## 라이선스

MIT

## 기여

이슈 및 풀 리퀘스트를 환영합니다.

# 무료 배포 가이드 (Vercel + Neon + GitHub Actions)

Railway 없이 완전 무료로 운영하는 구성입니다. 별도 백엔드 서버가 없으므로 슬립/콜드스타트 문제도 없습니다.

| 역할 | 서비스 | 비용 |
|---|---|---|
| 프론트엔드 + 읽기 API | Vercel (Next.js `/api` 라우트) | 무료 |
| 데이터베이스 | Neon PostgreSQL | 무료 (0.5GB) |
| 데이터 동기화 | GitHub Actions (`etf-sync.yml`, 매일 06:00 KST) | 무료 |

기존 `backend/` FastAPI는 **로컬 개발용으로만** 유지됩니다. (동기화 스크립트도 backend 모듈을 임포트하므로 삭제하면 안 됩니다.)

---

## 1단계: Neon 데이터베이스 생성

1. [neon.tech](https://neon.tech) 가입 (GitHub 계정 연동 권장)
2. 새 프로젝트 생성
   - **Region: AWS Asia Pacific 1 (Singapore)** — 한국 사용자 기준 권장.
   - 대신 Vercel 함수 리전도 맞춰야 합니다: Vercel 대시보드 → Settings → Functions → **Function Region을 Singapore(sin1)로 변경**. (함수↔DB가 같은 리전이어야 쿼리 지연이 없습니다)
   - Postgres 버전은 기본값, Neon Auth는 OFF.
3. 대시보드 → **Connect** 에서 연결 문자열 2개를 확보:
   - **Direct** (호스트에 `-pooler`가 **없는** 것) → GitHub Actions용
   - **Pooled** (호스트에 `-pooler`가 **있는** 것) → Vercel용

   형태 예시:
   ```
   postgresql://user:pass@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   postgresql://user:pass@ep-xxxx-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
   > 연결 문자열에 `channel_binding=require`가 붙어 있고 연결 오류가 나면 해당 파라미터만 지워보세요.

## 2단계: GitHub 시크릿 교체 및 데이터 적재

1. GitHub 저장소 → Settings → Secrets and variables → Actions
2. `DATABASE_URL` 시크릿 값을 **Neon Direct 문자열**로 교체
3. Actions 탭 → **ETF Data Sync** → **Run workflow** 수동 실행
   - 첫 실행에서 `etfs` 테이블이 자동 생성되고 전체 데이터가 채워집니다.

## 3단계: Vercel 환경변수 설정

Vercel 프로젝트 → Settings → Environment Variables:

1. `DATABASE_URL` 추가 (Production, Preview 모두) — **Neon Pooled 문자열**
2. `NEXT_PUBLIC_API_URL` **삭제** — 남아 있으면 계속 Railway로 요청이 갑니다.
3. 코드를 푸시하거나 **Redeploy** 실행

## 4단계: 확인 후 Railway 정리

1. `https://<배포주소>/api/etfs/filters` 접속 → 카테고리/운용사 JSON이 나오면 성공
2. 대시보드에서 ETF 목록이 정상 표시되는지 확인
3. Railway 프로젝트 삭제 (DB 포함 — 데이터는 매일 동기화로 다시 채워지므로 백업 불필요)

---

## 로컬 개발

- **기존 방식 그대로 동작**: `npm run dev` → FastAPI(`localhost:8000`) + SQLite 사용 (개발 모드에선 프론트가 자동으로 8000 포트를 봅니다)
- Next.js API 라우트를 로컬에서 테스트하려면 `frontend/.env.local`에:
  ```bash
  NEXT_PUBLIC_API_URL=""
  DATABASE_URL="postgresql://...(Neon 연결 문자열)"
  ```

## 아키텍처 요약

```
GitHub Actions (매일 06:00 KST)
  └─ scripts/sync_and_push.py ──[yfinance 수집 후 upsert]──▶ Neon PostgreSQL
                                                                  ▲
Vercel (Next.js)                                                  │
  ├─ 프론트엔드 (기존과 동일)                                       │
  └─ /api/etfs, /api/etfs/filters, /api/etfs/[ticker] ──[읽기]────┘
```

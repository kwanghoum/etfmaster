# 배포 가이드 (Vercel + Neon + GitHub Actions)

ETF Master는 별도 백엔드 서버 없이 **완전 무료**로 운영됩니다.

| 역할 | 서비스 | 비용 |
|---|---|---|
| 프론트엔드 + 읽기 API | Vercel — Next.js `/api` 라우트 | 무료 |
| 데이터베이스 | Neon PostgreSQL (싱가포르 리전) | 무료 (0.5GB) |
| 데이터 동기화 | GitHub Actions (`etf-sync.yml`, 매일 06:00 KST) | 무료 |

- **프로덕션**: https://etfmaster.vercel.app
- 기존 `backend/` FastAPI는 **로컬 개발 전용**입니다. 동기화 스크립트가 backend 모듈을 임포트하므로 삭제하면 안 됩니다.

## 아키텍처

```
GitHub Actions (매일 06:00 KST, 수동 실행 가능)
  └─ scripts/sync_and_push.py ──[yfinance 수집 → upsert]──▶ Neon PostgreSQL
                                                                  ▲
Vercel (Next.js, 함수 리전 sin1 = frontend/vercel.json)           │
  ├─ 프론트엔드                                                    │
  └─ /api/etfs, /api/etfs/filters, /api/etfs/[ticker] ──[읽기]────┘
```

## 환경변수 / 시크릿

| 위치 | 이름 | 값 |
|---|---|---|
| GitHub → Settings → Secrets → Actions | `DATABASE_URL` | Neon **Direct** 연결 문자열 (`-pooler` 없음) |
| Vercel → Settings → Environment Variables | `DATABASE_URL` | Neon **Pooled** 연결 문자열 (`-pooler` 포함) |

연결 문자열 형태 (Neon 대시보드 → Connect):

```
postgresql://user:pass@ep-xxxx.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require          # Direct
postgresql://user:pass@ep-xxxx-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require   # Pooled
```

⚠️ 값은 반드시 `postgresql://`로 시작해야 합니다. `DATABASE_URL=` 접두어, 따옴표, `psql` 명령어가 섞여 들어가면 `getaddrinfo ENOTFOUND` 오류가 납니다.

## 일상 운영

### 코드 배포

`main`에 푸시하면 Vercel이 자동으로 빌드/배포합니다 (Root Directory: `frontend`).

```bash
git push origin main
```

- 함수 리전은 [frontend/vercel.json](frontend/vercel.json)의 `regions: ["sin1"]`로 고정되어 있습니다 (Neon과 같은 싱가포르).
- **환경변수를 변경한 경우** 자동 반영되지 않습니다 — Vercel 대시보드에서 Redeploy 필요.

### 데이터 동기화

- **자동**: 매일 06:00 KST (`.github/workflows/etf-sync.yml`)
- **수동**:
  ```bash
  gh workflow run etf-sync.yml
  gh run list --workflow=etf-sync.yml --limit 1   # 상태 확인
  ```
- 전체 동기화는 1~2시간 걸립니다 (yfinance 레이트 리밋 때문에 50개 배치 + 5초 지연).

### 롤백

Vercel 대시보드 → Deployments → 이전 배포 → "Promote to Production"

## 문제 해결

**API가 `{"detail":"Database query failed"}` 반환**
- Vercel의 `DATABASE_URL` 형식 확인 (위의 ⚠️ 참고). 수정 후 Redeploy 필수.
- `etfs` 테이블이 없는 경우 (새 DB): 동기화 워크플로우를 한 번 실행하면 자동 생성됩니다.
- Vercel 대시보드 → 프로젝트 → Logs에서 실제 에러 확인.

**동기화가 `SSL connection has been closed unexpectedly`로 실패**
- Neon이 유휴 연결을 끊어서 발생. `backend/app/database.py`의 `pool_pre_ping=True`로 해결되어 있습니다. 재발하면 해당 설정이 지워지지 않았는지 확인.

**동기화 워크플로우가 자동 실행되지 않음**
- GitHub은 저장소에 60일간 활동이 없으면 스케줄 워크플로우를 비활성화합니다.
- Actions 탭에서 활성화하거나: `gh workflow enable etf-sync.yml`

**Neon 무료 플랜 특성**
- 5분 미사용 시 DB가 잠들지만(scale to zero) 깨어나는 데 1초 미만 — 체감 거의 없음.
- 저장 용량 0.5GB — ETF 4,400행은 넉넉함.

## 로컬 개발

- `npm run dev` → 기존처럼 FastAPI(`localhost:8000`) + SQLite 사용. 프로덕션 DB를 건드리지 않습니다.
- Next.js API 라우트를 로컬에서 프로덕션 DB로 테스트하려면 `frontend/.env.local`:
  ```bash
  NEXT_PUBLIC_API_URL=""
  DATABASE_URL="postgresql://...(Neon 연결 문자열)"
  ```

## 처음부터 다시 설정할 때

1. [neon.tech](https://neon.tech) 프로젝트 생성 (리전: AWS Asia Pacific 1 Singapore, Neon Auth OFF)
2. GitHub 시크릿 `DATABASE_URL`에 Direct 문자열 등록 → `gh workflow run etf-sync.yml`로 데이터 적재
3. [vercel.com](https://vercel.com)에서 저장소 Import — Root Directory: `frontend`, 환경변수 `DATABASE_URL`에 Pooled 문자열 등록
4. 배포 후 `https://<도메인>/api/etfs/filters`가 JSON을 반환하면 완료

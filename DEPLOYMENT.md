# 배포 가이드 (Vercel + Railway)

이 문서는 ETF Master를 Vercel(프론트엔드)과 Railway(백엔드)에 배포하는 전체 과정을 설명합니다.

## 🚀 배포 개요

- **Frontend**: Vercel (Next.js)
- **Backend**: Railway (FastAPI + PostgreSQL)
- **데이터베이스**: Railway PostgreSQL

---

## 📋 사전 준비

### 1. GitHub 계정 및 저장소

- [ ] GitHub 계정 생성 (없는 경우)
- [ ] 이 프로젝트를 GitHub에 푸시

### 2. 외부 서비스 계정 생성

- [ ] [Railway](https://railway.app) 계정 생성 (GitHub 연동 권장)
- [ ] [Vercel](https://vercel.com) 계정 생성 (GitHub 연동 권장)

---

## 📦 1단계: GitHub 저장소 설정

### 1.1 .gitignore 설정 확인 (중요!)

GitHub에 푸시하기 전에 민감한 정보와 불필요한 파일이 제외되는지 확인해야 합니다.

**이미 `.gitignore` 파일이 프로젝트 루트에 생성되어 있습니다.**

확인할 주요 항목:

```bash
# .gitignore 파일 내용 확인
cat .gitignore
```

다음 항목들이 포함되어 있어야 합니다:

```gitignore
# Python
__pycache__/
*.py[cod]
venv/
*.egg-info/

# Database (중요! DB 파일은 GitHub에 올리지 않음)
*.db
*.sqlite
*.sqlite3
backend/data/

# Environment variables (중요! API 키 등 민감 정보)
.env
.env.local
.env.*.local

# Node
node_modules/

# IDE
.vscode/
.idea/

# OS
.DS_Store
```

**⚠️ 특히 중요한 항목:**
- `backend/data/` - SQLite 데이터베이스 파일 (수백 MB)
- `.env` - API 키 등 민감한 환경 변수
- `node_modules/` - NPM 패키지 (수백 MB)
- `__pycache__/` - Python 캐시 파일

### 1.2 .gitignore 적용 확인

```bash
cd /Users/kwanghoum/Dev/etfmaster

# Git 상태 확인
git status

# 다음 항목들이 "Untracked files"에 나타나면 안 됩니다:
# - backend/data/
# - node_modules/
# - __pycache__/
# - .env
# - *.db
```

만약 위 항목들이 표시된다면:

```bash
# Git 캐시 제거 후 다시 추가
git rm -r --cached .
git add .
```

### 1.3 Git 초기화 및 첫 커밋

```bash
# Git 초기화 (아직 안 했다면)
git init

# .gitignore 먼저 커밋
git add .gitignore
git commit -m "Add .gitignore"

# 나머지 파일 추가
git add .
git commit -m "Initial commit: ETF Master project"

# 커밋된 파일 목록 확인
git log --stat
```

**✅ 확인 사항:**
- `backend/data/` 폴더가 커밋되지 않았는지
- `node_modules/` 폴더가 커밋되지 않았는지
- `.env` 파일이 커밋되지 않았는지

### 1.4 GitHub에 저장소 생성

1. GitHub 웹사이트에서 로그인
2. 우측 상단 '+' → 'New repository' 클릭
3. Repository 이름: `etfmaster` (원하는 이름)
4. Public 또는 Private 선택
5. **"Add a README file" 체크 해제** (이미 프로젝트에 있음)
6. **"Add .gitignore" 선택 안 함** (이미 설정했음)
7. 'Create repository' 클릭

### 1.5 로컬 저장소와 연결

GitHub에서 표시된 명령어를 실행 (예시):

```bash
git remote add origin https://github.com/YOUR_USERNAME/etfmaster.git
git branch -M main
git push -u origin main
```

**푸시 중 에러 발생 시:**

```bash
# 파일이 너무 큰 경우 (100MB 이상)
# .gitignore가 제대로 적용되지 않은 것입니다
git rm -r --cached backend/data/
git rm -r --cached node_modules/
git commit -m "Remove large files"
git push -u origin main
```

### 1.6 GitHub에서 최종 확인

GitHub 저장소 페이지에서:

**✅ 포함되어야 할 파일:**
- `README.md`
- `DEPLOYMENT.md`
- `.gitignore`
- `backend/` (코드 파일만)
- `frontend/` (코드 파일만)
- `package.json`

**❌ 포함되면 안 되는 파일:**
- `backend/data/` (데이터베이스)
- `node_modules/` (Node 패키지)
- `frontend/node_modules/`
- `__pycache__/` (Python 캐시)
- `.env` (환경 변수)
- `*.db`, `*.sqlite` (데이터베이스 파일)

**저장소 크기 확인:**
- GitHub 저장소 크기가 **10MB 이하**여야 정상입니다
- 만약 수백 MB라면 .gitignore가 제대로 적용되지 않은 것입니다

---

## 🚂 2단계: Railway 백엔드 배포

### 2.1 Railway 프로젝트 생성

1. [Railway](https://railway.app) 로그인
2. 'New Project' 클릭
3. 'Deploy from GitHub repo' 선택
4. 저장소 권한 부여 후 `etfmaster` 선택
5. **중요**: 'Add variables' 화면에서 **아직 배포하지 말고** 다음 단계로

### 2.2 PostgreSQL 추가

1. Railway 프로젝트 대시보드에서
2. '+ New' 버튼 → 'Database' → 'Add PostgreSQL' 클릭
3. PostgreSQL 서비스가 자동으로 배포됨

### 2.3 백엔드 서비스 설정

1. 백엔드 서비스 카드 클릭
2. 'Settings' 탭으로 이동
3. **Root Directory** 설정:
   - 'Root Directory' 입력란에 `backend` 입력
   - 이렇게 하면 Railway가 backend 폴더를 루트로 인식

4. **환경 변수 설정**:
   - 'Variables' 탭 클릭
   - 다음 변수들을 추가:

   ```
   ALPHA_VANTAGE_API_KEY=demo
   ALLOWED_ORIGINS=http://localhost:3000
   ```

   **참고**: `DATABASE_URL`은 PostgreSQL 서비스와 자동 연결되어 생성됩니다.

5. **빌드 명령어 확인**:
   - Railway가 `requirements.txt`를 자동 감지하여 설치함
   - `Procfile`의 `web` 명령어가 자동 실행됨

### 2.4 배포 시작

1. 'Deploy' 버튼 클릭 (또는 자동 배포 대기)
2. 배포 로그를 확인하며 대기 (3-5분 소요)
3. 배포 완료 후 'Settings' → 'Networking'에서 **Public URL** 확인
   - 예: `https://etfmaster-production.up.railway.app`
   - 이 URL을 복사해두세요 (프론트엔드에서 사용)

### 2.5 백엔드 동작 확인

브라우저에서 접속:
```
https://your-backend.up.railway.app/docs
```

Swagger UI가 표시되면 성공!

### 2.6 초기 데이터 동기화

Swagger UI에서:
1. `POST /api/admin/sync` 엔드포인트 찾기
2. 'Try it out' → 'Execute' 클릭
3. 7-10분 대기 (4400개 ETF 동기화)

또는 curl 사용:
```bash
curl -X POST https://your-backend.up.railway.app/api/admin/sync
```

---

## ▲ 3단계: Vercel 프론트엔드 배포

### 3.1 Vercel 프로젝트 생성

1. [Vercel](https://vercel.com) 로그인
2. 'Add New' → 'Project' 클릭
3. GitHub에서 `etfmaster` 저장소 Import
4. **Framework Preset**: Next.js (자동 감지됨)

### 3.2 프로젝트 설정

**Root Directory 설정**:
- 'Root Directory' 옆 'Edit' 클릭
- `frontend` 입력
- 'Continue' 클릭

**환경 변수 설정**:
- 'Environment Variables' 섹션에서 추가:

```
Name: NEXT_PUBLIC_API_URL
Value: https://your-backend.up.railway.app
```

(Railway에서 복사한 백엔드 URL 사용)

### 3.3 배포 시작

1. 'Deploy' 버튼 클릭
2. 빌드 로그 확인 (2-3분 소요)
3. 배포 완료 후 Vercel이 제공하는 URL 확인
   - 예: `https://etfmaster-abc123.vercel.app`

### 3.4 프론트엔드 동작 확인

브라우저에서 Vercel URL 접속:
```
https://your-app.vercel.app
```

ETF 대시보드가 표시되면 성공!

---

## 🔄 4단계: CORS 설정 업데이트

프론트엔드 URL을 백엔드 CORS에 추가해야 합니다.

### 4.1 Railway에서 환경 변수 업데이트

1. Railway 프로젝트 → 백엔드 서비스 → 'Variables' 탭
2. `ALLOWED_ORIGINS` 변수 수정:

```
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

(Vercel URL을 추가, 쉼표로 구분)

3. 저장하면 자동으로 재배포됨

---

## ✅ 5단계: 최종 확인

### 5.1 프론트엔드 테스트

Vercel URL에서:
- [ ] ETF 목록이 표시되는지 확인
- [ ] 검색 기능 테스트
- [ ] 정렬 기능 테스트
- [ ] 티커 클릭 시 Yahoo Finance 링크 작동 확인

### 5.2 백엔드 테스트

Railway URL에서:
- [ ] `/docs` - Swagger UI 접근
- [ ] `GET /api/etfs` - ETF 목록 조회
- [ ] 데이터가 4000개 이상인지 확인

### 5.3 스케줄링 확인

Railway 대시보드:
- [ ] 'Logs' 탭에서 스케줄러 로그 확인
- [ ] "Scheduler started" 메시지 확인
- [ ] "Next run time" 로그 확인

---

## 🔧 6단계: 자동 배포 설정 (선택사항)

### GitHub Push 시 자동 배포

**Railway (이미 설정됨)**:
- GitHub에 push하면 자동으로 재배포됨
- `backend/` 폴더 변경 시에만 재배포

**Vercel (이미 설정됨)**:
- GitHub에 push하면 자동으로 재배포됨
- `frontend/` 폴더 변경 시에만 재배포

---

## 🐛 문제 해결

### 프론트엔드에서 "Failed to fetch" 에러

**원인**: CORS 설정 문제
**해결**:
1. Railway에서 `ALLOWED_ORIGINS` 확인
2. Vercel URL이 정확히 포함되어 있는지 확인
3. Railway 재배포

### 백엔드 배포 실패

**원인**: Python 버전 또는 의존성 문제
**해결**:
1. Railway 'Deployments' 탭에서 로그 확인
2. `requirements.txt` 버전 확인
3. `runtime.txt`에서 Python 버전 확인

### 데이터가 표시되지 않음

**원인**: 초기 동기화 미실행
**해결**:
```bash
curl -X POST https://your-backend.up.railway.app/api/admin/sync
```

### 스케줄러가 작동하지 않음

**원인**: Railway가 백그라운드 프로세스를 중지함
**해결**:
- Railway는 기본적으로 백그라운드 워커를 지원합니다
- Logs에서 "Scheduler started" 메시지 확인
- 문제 지속 시 Railway 지원팀 문의

---

## 💰 비용 정보

### Railway
- **무료 플랜**: $5 크레딧/월 (약 500 시간)
- ETF Master는 월 $5 이하로 운영 가능
- 초과 시 사용량 기반 과금

### Vercel
- **무료 플랜**: 100GB 대역폭/월
- 개인 프로젝트에는 충분
- 빌드 시간 무제한 (Hobby 플랜)

**총 예상 비용**: 무료 ~ $5/월

---

## 🔄 업데이트 및 유지보수

### 코드 업데이트

```bash
# 로컬에서 코드 수정
git add .
git commit -m "Update: 수정 내용"
git push

# Railway와 Vercel이 자동으로 재배포
```

### 데이터베이스 백업

Railway에서:
1. PostgreSQL 서비스 클릭
2. 'Data' 탭에서 데이터 확인
3. 백업이 필요하면 'Backups' 기능 사용 (Pro 플랜)

### 로그 모니터링

- **Railway**: 'Logs' 탭에서 실시간 로그 확인
- **Vercel**: 'Runtime Logs'에서 프론트엔드 에러 확인

---

## 📚 추가 리소스

- [Railway 문서](https://docs.railway.app)
- [Vercel 문서](https://vercel.com/docs)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
- [Next.js 배포 가이드](https://nextjs.org/docs/deployment)

---

## 🎉 완료!

축하합니다! ETF Master가 성공적으로 배포되었습니다.

- **Frontend**: https://your-app.vercel.app
- **Backend API**: https://your-backend.up.railway.app
- **API Docs**: https://your-backend.up.railway.app/docs

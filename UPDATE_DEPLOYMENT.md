# 배포 업데이트 가이드

이 문서는 ETF Master 프로젝트의 코드를 수정한 후 Vercel과 Railway에 배포하는 전체 워크플로우를 설명합니다.

---

## 📝 코드 수정 후 배포 워크플로우

### 1단계: 로컬에서 코드 수정 및 테스트

```bash
cd /Users/kwanghoum/Dev/etfmaster

# 코드 수정 (예: VSCode, 다른 에디터 사용)
# - backend/ 폴더의 Python 파일 수정
# - frontend/ 폴더의 TypeScript/React 파일 수정
```

**로컬 테스트 실행:**

```bash
# 프론트엔드 + 백엔드 동시 실행 (프로젝트 루트에서)
npm run dev

# 또는 개별 실행:
# 백엔드만 (backend 폴더에서)
cd backend
uvicorn app.main:app --reload

# 프론트엔드만 (frontend 폴더에서)
cd frontend
npm run dev
```

**테스트 확인:**
- http://localhost:3000 (프론트엔드)
- http://localhost:8000/docs (백엔드 API)

---

### 2단계: Git에 변경사항 커밋

#### 2.1 변경된 파일 확인

```bash
cd /Users/kwanghoum/Dev/etfmaster

# 어떤 파일이 변경되었는지 확인
git status

# 변경 내용 상세 확인
git diff
```

#### 2.2 파일을 Staging Area에 추가

**특정 파일만 추가:**
```bash
# 백엔드 파일 수정한 경우
git add backend/app/routers/etfs.py
git add backend/app/services/etf_sync_service.py

# 프론트엔드 파일 수정한 경우
git add frontend/components/EtfTable.tsx
git add frontend/app/page.tsx
```

**모든 변경사항 추가:**
```bash
# 모든 수정된 파일 한 번에 추가
git add .
```

**⚠️ 주의:** `.env` 파일이나 `backend/data/` 폴더는 `.gitignore`에 있어서 자동으로 제외됩니다.

#### 2.3 커밋 생성

```bash
# 커밋 메시지와 함께 커밋 생성
git commit -m "Update: 수정 내용을 간단히 설명"

# 예시:
git commit -m "Fix: ETF 검색 버그 수정"
git commit -m "Add: 새로운 필터 기능 추가"
git commit -m "Update: API 응답 속도 개선"
```

**좋은 커밋 메시지 작성법:**
- `Fix:` - 버그 수정
- `Add:` - 새 기능 추가
- `Update:` - 기존 기능 개선
- `Refactor:` - 코드 리팩토링
- `Docs:` - 문서 수정

---

### 3단계: GitHub에 Push

```bash
# main 브랜치에 푸시
git push origin main

# 처음 푸시하는 경우 (upstream 설정)
git push -u origin main
```

**Push 성공 확인:**
```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 8 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 324 bytes | 324.00 KiB/s, done.
Total 3 (delta 2), reused 0 (delta 0), pack-reused 0
To https://github.com/YOUR_USERNAME/etfmaster.git
   abc1234..def5678  main -> main
```

---

### 4단계: 자동 배포 대기

GitHub에 push하면 **자동으로 배포가 시작**됩니다!

#### 4.1 Vercel 배포 확인

**방법 1: Vercel 대시보드**
1. https://vercel.com 로그인
2. 프로젝트 클릭
3. **"Deployments"** 탭 확인
4. 최상단에 "Building..." 상태 표시
5. 2-3분 후 "Ready" 상태로 변경

**방법 2: GitHub 저장소**
1. GitHub 저장소 페이지
2. 커밋 옆에 ✅ 또는 🟡 아이콘 표시
3. 클릭하면 Vercel 빌드 로그 확인 가능

**배포 시간:** 약 2-3분 (프론트엔드 빌드)

#### 4.2 Railway 배포 확인

**방법 1: Railway 대시보드**
1. https://railway.app 로그인
2. 프로젝트 → 백엔드 서비스 클릭
3. **"Deployments"** 탭 확인
4. 최상단에 "Building..." 상태 표시
5. 3-5분 후 "Active" 상태로 변경

**방법 2: 로그 확인**
1. Railway 서비스 → **"Logs"** 탭
2. 실시간 로그에서 "Application startup complete" 확인

**배포 시간:** 약 3-5분 (백엔드 빌드 + 재시작)

---

### 5단계: 배포된 사이트 확인

#### 5.1 프론트엔드 확인

```bash
# 브라우저에서 Vercel URL 접속
https://your-app.vercel.app
```

**확인 사항:**
- [ ] 페이지가 정상적으로 로드되는지
- [ ] 수정한 기능이 제대로 작동하는지
- [ ] 브라우저 콘솔에 에러가 없는지 (F12 → Console)

#### 5.2 백엔드 확인

```bash
# 브라우저에서 Railway API 문서 접속
https://your-backend.up.railway.app/docs
```

**확인 사항:**
- [ ] Swagger UI가 정상적으로 표시되는지
- [ ] API 엔드포인트 테스트 (Try it out)
- [ ] 수정한 로직이 제대로 작동하는지

---

## 📊 전체 워크플로우 요약

```
1. 코드 수정
   ↓
2. 로컬 테스트 (npm run dev)
   ↓
3. git add . (변경사항 추가)
   ↓
4. git commit -m "메시지" (커밋 생성)
   ↓
5. git push origin main (GitHub에 푸시)
   ↓
6. [자동] Vercel + Railway 배포 시작
   ↓
7. 배포 완료 대기 (5분)
   ↓
8. 배포된 사이트 확인
```

---

## 🔄 배포 자동화 세부 사항

### Vercel 자동 배포
- **트리거:** `frontend/` 폴더 변경 시
- **감지 파일:**
  - `frontend/**/*.tsx`
  - `frontend/**/*.ts`
  - `frontend/**/*.css`
  - `frontend/package.json`
- **빌드 명령어:** `npm run build` (자동 실행)
- **배포 위치:** Root Directory가 `frontend`로 설정되어 있음

### Railway 자동 배포
- **트리거:** `backend/` 폴더 변경 시
- **감지 파일:**
  - `backend/**/*.py`
  - `backend/requirements.txt`
- **빌드 명령어:** `pip install -r requirements.txt` (자동 실행)
- **시작 명령어:** `Procfile`의 `web` 명령어 실행
- **배포 위치:** Root Directory가 `backend`로 설정되어 있음

---

## ⚡ 빠른 배포 팁

### 프론트엔드만 수정한 경우

```bash
# backend/ 파일은 건드리지 않음
git add frontend/
git commit -m "Update: 프론트엔드 UI 개선"
git push

# → Vercel만 재배포 (Railway는 변경 감지 안 함)
```

### 백엔드만 수정한 경우

```bash
# frontend/ 파일은 건드리지 않음
git add backend/
git commit -m "Fix: API 응답 속도 개선"
git push

# → Railway만 재배포 (Vercel은 변경 감지 안 함)
```

### 둘 다 수정한 경우

```bash
git add .
git commit -m "Update: 전체 기능 개선"
git push

# → Vercel + Railway 모두 재배포
```

---

## 🐛 배포 실패 시 대처법

### 1. Vercel 빌드 실패

**확인 방법:**
```bash
# Vercel 대시보드 → Deployments → 실패한 배포 클릭
# "Build Logs" 확인
```

**주요 원인:**
- TypeScript 타입 에러
- 패키지 설치 실패 (`package.json` 오류)
- Next.js 빌드 에러

**해결:**
```bash
# 로컬에서 빌드 테스트
cd frontend
npm run build

# 에러 수정 후 다시 푸시
git add .
git commit -m "Fix: 빌드 에러 수정"
git push
```

### 2. Railway 배포 실패

**확인 방법:**
```bash
# Railway 대시보드 → Deployments → 실패한 배포 클릭
# "Deploy Logs" 확인
```

**주요 원인:**
- Python 패키지 설치 실패 (`requirements.txt` 오류)
- 환경 변수 누락
- 코드 실행 에러

**해결:**
```bash
# 로컬에서 테스트
cd backend
uvicorn app.main:app --reload

# 에러 수정 후 다시 푸시
git add .
git commit -m "Fix: 백엔드 에러 수정"
git push
```

### 3. 환경 변수 변경 필요한 경우

**Vercel:**
1. Vercel 대시보드 → 프로젝트 → **"Settings"** 탭
2. **"Environment Variables"** 클릭
3. 변수 수정 후 **"Redeploy"** 버튼 클릭

**Railway:**
1. Railway 대시보드 → 백엔드 서비스 → **"Variables"** 탭
2. 변수 수정 (자동으로 재배포됨)

---

## 📋 체크리스트

코드 배포 전 확인사항:

- [ ] 로컬에서 테스트 완료 (`npm run dev`)
- [ ] `.gitignore`에 민감한 파일 제외되어 있는지 확인
- [ ] 커밋 메시지 명확하게 작성
- [ ] `git push` 전 `git status`로 커밋 내용 확인
- [ ] Push 후 Vercel/Railway 배포 로그 확인
- [ ] 배포 완료 후 실제 사이트에서 동작 확인

---

## 🚀 실전 예시

### 예시 1: 프론트엔드 UI 버그 수정

```bash
# 1. 파일 수정
# frontend/components/EtfTable.tsx 에서 버그 수정

# 2. 로컬 테스트
npm run dev
# localhost:3000에서 확인

# 3. Git 커밋
git add frontend/components/EtfTable.tsx
git commit -m "Fix: ETF 테이블 정렬 버그 수정"

# 4. GitHub 푸시
git push origin main

# 5. Vercel 배포 대기 (2-3분)
# 6. https://your-app.vercel.app 에서 확인
```

### 예시 2: 백엔드 API 개선

```bash
# 1. 파일 수정
# backend/app/routers/etfs.py 에서 API 로직 개선

# 2. 로컬 테스트
cd backend
uvicorn app.main:app --reload
# localhost:8000/docs에서 테스트

# 3. Git 커밋
cd ..
git add backend/app/routers/etfs.py
git commit -m "Update: ETF API 응답 속도 개선"

# 4. GitHub 푸시
git push origin main

# 5. Railway 배포 대기 (3-5분)
# 6. https://your-backend.up.railway.app/docs 에서 확인
```

### 예시 3: 전체 기능 추가

```bash
# 1. 파일 수정
# backend/app/routers/etfs.py - 새 API 엔드포인트 추가
# frontend/hooks/useEtfData.ts - 새 API 호출 함수 추가
# frontend/components/EtfDashboard.tsx - 새 UI 컴포넌트 추가

# 2. 로컬 테스트
npm run dev
# 프론트엔드 + 백엔드 모두 확인

# 3. Git 커밋
git add backend/ frontend/
git commit -m "Add: ETF 즐겨찾기 기능 추가"

# 4. GitHub 푸시
git push origin main

# 5. Vercel + Railway 모두 배포 대기 (5분)
# 6. 양쪽 모두 확인
```

---

## 💡 추가 팁

### Git 커밋 취소하기 (Push 전)

```bash
# 마지막 커밋 취소 (변경사항은 유지)
git reset --soft HEAD~1

# 마지막 커밋 취소 (변경사항도 삭제)
git reset --hard HEAD~1
```

### 특정 파일만 이전 버전으로 되돌리기

```bash
# 특정 파일을 마지막 커밋 상태로 복원
git checkout HEAD -- frontend/components/EtfTable.tsx
```

### 배포 롤백하기

**Vercel:**
1. Vercel 대시보드 → Deployments
2. 이전 성공한 배포 찾기
3. "..." 메뉴 → "Promote to Production" 클릭

**Railway:**
1. Railway 대시보드 → Deployments
2. 이전 성공한 배포 찾기
3. "Redeploy" 버튼 클릭

---

## 📚 관련 문서

- [DEPLOYMENT.md](./DEPLOYMENT.md) - 초기 배포 가이드
- [README.md](./README.md) - 프로젝트 개요
- [CLAUDE.md](./CLAUDE.md) - 개발 가이드

---

## 🎉 완료!

이제 코드를 수정하고 `git push`만 하면 자동으로 배포됩니다!

궁금한 점이 있으면 언제든지 문의하세요.

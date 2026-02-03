<p align="center">
  <img src="https://img.shields.io/badge/Nexloop-AI-7c3aed?style=for-the-badge" alt="Nexloop AI" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776ab?style=for-the-badge&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/Next.js-16-000?style=for-the-badge&logo=next.js" alt="Next.js" />
  <img src="https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi" alt="FastAPI" />
</p>

# Nexloop AI

> **데이터 기반 마케팅 의사결정을 위한 AI 에이전트 시스템**  
> YouTube·네이버 데이터를 수집하고 **X-Algorithm Pipeline**으로 "팔리는 인사이트"를 추출한 뒤, 전략·썸네일·영상 대본까지 한 번에 제안합니다.

---

## 목차

- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [빠른 시작](#빠른-시작)
- [프로젝트 구조](#프로젝트-구조)
- [데이터 흐름](#데이터-흐름)
- [API 엔드포인트](#api-엔드포인트)
- [프론트엔드 라우트](#프론트엔드-라우트)
- [환경 변수](#환경-변수)
- [트러블슈팅](#트러블슈팅)

---

## 주요 기능

| 기능                     | 설명                                                                        |
| ------------------------ | --------------------------------------------------------------------------- |
| **X-Algorithm Pipeline** | Source → Hydration(Gemini) → Filter → Scorer → Selector로 Top 인사이트 추출 |
| **데이터 수집**          | YouTube 댓글, 네이버 리뷰 자동 수집 및 정규화                               |
| **AI 분석**              | 댓글 기본/심층 분석, CTR 예측, 마케팅 전략 생성                             |
| **SNS 콘텐츠**           | Instagram 캡션/해시태그, Twitter 포스트 자동 생성                           |
| **썸네일·영상**          | AI 썸네일 생성, Veo 영상 대본/프리셋                                        |
| **RAG 챗봇**             | Discovery Engine 기반 AI 챗봇 (비로그인 3회 무료)                           |
| **스케줄러**             | GCP Cloud Scheduler 연동, 파이프라인 자동 실행                              |
| **인증·관리**            | JWT 로그인/회원가입, 팀·역할, 감사 로그                                     |
| **Notion 연동**          | 분석 결과 Notion DB로 내보내기                                              |

---

## 기술 스택

| 영역         | 기술                                                          |
| ------------ | ------------------------------------------------------------- |
| **Backend**  | Python 3.10+, FastAPI, Pydantic, SQLAlchemy(async), aiosqlite |
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS                |
| **AI**       | Google Gemini, Vertex AI, Veo, Discovery Engine               |
| **외부 API** | YouTube API, Naver API, Notion API                            |
| **인프라**   | GCS, Cloud Run, Cloud Scheduler                               |
| **테스트**   | pytest, pytest-asyncio                                        |

---

## 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/HUNMINRYU/nexloop.git
cd nexloop
```

### 2. 백엔드 설정

```powershell
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env   # .env 편집 필요
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # .env 편집 필요
```

### 3. 프론트엔드 설정

```bash
cd frontend
npm install
cd ..
```

### 4. 실행

```powershell
# 터미널 1 - 백엔드
.\start_backend.ps1

# 터미널 2 - 프론트엔드
cd frontend && npm run dev
```

### 5. 확인

- 백엔드 API: http://localhost:8000/docs
- 프론트엔드: http://localhost:3000

---

## 프로젝트 구조

```
nexloop/
├── src/                    # 백엔드 (FastAPI)
│   ├── app.py              # 앱 진입점
│   ├── config/             # 설정 (settings, dependencies)
│   ├── core/               # 도메인 모델, 인터페이스, 프롬프트
│   ├── infrastructure/     # 외부 서비스 (Gemini, YouTube, Naver, GCS)
│   ├── services/           # 비즈니스 로직
│   │   ├── pipeline/       # X-Algorithm (orchestrator, stages)
│   │   ├── auth_service.py
│   │   ├── chatbot_service.py
│   │   ├── thumbnail_service.py
│   │   └── ...
│   └── utils/              # 유틸리티
├── frontend/               # Next.js
│   ├── src/app/            # 페이지 라우트
│   ├── src/components/     # 컴포넌트
│   ├── src/hooks/          # 커스텀 훅
│   └── src/lib/            # API, 유틸
├── tests/                  # pytest 테스트
├── alembic/                # DB 마이그레이션
├── pyproject.toml          # Python 의존성
├── Dockerfile              # 컨테이너 배포
└── README.md
```

---

## 데이터 흐름

```
사용자 입력 (제품명/YouTube URL)
        ↓
    데이터 수집 (YouTube 댓글, 네이버 리뷰)
        ↓
┌─────────────────────────────────────────┐
│         X-Algorithm Pipeline           │
│  Source → Filter → Hydration(LLM)      │
│  → Filter → Scorer → Selector          │
└─────────────────────────────────────────┘
        ↓
    출력 (인사이트 · 마케팅 전략 · 썸네일 · 영상)
```

---

## API 엔드포인트

| 메서드 | 경로                         | 설명            |
| ------ | ---------------------------- | --------------- |
| `GET`  | `/health`                    | 헬스 체크       |
| `POST` | `/run-pipeline`              | 파이프라인 실행 |
| `GET`  | `/pipeline-status/{task_id}` | 상태 조회       |
| `GET`  | `/pipeline-result/{task_id}` | 결과 조회       |
| `POST` | `/api/chat`                  | AI 챗봇         |
| `POST` | `/auth/signup`               | 회원가입        |
| `POST` | `/auth/login`                | 로그인          |
| `POST` | `/thumbnail/generate`        | 썸네일 생성     |
| `POST` | `/video/generate`            | 영상 대본 생성  |
| `GET`  | `/search/discovery`          | RAG 검색        |

> 전체 API: http://localhost:8000/docs (Swagger UI)

---

## 프론트엔드 라우트

| 경로                | 설명                 |
| ------------------- | -------------------- |
| `/`                 | 메인/랜딩            |
| `/login`            | 로그인               |
| `/signup`           | 회원가입             |
| `/pipeline/[slug]`  | 파이프라인 실행·결과 |
| `/analytics/[slug]` | 분석 대시보드        |
| `/insights`         | 인사이트 검색        |
| `/admin`            | 관리자 대시보드      |
| `/admin/scheduler`  | 스케줄러             |
| `/admin/audit-logs` | 감사 로그            |

---

## 환경 변수

`.env.example`을 복사하여 `.env`를 만들고 아래 값을 설정하세요.

### 필수

| 변수                      | 설명                     |
| ------------------------- | ------------------------ |
| `GOOGLE_CLOUD_PROJECT_ID` | GCP 프로젝트 ID          |
| `GOOGLE_API_KEY`          | Google API 키            |
| `NAVER_CLIENT_ID`         | 네이버 API 클라이언트 ID |
| `NAVER_CLIENT_SECRET`     | 네이버 API 시크릿        |

### 선택 (기본값 있음)

| 변수              | 기본값                               |
| ----------------- | ------------------------------------ |
| `DATABASE_URL`    | `sqlite+aiosqlite:///./data/auth.db` |
| `JWT_SECRET`      | `dev-secret`                         |
| `CORS_ORIGINS`    | `http://localhost:3000`              |
| `GCS_BUCKET_NAME` | (없음)                               |

---

## 트러블슈팅

| 증상                        | 해결                                                                     |
| --------------------------- | ------------------------------------------------------------------------ |
| `No module named pytest`    | `pip install -e ".[dev]"` 실행                                           |
| API 연결 실패               | `.env` 설정 확인, `CORS_ORIGINS`에 프론트 URL 추가                       |
| 프론트에서 백엔드 호출 실패 | `frontend/.env.local`에 `NEXT_PUBLIC_API_URL=http://localhost:8000` 설정 |
| GCP 인증 오류               | `GOOGLE_APPLICATION_CREDENTIALS` 경로 확인                               |

---

<p align="center">
  <strong>Nexloop AI</strong> — 데이터 기반 마케팅 인사이트를 한 곳에서.
</p>

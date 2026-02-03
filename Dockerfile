# Google Cloud Run용 Dockerfile
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim

# 시스템 의존성 설치 (필요 시)
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_ROOT_USER_ACTION=ignore
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 파일 복사 및 설치
COPY pyproject.toml .
COPY README.md .
RUN pip install --no-cache-dir .
RUN pip install --no-cache-dir fastapi uvicorn

# 소스 코드 복사
COPY . .
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

# PYTHONPATH 설정
ENV PYTHONPATH=/app/src

# 기본 실행 포트 (Cloud Run은 8080 권장)
EXPOSE 8080

# API 서버와 Streamlit을 동시에 띄우거나, 환경 변수에 따라 선택하도록 구성
# 여기서는 자동화 트리거를 위한 API 서버를 기본으로 실행하거나, 멀티 프로세스로 실행 가능
# 간편함을 위해 run_server.sh 같은 래퍼 스크립트를 사용할 수도 있습니다.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

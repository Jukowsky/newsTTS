# ── Stage 1: build frontend ──────────────────────────────────────────────────
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ── Stage 2: production image ─────────────────────────────────────────────────
FROM python:3.12-slim
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Backend source
COPY backend/ ./backend/

# Built frontend — FastAPI serves it as static files from ../frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Persistent data directory (mount your volume here, NOT on /app/backend)
RUN mkdir -p /app/data/audio_files /app/backend/logs

WORKDIR /app/backend
EXPOSE 8000

CMD gunicorn main:app \
    --chdir /app/backend \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 2 \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 300 \
    --access-logfile - \
    --error-logfile -

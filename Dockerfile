# FastAPI backend. Build context is the project root because the app reads the
# CMHC CSVs from data/processed at import time.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# psycopg2-binary ships prebuilt wheels, so no compiler toolchain is needed.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY data/processed ./data/processed

RUN useradd --create-home --uid 1001 rentscout
USER rentscout

EXPOSE 8000

# Shell form so $PORT expands — Railway (and most PaaS) inject the port at
# runtime; 8000 is only the local/compose default.
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}

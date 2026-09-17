FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/req.txt .

RUN pip install --no-cache-dir -r req.txt

COPY backend/ /app/backend/
COPY utils/ /app/utils/

RUN mkdir -p /app/documents /app/memory /app/logs

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Stage 1: Build
FROM python:3.10-slim AS builder

WORKDIR /install

COPY requirements.txt .

RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app.py .

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
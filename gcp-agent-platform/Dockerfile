FROM python:3.12-slim

# docling needs these; without them PDF parsing fails at runtime with an
# unhelpful error rather than at build time.
RUN apt-get update && apt-get install -y --no-install-recommends \
      libgl1 libglib2.0-0 poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app/src

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Cloud Run injects PORT. Do not hardcode 8080 in the app.
ENV PORT=8080
CMD exec uvicorn dia.api.main:app --host 0.0.0.0 --port ${PORT} --timeout-keep-alive 900

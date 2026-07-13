FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements-api.txt .

RUN pip install --default-timeout=1000 --retries 10 \
    --no-cache-dir -r requirements-api.txt

COPY api.py .
COPY config.py .
COPY feature_extraction.py .
COPY qr_decoder.py .
COPY url_analysis.py .
COPY model.pkl .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
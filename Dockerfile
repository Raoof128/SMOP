# Secure MLOps production image
FROM python:3.11-slim

# Create non-root user
RUN useradd -m appuser
WORKDIR /app

# Install system deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend backend
COPY models models
COPY docs docs
COPY frontend frontend
COPY sbom sbom
COPY logs logs
COPY examples examples

ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8000
EXPOSE 8000

USER appuser

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

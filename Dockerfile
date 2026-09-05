# ==============================================================================
# GCC Customer Support AI — Multi-Agent System Dockerfile
# Optimized for Railway & containerized production deployments
# ==============================================================================

FROM python:3.13-slim

# Set environment defaults
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    PORT=8000 \
    CHROMA_PERSIST_DIRECTORY=/app/chroma_db

WORKDIR /app

# Install system dependencies required by C extensions (psycopg, chromadb, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for optimal Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application assets, frontend, and backend code
COPY data/ ./data/
COPY frontend/ ./frontend/
COPY backend/ ./backend/

# Ensure ChromaDB vector store directory exists with write permissions
RUN mkdir -p /app/chroma_db

WORKDIR /app/backend

EXPOSE 8000

# Railway dynamically injects $PORT at runtime
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

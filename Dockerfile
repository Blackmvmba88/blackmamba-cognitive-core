FROM python:3.11-slim

LABEL maintainer="BlackMamba <blackmvmba88@example.com>"
LABEL description="BlackMamba Cognitive Core - Motor cognitivo modular para IA"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY blackmamba/ ./blackmamba/
COPY scripts/ ./scripts/

# Create data directory
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV COGNITIVE_API_HOST=0.0.0.0
ENV COGNITIVE_API_PORT=8000
ENV COGNITIVE_MEMORY_PATH=/app/data/memory.json

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "-m", "blackmamba.api.app"]

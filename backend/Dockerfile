FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (rebuild with timestamp to force redeploy)
# Build timestamp: 2026-03-15-argon2-v3
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (Railway will use PORT env variable)
EXPOSE 8000

# Run with verbose logging
# Railway sets PORT env variable, so we use it via shell expansion
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info"

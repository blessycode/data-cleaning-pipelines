# Multi-stage build for Data Cleaning Pipeline API
FROM python:3.12-slim as backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY api/requirements-api.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy API code
COPY api/ ./api/
COPY data_cleaning_pipeline/ ./data_cleaning_pipeline/

# Set working directory
WORKDIR /app/api

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && python init_db.py && uvicorn main:app --host 0.0.0.0 --port 8000"]


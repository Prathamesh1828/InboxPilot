# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies for psycopg2 and others
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Run the API server by default
# Shell form is used (instead of exec/JSON form) so that the $PORT
# environment variable provided by Railway is expanded at runtime.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

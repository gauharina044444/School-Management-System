FROM python:3.9-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directory for SQLite database and set permissions
RUN mkdir -p /data \
    && chmod 777 /data

# Set the environment variable for the database location
ENV DATABASE_URL=sqlite:////data/school_management.db

# Expose application port
EXPOSE 5002

# Default command for development
CMD ["python", "run.py"]
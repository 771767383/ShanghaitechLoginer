FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
# iputils-ping is required for ping command
# libgl1 and libglib2.0-0 are required for ddddocr/opencv
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Entrypoint
CMD ["python", "entrypoint.py"]

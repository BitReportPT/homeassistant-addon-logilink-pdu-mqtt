FROM python:3.11-alpine

# Install required packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY run.py .

# Create non-root user
RUN adduser -D -s /bin/sh app
USER app

# Run the application
CMD ["python", "run.py"]
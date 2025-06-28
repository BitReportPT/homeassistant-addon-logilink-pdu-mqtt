FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY run.py .
COPY pdu.py .
COPY discover_pdus.py .

# Create non-root user for security
RUN useradd -m -u 1000 pduuser && chown -R pduuser:pduuser /app
USER pduuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8123', timeout=5)" || exit 1

CMD ["python", "run.py"]
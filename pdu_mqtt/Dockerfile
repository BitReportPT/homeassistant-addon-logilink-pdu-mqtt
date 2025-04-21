FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir paho-mqtt requests

COPY run.py .
COPY pdu.py .

CMD ["python", "run.py"]
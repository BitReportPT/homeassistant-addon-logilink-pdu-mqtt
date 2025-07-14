ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN apk add --no-cache \
    python3 \
    py3-pip

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    requests \
    paho-mqtt

# Copy Python files
COPY run.py /
COPY pdu.py /
COPY discover_pdus.py /

# Set working directory
WORKDIR /

# Run Python directly
CMD ["python3", "-u", "run.py"]
ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN apk add --no-cache \
    python3 \
    py3-pip

# Set working directory
WORKDIR /

# Copy requirements first for better caching
COPY requirements.txt /
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy Python files
COPY run.py /
COPY pdu.py /
COPY discover_pdus.py /
COPY web_interface.py /
COPY device_detection.py /
COPY ha_theme_integration.py /
COPY bug_fixes.py /
COPY translations.json /

# Create templates directory and copy templates
RUN mkdir -p /templates
COPY templates/ /templates/

# Run Python directly
CMD ["python3", "-u", "run.py"]
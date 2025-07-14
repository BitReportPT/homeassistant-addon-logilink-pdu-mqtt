ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-requests \
    py3-paho-mqtt

# Python 3 HTTP library
RUN pip3 install --no-cache-dir requests paho-mqtt

# Copy data for add-on
COPY run.py /
COPY pdu.py /
COPY pdu_manager.py /
COPY mqtt_bridge.py /
COPY discover_pdus.py /

# Copy service files
COPY rootfs /

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="BitReport.pt" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.vendor="Home Assistant Add-ons" \
    org.opencontainers.image.authors="BitReport.pt" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt" \
    org.opencontainers.image.source="https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt" \
    org.opencontainers.image.documentation="https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt/blob/main/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}
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
COPY run.sh /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
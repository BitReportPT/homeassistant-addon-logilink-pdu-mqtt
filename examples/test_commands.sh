#!/bin/bash
# Test commands for LogiLink PDU MQTT control
# Only tests outlets 1 and 8 as requested

MQTT_HOST="192.168.1.241"
MQTT_USER="mqttuser"
MQTT_PASS="mqttpass"

echo "=== LogiLink PDU MQTT Test Commands ==="
echo "⚠️  Only testing outlets 1 and 8 for safety"
echo ""

# Function to run MQTT commands
mqtt_pub() {
    mosquitto_pub -h $MQTT_HOST -u $MQTT_USER -P $MQTT_PASS "$@"
}

mqtt_sub() {
    mosquitto_sub -h $MQTT_HOST -u $MQTT_USER -P $MQTT_PASS "$@"
}

# Test 1: Check current status
echo "1. Subscribing to outlet states (press Ctrl+C after 10 seconds)..."
timeout 10 mqtt_sub -t "pdu/rack_01/outlet+/state" -v

echo ""
echo "2. Testing Outlet 1 control..."
echo "   Turning OFF outlet 1..."
mqtt_pub -t "pdu/rack_01/outlet1/set" -m "OFF"
sleep 3

echo "   Turning ON outlet 1..."
mqtt_pub -t "pdu/rack_01/outlet1/set" -m "ON"
sleep 3

echo ""
echo "3. Testing Outlet 8 control..."
echo "   Turning OFF outlet 8..."
mqtt_pub -t "pdu/rack_01/outlet8/set" -m "OFF"
sleep 3

echo "   Turning ON outlet 8..."
mqtt_pub -t "pdu/rack_01/outlet8/set" -m "ON"
sleep 3

echo ""
echo "4. Reading sensor data..."
echo "   Temperature:"
timeout 2 mqtt_sub -t "pdu/rack_01/sensor/temperature" -C 1
echo "   Humidity:"
timeout 2 mqtt_sub -t "pdu/rack_01/sensor/humidity" -C 1
echo "   Current:"
timeout 2 mqtt_sub -t "pdu/rack_01/sensor/current" -C 1

echo ""
echo "5. Testing outlet configuration..."
echo "   Configuring outlet 1 name and delays..."
mqtt_pub -t "pdu/rack_01/outlet/1/config/set" -m '{"name": "Test Server", "delay_on": "5", "delay_off": "10"}'

echo ""
echo "6. Testing temperature thresholds..."
echo "   Setting temperature limits (15-30°C)..."
mqtt_pub -t "pdu/rack_01/threshold/temperature/set" -m '{"min": "15", "max": "30", "enabled": true}'

echo ""
echo "=== Test completed ==="
echo ""
echo "To monitor all PDU topics continuously, run:"
echo "mosquitto_sub -h $MQTT_HOST -u $MQTT_USER -P $MQTT_PASS -t 'pdu/rack_01/#' -v" 
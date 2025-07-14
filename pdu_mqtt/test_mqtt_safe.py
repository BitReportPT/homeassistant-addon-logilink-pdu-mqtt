#!/usr/bin/env python3
"""
Safe MQTT test script - only tests outlets 1 and 8
"""

import paho.mqtt.client as mqtt
import time
import json

# MQTT configuration
MQTT_HOST = "192.168.1.241"
MQTT_PORT = 1883
MQTT_USER = "mqttuser"
MQTT_PASS = "mqttpass"
PDU_NAME = "rack_01"

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to all status topics
    client.subscribe(f"pdu/{PDU_NAME}/outlet1/state")
    client.subscribe(f"pdu/{PDU_NAME}/outlet8/state")
    client.subscribe(f"pdu/{PDU_NAME}/sensor/+")
    client.subscribe(f"pdu/{PDU_NAME}/device/info")

def on_message(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")

def test_basic_control():
    """Test basic outlet control - only outlets 1 and 8"""
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_message = on_message
    
    print("Connecting to MQTT broker...")
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()
    
    time.sleep(2)  # Wait for connection
    
    print("\n=== Testing Outlet 1 ===")
    print("Turning outlet 1 OFF...")
    client.publish(f"pdu/{PDU_NAME}/outlet1/set", "OFF")
    time.sleep(3)
    
    print("Turning outlet 1 ON...")
    client.publish(f"pdu/{PDU_NAME}/outlet1/set", "ON")
    time.sleep(3)
    
    print("\n=== Testing Outlet 8 ===")
    print("Turning outlet 8 OFF...")
    client.publish(f"pdu/{PDU_NAME}/outlet8/set", "OFF")
    time.sleep(3)
    
    print("Turning outlet 8 ON...")
    client.publish(f"pdu/{PDU_NAME}/outlet8/set", "ON")
    time.sleep(3)
    
    print("\n=== Reading Sensor Data ===")
    time.sleep(5)  # Wait for sensor updates
    
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    test_basic_control() 
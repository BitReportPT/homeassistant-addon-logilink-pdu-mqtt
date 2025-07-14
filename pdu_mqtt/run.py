#!/usr/bin/env python3
"""
PDU MQTT Bridge - Simple version based on v1.1
"""

import time
import os
import json
import paho.mqtt.client as mqtt
import logging
import sys
from pdu import PDU

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load configuration from Home Assistant options
def load_config():
    """Load configuration from Home Assistant add-on options"""
    try:
        # Try to read from Home Assistant options file
        with open('/data/options.json', 'r') as f:
            options = json.load(f)
        logger.info("Loaded configuration from Home Assistant options")
        return options
    except FileNotFoundError:
        logger.warning("Options file not found, using environment variables")
        # Fallback to environment variables
        return {
            'mqtt_host': os.getenv('MQTT_HOST', 'localhost'),
            'mqtt_port': int(os.getenv('MQTT_PORT', 1883)),
            'mqtt_user': os.getenv('MQTT_USER', ''),
            'mqtt_password': os.getenv('MQTT_PASSWORD', ''),
            'mqtt_topic': os.getenv('MQTT_TOPIC', 'pdu'),
            'pdu_list': json.loads(os.getenv('PDU_LIST', '[]'))
        }
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return {}

# Load configuration
config = load_config()
mqtt_host = config.get('mqtt_host', 'localhost')
mqtt_port = config.get('mqtt_port', 1883)
mqtt_user = config.get('mqtt_user', '')
mqtt_password = config.get('mqtt_password', '')
mqtt_topic = config.get('mqtt_topic', 'pdu')
pdu_list = config.get('pdu_list', [])

# MQTT client setup
client = mqtt.Client()
if mqtt_user and mqtt_password:
    client.username_pw_set(mqtt_user, mqtt_password)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker")
        # Subscribe to control topics
        for pdu_config in pdu_list:
            pdu_name = pdu_config['name']
            for i in range(8):
                topic = f"{mqtt_topic}/{pdu_name}/outlet{i+1}/set"
                client.subscribe(topic)
                logger.info(f"Subscribed to {topic}")
    else:
        logger.error(f"Failed to connect to MQTT broker, return code {rc}")
        if rc == 5:
            logger.error("MQTT Error: Authentication failed - check username/password")
        elif rc == 1:
            logger.error("MQTT Error: Connection refused - incorrect protocol version")
        elif rc == 2:
            logger.error("MQTT Error: Connection refused - invalid client identifier")
        elif rc == 3:
            logger.error("MQTT Error: Connection refused - server unavailable")
        elif rc == 4:
            logger.error("MQTT Error: Connection refused - bad username or password")

def on_message(client, userdata, msg):
    try:
        topic_parts = msg.topic.split('/')
        if len(topic_parts) >= 4 and topic_parts[-1] == 'set':
            pdu_name = topic_parts[-3]
            outlet_str = topic_parts[-2]
            outlet_num = int(outlet_str.replace('outlet', ''))
            command = msg.payload.decode().lower()
            
            logger.info(f"Received command: {pdu_name} {outlet_str} -> {command}")
            
            # Find PDU config
            pdu_config = next((p for p in pdu_list if p['name'] == pdu_name), None)
            if pdu_config:
                pdu = PDU(pdu_config['host'], pdu_config['username'], pdu_config['password'])
                if command == 'on':
                    pdu.set_outlet(outlet_num, True)
                elif command == 'off':
                    pdu.set_outlet(outlet_num, False)
                    
    except Exception as e:
        logger.error(f"Error processing command: {e}")

def publish_status(pdu_name, pdu):
    """Publish PDU status to MQTT"""
    try:
        status = pdu.status()
        if status:
            # Publish outlet states
            for i in range(8):
                outlet = f"outlet{i+1}"
                state = status['outlets'][i] if i < len(status['outlets']) else 'off'
                client.publish(f"{mqtt_topic}/{pdu_name}/{outlet}", state, retain=True)
            
            # Publish sensor data
            if 'tempBan' in status and status['tempBan']:
                client.publish(f"{mqtt_topic}/{pdu_name}/temperature", status['tempBan'], retain=True)
            if 'humBan' in status and status['humBan']:
                client.publish(f"{mqtt_topic}/{pdu_name}/humidity", status['humBan'], retain=True)
            if 'curBan' in status and status['curBan']:
                client.publish(f"{mqtt_topic}/{pdu_name}/current", status['curBan'], retain=True)
                
    except Exception as e:
        logger.error(f"Error publishing status for {pdu_name}: {e}")

def main():
    logger.info("Starting PDU MQTT Bridge v1.1.1")
    logger.info(f"MQTT: {mqtt_host}:{mqtt_port}")
    logger.info(f"MQTT User: {mqtt_user if mqtt_user else 'None'}")
    logger.info(f"PDUs: {[p['name'] for p in pdu_list]}")
    
    if not pdu_list:
        logger.error("No PDUs configured! Please check your add-on configuration.")
        return
    
    # Set up MQTT callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Connect to MQTT broker
    try:
        logger.info(f"Connecting to MQTT broker at {mqtt_host}:{mqtt_port}")
        client.connect(mqtt_host, mqtt_port, 60)
        client.loop_start()
        
        # Main loop
        while True:
            for pdu_config in pdu_list:
                try:
                    pdu = PDU(pdu_config['host'], pdu_config['username'], pdu_config['password'])
                    publish_status(pdu_config['name'], pdu)
                except Exception as e:
                    logger.error(f"Error with PDU {pdu_config['name']}: {e}")
            
            time.sleep(30)  # Update every 30 seconds
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
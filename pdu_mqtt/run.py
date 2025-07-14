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
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Global variables
client = None
mqtt_topic = None
pdu_instances = {}  # Store PDU instances to avoid recreating them

# Load configuration from Home Assistant options
def load_config():
    """Load configuration from Home Assistant add-on options"""
    try:
        # Try to read from Home Assistant options file
        with open('/data/options.json', 'r') as f:
            options = json.load(f)
        logger.info("Loaded configuration from Home Assistant options")
        logger.info(f"Raw options: {json.dumps(options, indent=2)}")
        return options
    except FileNotFoundError:
        logger.warning("Home Assistant options file not found, using environment variables")
        # Fallback to environment variables
        return {
            'mqtt_host': os.getenv('MQTT_HOST', 'localhost'),
            'mqtt_port': int(os.getenv('MQTT_PORT', 1883)),
            'mqtt_user': os.getenv('MQTT_USER', ''),
            'mqtt_password': os.getenv('MQTT_PASSWORD', ''),
            'mqtt_topic': os.getenv('MQTT_TOPIC', 'pdu'),
            'pdu_list': json.loads(os.getenv('PDU_LIST', '[]'))
        }

def on_connect(client, userdata, flags, rc, properties=None):
    """MQTT connection callback (API v2)"""
    if rc == 0:
        logger.info("Connected to MQTT broker")
        # Subscribe to control topics
        for pdu_config in pdu_list:
            for i in range(8):
                topic = f"{mqtt_topic}/{pdu_config['name']}/outlet{i+1}/set"
                client.subscribe(topic)
                logger.info(f"Subscribed to {topic}")
    else:
        logger.error(f"Failed to connect to MQTT broker, return code {rc}")
        if rc == 1:
            logger.error("MQTT Error: Incorrect protocol version")
        elif rc == 2:
            logger.error("MQTT Error: Invalid client identifier")
        elif rc == 3:
            logger.error("MQTT Error: Server unavailable")
        elif rc == 4:
            logger.error("MQTT Error: Bad username or password")
        elif rc == 5:
            logger.error("MQTT Error: Authentication failed - check username/password")

def on_disconnect(client, userdata, rc, properties=None):
    """MQTT disconnection callback (API v2)"""
    logger.info(f"Disconnected from MQTT broker with result code {rc}")

def on_message(client, userdata, msg):
    """MQTT message callback"""
    try:
        topic = msg.topic
        payload = msg.payload.decode()
        logger.info(f"Received message: {topic} = {payload}")
        
        # Parse topic: pdu/{pdu_name}/outlet{X}/set
        parts = topic.split('/')
        if len(parts) >= 4 and parts[-1] == 'set':
            pdu_name = parts[1]
            outlet_str = parts[2]  # outlet1, outlet2, etc.
            
            if outlet_str.startswith('outlet'):
                outlet_num = int(outlet_str[6:])  # Extract number from 'outlet1'
                state = payload.lower() == 'on'
                
                # Find PDU instance
                if pdu_name in pdu_instances:
                    pdu = pdu_instances[pdu_name]
                    success = pdu.set_outlet(outlet_num, state)
                    if success:
                        # Publish state confirmation
                        state_topic = f"{mqtt_topic}/{pdu_name}/outlet{outlet_num}/state"
                        client.publish(state_topic, "ON" if state else "OFF", retain=True)
                        logger.info(f"Set {pdu_name} outlet {outlet_num} to {'ON' if state else 'OFF'}")
                    else:
                        logger.error(f"Failed to set {pdu_name} outlet {outlet_num}")
                else:
                    logger.error(f"PDU {pdu_name} not found")
    except Exception as e:
        logger.error(f"Error processing message {topic}: {e}")

def publish_status(pdu_name, pdu):
    """Publish status for all outlets of a PDU"""
    try:
        logger.debug(f"Publishing status for PDU: {pdu_name}")
        status = pdu.status()
        if status:
            # Check if we have outlets data
            if 'outlets' in status:
                for i, state in enumerate(status['outlets']):
                    outlet_num = i + 1
                    state_topic = f"{mqtt_topic}/{pdu_name}/outlet{outlet_num}/state"
                    mqtt_state = "ON" if state == 'on' else "OFF"
                    client.publish(state_topic, mqtt_state, retain=True)
                    logger.debug(f"Published {state_topic} = {mqtt_state}")
                
            # Publish sensor data if available
            if 'tempBan' in status and status['tempBan']:
                temp_topic = f"{mqtt_topic}/{pdu_name}/temperature"
                client.publish(temp_topic, status['tempBan'], retain=True)
                
            if 'humBan' in status and status['humBan']:
                hum_topic = f"{mqtt_topic}/{pdu_name}/humidity"
                client.publish(hum_topic, status['humBan'], retain=True)
                
            if 'curBan' in status and status['curBan']:
                cur_topic = f"{mqtt_topic}/{pdu_name}/current"
                client.publish(cur_topic, status['curBan'], retain=True)
                
            logger.info(f"Status published for PDU {pdu_name} - {len(status.get('outlets', []))} outlets")
        else:
            logger.warning(f"No status data received from PDU: {pdu_name}")
    except Exception as e:
        logger.error(f"Error publishing status for {pdu_name}: {e}")

def main():
    global client, mqtt_topic, pdu_list, pdu_instances
    
    # Load configuration
    config = load_config()
    
    mqtt_host = config['mqtt_host']
    mqtt_port = config['mqtt_port']
    mqtt_user = config['mqtt_user']
    mqtt_password = config['mqtt_password']
    mqtt_topic = config['mqtt_topic']
    pdu_list = config['pdu_list']
    
    # Log configuration (mask password)
    logger.info("Configuration loaded:")
    logger.info(f"  mqtt_host: {mqtt_host}")
    logger.info(f"  mqtt_port: {mqtt_port}")
    logger.info(f"  mqtt_user: {mqtt_user}")
    logger.info(f"  mqtt_password: {'********' if mqtt_password else 'None'}")
    logger.info(f"  mqtt_topic: {mqtt_topic}")
    logger.info(f"  pdu_list: {pdu_list}")
    logger.info(f"  pdu_list type: {type(pdu_list)}")
    logger.info(f"  pdu_list length: {len(pdu_list)}")
    
    # Create PDU instances once
    for pdu_config in pdu_list:
        pdu_name = pdu_config['name']
        pdu_instances[pdu_name] = PDU(pdu_config['host'], pdu_config['username'], pdu_config['password'])
        logger.info(f"Created PDU instance for {pdu_name}")
    
    logger.info(f"Starting PDU MQTT Bridge v1.1.5")
    logger.info(f"MQTT: {mqtt_host}:{mqtt_port}")
    logger.info(f"MQTT User: {mqtt_user if mqtt_user else 'None'}")
    logger.info(f"PDUs: {[pdu['name'] for pdu in pdu_list]}")
    
    # Create MQTT client with API v2
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    
    # Set credentials if provided
    if mqtt_user and mqtt_password:
        client.username_pw_set(mqtt_user, mqtt_password)
    
    # Set up MQTT callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # Connect to MQTT broker
    try:
        logger.info(f"Connecting to MQTT broker at {mqtt_host}:{mqtt_port}")
        client.connect(mqtt_host, mqtt_port, 60)
        client.loop_start()
        
        # Wait a bit for connection to establish
        time.sleep(2)
        
        # Main loop
        while True:
            for pdu_config in pdu_list:
                try:
                    pdu_name = pdu_config['name']
                    pdu = pdu_instances[pdu_name]
                    publish_status(pdu_name, pdu)
                except Exception as e:
                    logger.error(f"Error with PDU {pdu_config['name']}: {e}")
            
            time.sleep(30)  # Update every 30 seconds
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        if client:
            client.loop_stop()
            client.disconnect()

if __name__ == "__main__":
    main()
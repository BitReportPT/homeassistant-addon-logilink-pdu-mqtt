#!/usr/bin/env python3
"""
PDU MQTT Bridge - Complete version with all features
"""

import time
import os
import json
import paho.mqtt.client as mqtt
import logging
import sys
from pdu import PDU
from typing import Dict, Any

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
pdu_instances = {}

def load_config():
    """Load configuration from Home Assistant add-on options"""
    try:
        with open('/data/options.json', 'r') as f:
            options = json.load(f)
        logger.info("Loaded configuration from Home Assistant options")
        return options
    except FileNotFoundError:
        logger.warning("Home Assistant options file not found, using environment variables")
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
        
        # Subscribe to control topics for all PDUs
        for pdu_name in pdu_instances.keys():
            base = f"{mqtt_topic}/{pdu_name}"
            
            # Basic outlet control
            for i in range(1, 9):
                client.subscribe(f"{base}/outlet{i}/set")
                logger.info(f"Subscribed to {base}/outlet{i}/set")
            
            # Extended configuration topics
            client.subscribe(f"{base}/config/+/set")
            client.subscribe(f"{base}/network/set")
            client.subscribe(f"{base}/threshold/+/set")
            client.subscribe(f"{base}/outlet/+/config/set")
            client.subscribe(f"{base}/system/reboot")
            client.subscribe(f"{base}/snmp/set")
            client.subscribe(f"{base}/email/set")
            
            logger.info(f"Subscribed to all control topics for {pdu_name}")
        
        # Send MQTT Discovery messages
        send_discovery_messages()
    else:
        logger.error(f"Failed to connect to MQTT broker: {rc}")

def on_disconnect(client, userdata, rc, properties=None):
    """MQTT disconnection callback"""
    if rc != 0:
        logger.warning(f"Unexpected disconnect from MQTT broker: {rc}")

def on_message(client, userdata, msg):
    """Handle incoming MQTT messages"""
    try:
        topic_parts = msg.topic.split('/')
        if len(topic_parts) < 3:
            return
            
        pdu_name = topic_parts[1]
        if pdu_name not in pdu_instances:
            logger.error(f"Unknown PDU: {pdu_name}")
            return
            
        pdu = pdu_instances[pdu_name]
        payload = msg.payload.decode('utf-8')
        
        # Basic outlet control
        if topic_parts[2].startswith('outlet') and len(topic_parts) > 3 and topic_parts[3] == 'set':
            outlet_num = int(topic_parts[2].replace('outlet', ''))
            state = payload.upper() == 'ON'
            if pdu.set_outlet(outlet_num, state):
                logger.info(f"Set {pdu_name} outlet {outlet_num} to {payload}")
                client.publish(f"{mqtt_topic}/{pdu_name}/outlet{outlet_num}/state", 
                             payload.upper(), retain=True)
            else:
                logger.error(f"Failed to set {pdu_name} outlet {outlet_num}")
                
        # Extended features (for future implementation)
        elif topic_parts[2] == 'outlet' and len(topic_parts) > 4 and topic_parts[4] == 'config' and topic_parts[5] == 'set':
            outlet_num = int(topic_parts[3])
            logger.info(f"Outlet config request for {pdu_name} outlet {outlet_num}: {payload}")
            # TODO: Implement outlet configuration when PDU supports it
            
        elif topic_parts[2] == 'network' and topic_parts[3] == 'set':
            logger.info(f"Network config request for {pdu_name}: {payload}")
            # TODO: Implement network configuration when PDU supports it
            
        elif topic_parts[2] == 'threshold' and len(topic_parts) > 4 and topic_parts[4] == 'set':
            sensor_type = topic_parts[3]
            logger.info(f"Threshold config request for {pdu_name} {sensor_type}: {payload}")
            # TODO: Implement threshold configuration when PDU supports it
            
        elif topic_parts[2] == 'system' and topic_parts[3] == 'reboot':
            if payload.upper() == 'REBOOT':
                logger.warning(f"Reboot request for {pdu_name}")
                # TODO: Implement reboot when PDU supports it
                
    except Exception as e:
        logger.error(f"Error handling message on {msg.topic}: {e}")

def publish_status(pdu_name, pdu):
    """Publish status for all outlets of a PDU"""
    try:
        logger.debug(f"Publishing status for PDU: {pdu_name}")
        status = pdu.status()
        if status:
            # Publish outlet states
            if 'outlets' in status:
                for i, state in enumerate(status['outlets']):
                    outlet_num = i + 1
                    state_topic = f"{mqtt_topic}/{pdu_name}/outlet{outlet_num}/state"
                    mqtt_state = "ON" if state == 'on' else "OFF"
                    client.publish(state_topic, mqtt_state, retain=True)
                    logger.debug(f"Published {state_topic} = {mqtt_state}")
            # Publish sensor data
            if 'tempBan' in status and status['tempBan']:
                temp_topic = f"{mqtt_topic}/{pdu_name}/sensor/temperature"
                client.publish(temp_topic, status['tempBan'], retain=True)
            if 'humBan' in status and status['humBan']:
                hum_topic = f"{mqtt_topic}/{pdu_name}/sensor/humidity"
                client.publish(hum_topic, status['humBan'], retain=True)
            if 'curBan' in status and status['curBan']:
                cur_topic = f"{mqtt_topic}/{pdu_name}/sensor/current"
                client.publish(cur_topic, status['curBan'], retain=True)
            # Publish device info
            device_info = {
                "model": "LogiLink PDU8P01",
                "ip": pdu.host,
                "status": "online"
            }
            client.publish(f"{mqtt_topic}/{pdu_name}/device/info", 
                         json.dumps(device_info), retain=True)
            logger.info(f"Status published for PDU {pdu_name} - {len(status.get('outlets', []))} outlets")
        else:
            logger.warning(f"No status data received from PDU: {pdu_name}")
    except Exception as e:
        logger.error(f"Error publishing status for {pdu_name}: {e}")

def send_discovery_messages():
    """Send Home Assistant MQTT Discovery messages"""
    discovery_prefix = "homeassistant"
    
    for pdu_name in pdu_instances.keys():
        logger.info(f"Sending discovery messages for {pdu_name}")
        # Remove prefix 'pdu_' se existir
        clean_name = pdu_name
        if clean_name.startswith("pdu_"):
            clean_name = clean_name[4:]
        # Create discovery for each outlet switch
        for i in range(1, 9):
            entity_id = f"{clean_name}_outlet{i}"
            switch_config = {
                "name": f"Outlet {i}",
                "unique_id": entity_id,
                "object_id": entity_id,
                "command_topic": f"{mqtt_topic}/{pdu_name}/outlet{i}/set",
                "state_topic": f"{mqtt_topic}/{pdu_name}/outlet{i}/state",
                "payload_on": "ON",
                "payload_off": "OFF",
                "device_class": "outlet",
                "device": {
                    "identifiers": [f"pdu_{pdu_name}"],
                    "name": f"PDU {pdu_name}",
                    "model": "LogiLink PDU8P01",
                    "manufacturer": "LogiLink"
                }
            }
            discovery_topic = f"{discovery_prefix}/switch/{entity_id}/config"
            client.publish(discovery_topic, json.dumps(switch_config), retain=True)
            logger.debug(f"Published discovery for switch.{entity_id}")
        # Create discovery for sensors
        sensors = [
            ("temperature", "Temperature", "°C", "temperature"),
            ("humidity", "Humidity", "%", "humidity"),
            ("current", "Current", "A", "current")
        ]
        for sensor_id, name, unit, device_class in sensors:
            sensor_entity_id = f"{clean_name}_{sensor_id}"
            sensor_config = {
                "name": f"{name}",
                "unique_id": sensor_entity_id,
                "object_id": sensor_entity_id,
                "state_topic": f"{mqtt_topic}/{pdu_name}/sensor/{sensor_id}",
                "unit_of_measurement": unit,
                "device_class": device_class,
                "device": {
                    "identifiers": [f"pdu_{pdu_name}"],
                    "name": f"PDU {pdu_name}",
                    "model": "LogiLink PDU8P01",
                    "manufacturer": "LogiLink"
                }
            }
            discovery_topic = f"{discovery_prefix}/sensor/{sensor_entity_id}/config"
            client.publish(discovery_topic, json.dumps(sensor_config), retain=True)
            logger.debug(f"Published discovery for sensor.{sensor_entity_id}")
        # Additional entities for extended features
        # Text sensor for device info
        text_sensor_config = {
            "name": f"{clean_name} Device Info",
            "unique_id": f"{clean_name}_device_info",
            "state_topic": f"{mqtt_topic}/{pdu_name}/device/info",
            "device": {
                "identifiers": [f"pdu_{pdu_name}"],
                "name": f"PDU {pdu_name}",
                "model": "LogiLink PDU8P01",
                "manufacturer": "LogiLink"
            }
        }
        discovery_topic = f"{discovery_prefix}/sensor/{clean_name}_device_info/config"
        client.publish(discovery_topic, json.dumps(text_sensor_config), retain=True)
    logger.info("MQTT Discovery messages sent")

def main():
    global client, mqtt_topic, pdu_instances
    
    try:
        # Load configuration
        config = load_config()
        mqtt_host = config.get('mqtt_host', 'localhost')
        mqtt_port = config.get('mqtt_port', 1883)
        mqtt_user = config.get('mqtt_user', '')
        mqtt_password = config.get('mqtt_password', '')
        mqtt_topic = config.get('mqtt_topic', 'pdu')
        pdu_list = config.get('pdu_list', [])
        
        if not pdu_list:
            logger.error("No PDUs configured!")
            return
            
        # Create PDU instances
        for pdu_config in pdu_list:
            pdu_name = pdu_config['name']
            pdu_instances[pdu_name] = PDU(
                pdu_config['host'],
                pdu_config.get('username', 'admin'),
                pdu_config.get('password', 'admin')
            )
            logger.info(f"Created PDU instance for {pdu_name}")
        
        logger.info(f"Starting PDU MQTT Bridge v1.3.2")
        logger.info(f"MQTT: {mqtt_host}:{mqtt_port}")
        logger.info(f"PDUs: {list(pdu_instances.keys())}")
        
        # Setup MQTT client
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        
        if mqtt_user:
            client.username_pw_set(mqtt_user, mqtt_password)
            
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        
        # Connect to MQTT broker
        logger.info(f"Connecting to MQTT broker at {mqtt_host}:{mqtt_port}")
        client.connect(mqtt_host, mqtt_port, 60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(2)
        
        # Main loop
        while True:
            for pdu_name, pdu in pdu_instances.items():
                try:
                    publish_status(pdu_name, pdu)
                except Exception as e:
                    logger.error(f"Error updating {pdu_name}: {e}")
            
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
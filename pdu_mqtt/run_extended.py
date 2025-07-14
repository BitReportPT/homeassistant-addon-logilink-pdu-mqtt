#!/usr/bin/env python3
"""
PDU MQTT Bridge Extended - Full feature support
"""

import time
import os
import json
import paho.mqtt.client as mqtt
import logging
import sys
from pdu_extended import PDUExtended
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
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
    """MQTT connection callback"""
    if rc == 0:
        logger.info("Connected to MQTT broker")
        
        # Subscribe to all control topics
        for pdu_config in userdata['pdu_list']:
            pdu_name = pdu_config['name']
            base = f"{userdata['mqtt_topic']}/{pdu_name}"
            
            # Outlet control
            for i in range(1, 9):
                client.subscribe(f"{base}/outlet{i}/set")
                logger.info(f"Subscribed to {base}/outlet{i}/set")
            
            # Configuration topics
            client.subscribe(f"{base}/config/+/set")
            client.subscribe(f"{base}/network/set")
            client.subscribe(f"{base}/threshold/+/set")
            client.subscribe(f"{base}/outlet/+/config/set")
            client.subscribe(f"{base}/system/reboot")
            client.subscribe(f"{base}/snmp/set")
            client.subscribe(f"{base}/email/set")
            
            logger.info(f"Subscribed to all control topics for {pdu_name}")
    else:
        logger.error(f"Failed to connect to MQTT broker: {rc}")

def on_message(client, userdata, msg):
    """Handle incoming MQTT messages"""
    try:
        topic_parts = msg.topic.split('/')
        if len(topic_parts) < 4:
            return
            
        pdu_name = topic_parts[1]
        if pdu_name not in pdu_instances:
            logger.error(f"Unknown PDU: {pdu_name}")
            return
            
        pdu = pdu_instances[pdu_name]
        payload = msg.payload.decode('utf-8')
        
        # Handle different message types
        if topic_parts[2].startswith('outlet') and topic_parts[3] == 'set':
            # Outlet on/off control
            outlet_num = int(topic_parts[2].replace('outlet', ''))
            state = payload.upper() == 'ON'
            if pdu.set_outlet(outlet_num, state):
                logger.info(f"Set {pdu_name} outlet {outlet_num} to {payload}")
                # Publish confirmation
                client.publish(f"{userdata['mqtt_topic']}/{pdu_name}/outlet{outlet_num}/state", 
                             payload.upper(), retain=True)
            else:
                logger.error(f"Failed to set {pdu_name} outlet {outlet_num}")
                
        elif topic_parts[2] == 'outlet' and topic_parts[4] == 'config' and topic_parts[5] == 'set':
            # Outlet configuration
            outlet_num = int(topic_parts[3])
            try:
                config = json.loads(payload)
                if pdu.set_outlet_config(outlet_num, config):
                    logger.info(f"Updated config for {pdu_name} outlet {outlet_num}")
                    publish_outlet_config(client, userdata['mqtt_topic'], pdu_name, pdu)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in outlet config: {payload}")
                
        elif topic_parts[2] == 'network' and topic_parts[3] == 'set':
            # Network configuration
            try:
                config = json.loads(payload)
                if pdu.set_network_config(config):
                    logger.info(f"Updated network config for {pdu_name}")
                    publish_network_config(client, userdata['mqtt_topic'], pdu_name, pdu)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in network config: {payload}")
                
        elif topic_parts[2] == 'threshold' and topic_parts[4] == 'set':
            # Threshold configuration
            sensor_type = topic_parts[3]
            try:
                config = json.loads(payload)
                thresholds = {sensor_type: config}
                if pdu.set_thresholds(thresholds):
                    logger.info(f"Updated {sensor_type} thresholds for {pdu_name}")
                    publish_thresholds(client, userdata['mqtt_topic'], pdu_name, pdu)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in threshold config: {payload}")
                
        elif topic_parts[2] == 'system' and topic_parts[3] == 'reboot':
            # System reboot
            if payload.upper() == 'REBOOT':
                if pdu.reboot():
                    logger.info(f"Rebooting {pdu_name}")
                    client.publish(f"{userdata['mqtt_topic']}/{pdu_name}/system/status", 
                                 "REBOOTING", retain=False)
                else:
                    logger.error(f"Failed to reboot {pdu_name}")
                    
        elif topic_parts[2] == 'snmp' and topic_parts[3] == 'set':
            # SNMP configuration
            try:
                config = json.loads(payload)
                if pdu.set_snmp(config):
                    logger.info(f"Updated SNMP config for {pdu_name}")
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in SNMP config: {payload}")
                
        elif topic_parts[2] == 'email' and topic_parts[3] == 'set':
            # Email configuration
            try:
                config = json.loads(payload)
                if pdu.set_email_alerts(config):
                    logger.info(f"Updated email config for {pdu_name}")
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in email config: {payload}")
                
    except Exception as e:
        logger.error(f"Error handling message on {msg.topic}: {e}")

def publish_full_status(client, base_topic: str, pdu_name: str, pdu: PDUExtended):
    """Publish complete PDU status"""
    try:
        status = pdu.get_full_status()
        if not status:
            return
            
        base = f"{base_topic}/{pdu_name}"
        
        # Publish outlet states and info
        for outlet in status.get('outlets', []):
            outlet_num = outlet['number']
            outlet_base = f"{base}/outlet{outlet_num}"
            
            # State
            client.publish(f"{outlet_base}/state", 
                         "ON" if outlet['state'] == 'on' else "OFF", retain=True)
            
            # Name
            client.publish(f"{outlet_base}/name", outlet['name'], retain=True)
            
            # Delays
            client.publish(f"{outlet_base}/delay_on", outlet['delay_on'], retain=True)
            client.publish(f"{outlet_base}/delay_off", outlet['delay_off'], retain=True)
            
            # Power if available
            if 'power' in outlet:
                client.publish(f"{outlet_base}/power", outlet['power'], retain=True)
        
        # Publish sensor data
        sensors = status.get('sensors', {})
        if sensors.get('temperature', {}).get('value'):
            client.publish(f"{base}/sensor/temperature", 
                         sensors['temperature']['value'], retain=True)
            
        if sensors.get('humidity', {}).get('value'):
            client.publish(f"{base}/sensor/humidity", 
                         sensors['humidity']['value'], retain=True)
            
        if sensors.get('current', {}).get('value'):
            client.publish(f"{base}/sensor/current", 
                         sensors['current']['value'], retain=True)
        
        # Publish device info
        device = status.get('device', {})
        if device:
            client.publish(f"{base}/device/info", json.dumps(device), retain=True)
            
        logger.debug(f"Published full status for {pdu_name}")
        
    except Exception as e:
        logger.error(f"Error publishing full status for {pdu_name}: {e}")

def publish_network_config(client, base_topic: str, pdu_name: str, pdu: PDUExtended):
    """Publish network configuration"""
    try:
        config = pdu.get_network_config()
        if config:
            client.publish(f"{base_topic}/{pdu_name}/network/config", 
                         json.dumps(config), retain=True)
    except Exception as e:
        logger.error(f"Error publishing network config: {e}")

def publish_thresholds(client, base_topic: str, pdu_name: str, pdu: PDUExtended):
    """Publish threshold configuration"""
    try:
        thresholds = pdu.get_thresholds()
        if thresholds:
            base = f"{base_topic}/{pdu_name}/threshold"
            for sensor, config in thresholds.items():
                client.publish(f"{base}/{sensor}", json.dumps(config), retain=True)
    except Exception as e:
        logger.error(f"Error publishing thresholds: {e}")

def publish_outlet_config(client, base_topic: str, pdu_name: str, pdu: PDUExtended):
    """Publish outlet configurations"""
    try:
        status = pdu.get_full_status()
        if status:
            for outlet in status.get('outlets', []):
                outlet_num = outlet['number']
                config = {
                    'name': outlet['name'],
                    'delay_on': outlet['delay_on'],
                    'delay_off': outlet['delay_off']
                }
                client.publish(f"{base_topic}/{pdu_name}/outlet/{outlet_num}/config", 
                             json.dumps(config), retain=True)
    except Exception as e:
        logger.error(f"Error publishing outlet configs: {e}")

def publish_discovery(client, base_topic: str, pdu_name: str, pdu_config: Dict[str, Any]):
    """Publish Home Assistant MQTT discovery messages"""
    discovery_prefix = "homeassistant"
    
    # Discover outlets as switches
    for i in range(1, 9):
        outlet_config = {
            "name": f"{pdu_name} Outlet {i}",
            "unique_id": f"{pdu_name}_outlet{i}",
            "command_topic": f"{base_topic}/{pdu_name}/outlet{i}/set",
            "state_topic": f"{base_topic}/{pdu_name}/outlet{i}/state",
            "payload_on": "ON",
            "payload_off": "OFF",
            "device": {
                "identifiers": [f"pdu_{pdu_name}"],
                "name": f"PDU {pdu_name}",
                "model": "LogiLink PDU8P01",
                "manufacturer": "LogiLink"
            }
        }
        
        discovery_topic = f"{discovery_prefix}/switch/{pdu_name}_outlet{i}/config"
        client.publish(discovery_topic, json.dumps(outlet_config), retain=True)
    
    # Discover sensors
    sensors = [
        ("temperature", "Temperature", "°C", "temperature"),
        ("humidity", "Humidity", "%", "humidity"),
        ("current", "Current", "A", "current")
    ]
    
    for sensor_id, name, unit, device_class in sensors:
        sensor_config = {
            "name": f"{pdu_name} {name}",
            "unique_id": f"{pdu_name}_{sensor_id}",
            "state_topic": f"{base_topic}/{pdu_name}/sensor/{sensor_id}",
            "unit_of_measurement": unit,
            "device_class": device_class,
            "device": {
                "identifiers": [f"pdu_{pdu_name}"],
                "name": f"PDU {pdu_name}",
                "model": "LogiLink PDU8P01",
                "manufacturer": "LogiLink"
            }
        }
        
        discovery_topic = f"{discovery_prefix}/sensor/{pdu_name}_{sensor_id}/config"
        client.publish(discovery_topic, json.dumps(sensor_config), retain=True)
    
    logger.info(f"Published discovery messages for {pdu_name}")

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
        enable_discovery = config.get('enable_discovery', True)
        
        if not pdu_list:
            logger.error("No PDUs configured!")
            return
            
        # Create PDU instances
        for pdu_config in pdu_list:
            pdu_name = pdu_config['name']
            pdu_instances[pdu_name] = PDUExtended(
                pdu_config['host'],
                pdu_config.get('username', 'admin'),
                pdu_config.get('password', 'admin')
            )
            logger.info(f"Created PDU instance for {pdu_name}")
        
        logger.info(f"Starting PDU MQTT Bridge Extended v1.2.0")
        logger.info(f"MQTT: {mqtt_host}:{mqtt_port}")
        logger.info(f"PDUs: {list(pdu_instances.keys())}")
        
        # Setup MQTT client
        client = mqtt.Client(userdata={'mqtt_topic': mqtt_topic, 'pdu_list': pdu_list})
        
        if mqtt_user:
            client.username_pw_set(mqtt_user, mqtt_password)
            
        client.on_connect = on_connect
        client.on_message = on_message
        
        # Connect to MQTT broker
        logger.info(f"Connecting to MQTT broker at {mqtt_host}:{mqtt_port}")
        client.connect(mqtt_host, mqtt_port, 60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(2)
        
        # Publish discovery if enabled
        if enable_discovery:
            for pdu_config in pdu_list:
                publish_discovery(client, mqtt_topic, pdu_config['name'], pdu_config)
        
        # Main loop
        while True:
            for pdu_config in pdu_list:
                try:
                    pdu_name = pdu_config['name']
                    pdu = pdu_instances[pdu_name]
                    
                    # Publish full status
                    publish_full_status(client, mqtt_topic, pdu_name, pdu)
                    
                    # Publish configurations periodically
                    publish_network_config(client, mqtt_topic, pdu_name, pdu)
                    publish_thresholds(client, mqtt_topic, pdu_name, pdu)
                    publish_outlet_config(client, mqtt_topic, pdu_name, pdu)
                    
                except Exception as e:
                    logger.error(f"Error updating {pdu_config['name']}: {e}")
            
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
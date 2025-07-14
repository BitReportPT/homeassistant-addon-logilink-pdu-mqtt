#!/usr/bin/env python3
"""
PDU MQTT Bridge - Simplified version
"""

import time
import os
import json
import paho.mqtt.client as mqtt
import logging
import sys
import requests
import xml.etree.ElementTree as ET
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class SimplePDU:
    """Simple PDU class for LogiLink PDU8P01"""
    
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.base_url = f"http://{host}"
        self.session = requests.Session()
        self.session.auth = (username, password)
        logger.info(f"PDU initialized: {host}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get PDU status"""
        try:
            logger.debug(f"Getting status from {self.base_url}/status.xml")
            response = self.session.get(f"{self.base_url}/status.xml", timeout=10)
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            status = {"outlets": []}
            
            # Extract outlet information
            for outlet in root.findall(".//outlet"):
                outlet_id = outlet.get("id")
                state = outlet.find("state").text
                power = outlet.find("power").text if outlet.find("power") is not None else "0"
                
                status["outlets"].append({
                    "id": outlet_id,
                    "state": state,
                    "power": power
                })
            
            logger.debug(f"PDU status: {status}")
            return status
            
        except Exception as e:
            logger.error(f"Error getting PDU status: {e}")
            return {"outlets": []}
    
    def set_outlet(self, outlet_num: int, state: bool) -> bool:
        """Set outlet state"""
        try:
            action = "on" if state else "off"
            url = f"{self.base_url}/control.cgi"
            data = {
                "outlet": outlet_num,
                "action": action
            }
            
            logger.debug(f"Setting outlet {outlet_num} to {action}")
            response = self.session.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Set outlet {outlet_num} to {action}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting outlet {outlet_num}: {e}")
            return False

def load_config():
    """Load configuration from Home Assistant add-on options"""
    try:
        logger.info("Loading configuration from /data/options.json")
        with open('/data/options.json', 'r') as f:
            options = json.load(f)
        logger.info("Configuration loaded successfully")
        logger.info(f"Configuration: {json.dumps(options, indent=2)}")
        return options
    except FileNotFoundError:
        logger.error("Options file not found at /data/options.json")
        return {}
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return {}

def on_mqtt_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        logger.info("Connected to MQTT broker")
        # Subscribe to control topics for outlets 1 and 8 only
        client.subscribe("pdu/outlet_1/set")
        client.subscribe("pdu/outlet_8/set")
        logger.info("Subscribed to control topics")
    else:
        logger.error(f"Failed to connect to MQTT broker, return code {rc}")

def on_mqtt_message(client, userdata, msg):
    """MQTT message callback"""
    try:
        topic = msg.topic
        payload = msg.payload.decode().lower()
        
        logger.info(f"Received command: {topic} -> {payload}")
        
        # Parse outlet number from topic
        if topic == "pdu/outlet_1/set":
            outlet_num = 1
        elif topic == "pdu/outlet_8/set":
            outlet_num = 8
        else:
            logger.warning(f"Unknown topic: {topic}")
            return
        
        # Get PDU config
        config = load_config()
        pdu_list = config.get('pdu_list', [])
        
        if not pdu_list:
            logger.error("No PDU configured")
            return
        
        pdu_config = pdu_list[0]  # Use first PDU
        pdu = SimplePDU(pdu_config['host'], pdu_config['username'], pdu_config['password'])
        
        # Control outlet
        if payload in ['on', 'true', '1']:
            pdu.set_outlet(outlet_num, True)
        elif payload in ['off', 'false', '0']:
            pdu.set_outlet(outlet_num, False)
        else:
            logger.warning(f"Invalid payload: {payload}")
            
    except Exception as e:
        logger.error(f"Error processing command: {e}")

def publish_status(client, pdu: SimplePDU):
    """Publish PDU status to MQTT"""
    try:
        status = pdu.get_status()
        
        # Only publish outlets 1 and 8
        for outlet in status.get('outlets', []):
            outlet_id = int(outlet['id'])
            if outlet_id in [1, 8]:
                outlet_name = f"outlet_{outlet_id}"
                
                # Publish state
                state = "ON" if outlet['state'] == 'on' else "OFF"
                client.publish(f"pdu/{outlet_name}/state", state, retain=True)
                
                # Publish power
                power = outlet.get('power', '0')
                client.publish(f"pdu/{outlet_name}/power", power, retain=True)
                
                # Publish availability
                client.publish(f"pdu/{outlet_name}/available", "online", retain=True)
                
        logger.debug("Status published")
        
    except Exception as e:
        logger.error(f"Error publishing status: {e}")

def main():
    """Main function"""
    logger.info("Starting PDU MQTT Bridge - Simplified Version 1.2.1")
    
    # Load configuration
    config = load_config()
    
    mqtt_host = config.get('mqtt_host', 'localhost')
    mqtt_port = config.get('mqtt_port', 1883)
    mqtt_user = config.get('mqtt_user', '')
    mqtt_password = config.get('mqtt_password', '')
    pdu_list = config.get('pdu_list', [])
    
    logger.info(f"MQTT: {mqtt_host}:{mqtt_port}")
    logger.info(f"MQTT User: {mqtt_user if mqtt_user else 'None'}")
    logger.info(f"PDUs configured: {len(pdu_list)}")
    
    if not pdu_list:
        logger.error("No PDUs configured! Please check your add-on configuration.")
        return
    
    # Create MQTT client
    client = mqtt.Client()
    if mqtt_user and mqtt_password:
        client.username_pw_set(mqtt_user, mqtt_password)
    
    # Set up callbacks
    client.on_connect = on_mqtt_connect
    client.on_message = on_mqtt_message
    
    # Connect to MQTT
    try:
        logger.info(f"Connecting to MQTT broker...")
        client.connect(mqtt_host, mqtt_port, 60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(2)
        
        # Get PDU instance
        pdu_config = pdu_list[0]
        pdu = SimplePDU(pdu_config['host'], pdu_config['username'], pdu_config['password'])
        
        logger.info(f"Connected to PDU at {pdu_config['host']}")
        
        # Main loop
        while True:
            try:
                publish_status(client, pdu)
                time.sleep(30)  # Update every 30 seconds
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait longer on error
        
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("Shutting down...")

if __name__ == "__main__":
    main()
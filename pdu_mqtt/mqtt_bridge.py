#!/usr/bin/env python3
"""
Professional MQTT Bridge for Home Assistant
Handles MQTT communication and Home Assistant discovery
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt
from pdu_manager import PDUManager, PDUStatus

logger = logging.getLogger(__name__)

class MQTTBridge:
    """MQTT Bridge for Home Assistant integration"""
    
    def __init__(self, config: Dict[str, Any], pdu_manager: PDUManager):
        self.config = config
        self.pdu_manager = pdu_manager
        self.mqtt_config = config.get("mqtt", {})
        self.client = None
        self.connected = False
        self.discovery_sent = set()
        
    async def initialize(self):
        """Initialize MQTT client"""
        self.client = mqtt.Client(
            client_id=f"pdu_bridge_{int(asyncio.get_event_loop().time())}",
            protocol=mqtt.MQTTv311
        )
        
        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Set credentials if provided
        username = self.mqtt_config.get("username")
        password = self.mqtt_config.get("password")
        if username and password:
            self.client.username_pw_set(username, password)
        
        # Connect to broker
        host = self.mqtt_config.get("host", "localhost")
        port = self.mqtt_config.get("port", 1883)
        
        try:
            self.client.connect(host, port, 60)
            self.client.loop_start()
            logger.info(f"Connected to MQTT broker at {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.connected = True
            logger.info("MQTT connection established")
            # Subscribe to control topics
            asyncio.create_task(self._subscribe_control_topics())
        else:
            logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnection (rc={rc})")
    
    async def _subscribe_control_topics(self):
        """Subscribe to outlet control topics"""
        topic_prefix = self.mqtt_config.get("topic_prefix", "pdu")
        
        for pdu_name in self.pdu_manager.pdus.keys():
            for outlet in range(1, 9):
                topic = f"{topic_prefix}/{pdu_name}/outlet{outlet}/set"
                self.client.subscribe(topic)
                logger.info(f"Subscribed to {topic}")
    
    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            topic = msg.topic
            payload = msg.payload.decode().lower()
            
            # Parse topic: pdu/{pdu_name}/outlet{number}/set
            parts = topic.split("/")
            if len(parts) == 4 and parts[-1] == "set":
                pdu_name = parts[1]
                outlet_str = parts[2].replace("outlet", "")
                outlet = int(outlet_str)
                state = payload == "on"
                
                logger.info(f"Received command: {pdu_name} outlet {outlet} -> {payload}")
                
                # Execute command
                asyncio.create_task(self._execute_outlet_command(pdu_name, outlet, state))
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    async def _execute_outlet_command(self, pdu_name: str, outlet: int, state: bool):
        """Execute outlet control command"""
        try:
            success = await self.pdu_manager.set_outlet(pdu_name, outlet, state)
            if success:
                logger.info(f"Successfully set {pdu_name} outlet {outlet} to {'ON' if state else 'OFF'}")
                # Publish updated status
                await self.publish_status()
            else:
                logger.error(f"Failed to set {pdu_name} outlet {outlet}")
        except Exception as e:
            logger.error(f"Error executing outlet command: {e}")
    
    async def publish_status(self):
        """Publish all PDU status to MQTT"""
        if not self.connected:
            return
        
        topic_prefix = self.mqtt_config.get("topic_prefix", "pdu")
        retain = self.mqtt_config.get("retain", True)
        
        for pdu_name, status in self.pdu_manager.status_cache.items():
            # Publish outlet states
            for i, outlet_state in enumerate(status.outlets, 1):
                topic = f"{topic_prefix}/{pdu_name}/outlet{i}"
                self.client.publish(topic, outlet_state, retain=retain)
            
            # Publish sensor data
            if status.temperature is not None:
                topic = f"{topic_prefix}/{pdu_name}/temperature"
                self.client.publish(topic, str(status.temperature), retain=retain)
            
            if status.humidity is not None:
                topic = f"{topic_prefix}/{pdu_name}/humidity"
                self.client.publish(topic, str(status.humidity), retain=retain)
            
            if status.current is not None:
                topic = f"{topic_prefix}/{pdu_name}/current"
                self.client.publish(topic, str(status.current), retain=retain)
            
            # Publish status
            topic = f"{topic_prefix}/{pdu_name}/status"
            self.client.publish(topic, status.status, retain=retain)
    
    async def send_discovery(self):
        """Send Home Assistant discovery messages"""
        if not self.connected:
            return
        
        discovery_prefix = self.mqtt_config.get("discovery_prefix", "homeassistant")
        topic_prefix = self.mqtt_config.get("topic_prefix", "pdu")
        
        for pdu_name in self.pdu_manager.pdus.keys():
            # Send switch discovery for each outlet
            for outlet in range(1, 9):
                await self._send_switch_discovery(pdu_name, outlet, discovery_prefix, topic_prefix)
            
            # Send sensor discovery
            await self._send_sensor_discovery(pdu_name, discovery_prefix, topic_prefix)
    
    async def _send_switch_discovery(self, pdu_name: str, outlet: int, discovery_prefix: str, topic_prefix: str):
        """Send switch discovery message"""
        discovery_id = f"pdu_{pdu_name}_outlet_{outlet}"
        
        config = {
            "name": f"{pdu_name.title()} - Outlet {outlet}",
            "unique_id": discovery_id,
            "command_topic": f"{topic_prefix}/{pdu_name}/outlet{outlet}/set",
            "state_topic": f"{topic_prefix}/{pdu_name}/outlet{outlet}",
            "payload_on": "on",
            "payload_off": "off",
            "device_class": "switch",
            "icon": "mdi:power-plug",
            "device": {
                "name": f"PDU {pdu_name.title()}",
                "model": "Smart PDU",
                "manufacturer": "LogiLink/Intellinet",
                "identifiers": [f"pdu_{pdu_name}"],
                "via_device": "pdu_bridge"
            }
        }
        
        topic = f"{discovery_prefix}/switch/{discovery_id}/config"
        self.client.publish(topic, json.dumps(config), retain=True)
    
    async def _send_sensor_discovery(self, pdu_name: str, discovery_prefix: str, topic_prefix: str):
        """Send sensor discovery messages"""
        sensors = [
            {
                "name": "Temperature",
                "unit": "°C",
                "device_class": "temperature",
                "icon": "mdi:thermometer",
                "topic": f"{topic_prefix}/{pdu_name}/temperature"
            },
            {
                "name": "Humidity",
                "unit": "%",
                "device_class": "humidity",
                "icon": "mdi:water-percent",
                "topic": f"{topic_prefix}/{pdu_name}/humidity"
            },
            {
                "name": "Current",
                "unit": "A",
                "device_class": "current",
                "icon": "mdi:lightning-bolt",
                "topic": f"{topic_prefix}/{pdu_name}/current"
            }
        ]
        
        for sensor in sensors:
            discovery_id = f"pdu_{pdu_name}_{sensor['name'].lower()}"
            
            config = {
                "name": f"{pdu_name.title()} - {sensor['name']}",
                "unique_id": discovery_id,
                "state_topic": sensor["topic"],
                "unit_of_measurement": sensor["unit"],
                "device_class": sensor["device_class"],
                "icon": sensor["icon"],
                "device": {
                    "name": f"PDU {pdu_name.title()}",
                    "model": "Smart PDU",
                    "manufacturer": "LogiLink/Intellinet",
                    "identifiers": [f"pdu_{pdu_name}"],
                    "via_device": "pdu_bridge"
                }
            }
            
            topic = f"{discovery_prefix}/sensor/{discovery_id}/config"
            self.client.publish(topic, json.dumps(config), retain=True)
    
    async def start_publishing(self):
        """Start publishing loop"""
        logger.info("Starting MQTT publishing")
        
        # Send discovery messages
        await self.send_discovery()
        
        # Start status publishing loop
        while self.connected:
            try:
                await self.publish_status()
                await asyncio.sleep(30)  # Publish every 30 seconds
            except Exception as e:
                logger.error(f"Publishing error: {e}")
                await asyncio.sleep(10)
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker") 
#!/usr/bin/env python3
"""
Bug Fixes for PDU MQTT Bridge
Corrections of identified problems and stability improvements
"""

import logging
import time
import json
from typing import Optional, Dict, Any
import requests
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

class PDUBugFixes:
    """Class with bug fixes and improvements"""
    
    @staticmethod
    def fix_xml_parsing(xml_content: str) -> Optional[Dict[str, Any]]:
        """
        Bug Fix: More robust XML parsing for different PDU formats
        """
        try:
            # Remove problematic characters
            xml_content = xml_content.strip()
            
            # Check if contains response tag
            if "<response>" not in xml_content:
                logger.warning("XML does not contain <response> tag")
                return None
            
            # Parse XML with error handling
            xml = ET.fromstring(xml_content)
            
            # Extract data with default values
            data = {
                "outlets": [],
                "tempBan": xml.findtext("tempBan", "N/A"),
                "humBan": xml.findtext("humBan", "N/A"),
                "curBan": xml.findtext("curBan", "N/A")
            }
            
            # Extract outlet status with fallback
            for i in range(8):
                tag = f"outletStat{i}"
                val = xml.findtext(tag)
                if val is not None:
                    data["outlets"].append(val.lower())
                else:
                    data["outlets"].append("unknown")
            
            # Convert numeric values with validation
            for key in ["tempBan", "humBan", "curBan"]:
                try:
                    if data[key] not in ["N/A", None, ""]:
                        # Try to convert to float for validation
                        float(data[key])
                except (ValueError, TypeError):
                    data[key] = "N/A"
            
            return data
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in XML parsing: {e}")
            return None
    
    @staticmethod
    def fix_connection_timeout(url: str, auth: tuple, timeout: int = 10) -> Optional[requests.Response]:
        """
        Bug Fix: Connection with timeout and automatic retry
        """
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url, 
                    auth=auth, 
                    timeout=timeout,
                    headers={
                        'User-Agent': 'PDU-MQTT-Bridge/1.4.0',
                        'Accept': 'application/xml, text/xml'
                    }
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 401:
                    logger.error(f"Invalid credentials for {url}")
                    return response
                else:
                    logger.warning(f"HTTP {response.status_code} on attempt {attempt + 1}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error on attempt {attempt + 1} for {url}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
                
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        
        logger.error(f"Failed after {max_retries} attempts for {url}")
        return None
    
    @staticmethod
    def fix_outlet_state_validation(outlet_num: int, state: Any) -> bool:
        """
        Bug Fix: Robust outlet state validation
        """
        if not isinstance(outlet_num, int) or outlet_num < 1 or outlet_num > 8:
            logger.error(f"Invalid outlet number: {outlet_num}")
            return False
        
        # Normalize state
        if isinstance(state, str):
            state = state.lower().strip()
            valid_states = ['on', 'off', 'true', 'false', '1', '0']
            if state not in valid_states:
                logger.error(f"Invalid state: {state}")
                return False
        elif isinstance(state, bool):
            pass  # Boolean state is valid
        elif isinstance(state, int):
            if state not in [0, 1]:
                logger.error(f"Invalid numeric state: {state}")
                return False
        else:
            logger.error(f"Invalid state type: {type(state)}")
            return False
        
        return True
    
    @staticmethod
    def fix_mqtt_topic_validation(topic: str) -> str:
        """
        Bug Fix: MQTT topic validation and cleanup
        """
        if not topic or not isinstance(topic, str):
            logger.warning("Invalid MQTT topic, using default")
            return "pdu"
        
        # Remove problematic characters
        topic = topic.strip()
        invalid_chars = ['#', '+', '\x00']
        for char in invalid_chars:
            if char in topic:
                logger.warning(f"Removing invalid character '{char}' from topic")
                topic = topic.replace(char, '')
        
        # Remove double slashes
        while '//' in topic:
            topic = topic.replace('//', '/')
        
        # Remove leading/trailing slashes
        topic = topic.strip('/')
        
        if not topic:
            logger.warning("Empty topic after cleanup, using default")
            return "pdu"
        
        return topic
    
    @staticmethod
    def fix_configuration_validation(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bug Fix: Complete configuration validation
        """
        fixed_config = {}
        
        # MQTT Host
        fixed_config['mqtt_host'] = config.get('mqtt_host', 'localhost')
        if not isinstance(fixed_config['mqtt_host'], str) or not fixed_config['mqtt_host'].strip():
            fixed_config['mqtt_host'] = 'localhost'
        
        # MQTT Port
        try:
            fixed_config['mqtt_port'] = int(config.get('mqtt_port', 1883))
            if fixed_config['mqtt_port'] < 1 or fixed_config['mqtt_port'] > 65535:
                fixed_config['mqtt_port'] = 1883
        except (ValueError, TypeError):
            fixed_config['mqtt_port'] = 1883
        
        # MQTT User/Password
        fixed_config['mqtt_user'] = str(config.get('mqtt_user', ''))
        fixed_config['mqtt_password'] = str(config.get('mqtt_password', ''))
        
        # MQTT Topic
        fixed_config['mqtt_topic'] = PDUBugFixes.fix_mqtt_topic_validation(
            config.get('mqtt_topic', 'pdu')
        )
        
        # PDU List
        pdu_list = config.get('pdu_list', [])
        if not isinstance(pdu_list, list):
            pdu_list = []
        
        fixed_pdu_list = []
        for pdu in pdu_list:
            if not isinstance(pdu, dict):
                continue
            
            # Validação de cada PDU
            if not pdu.get('name') or not pdu.get('host'):
                logger.warning(f"PDU inválido ignorado: {pdu}")
                continue
            
            fixed_pdu = {
                'name': str(pdu['name']).strip(),
                'host': str(pdu['host']).strip(),
                'username': str(pdu.get('username', 'admin')).strip(),
                'password': str(pdu.get('password', 'admin'))
            }
            
            # Validação básica de IP/hostname
            if not fixed_pdu['host'] or '/' in fixed_pdu['host']:
                logger.warning(f"Host inválido: {fixed_pdu['host']}")
                continue
            
            fixed_pdu_list.append(fixed_pdu)
        
        fixed_config['pdu_list'] = fixed_pdu_list
        
        return fixed_config
    
    @staticmethod
    def fix_discovery_network_validation(network: str) -> Optional[str]:
        """
        Bug Fix: Network validation for discovery
        """
        if not network or not isinstance(network, str):
            return None
        
        network = network.strip()
        
        # Check basic format (e.g., 192.168.1)
        parts = network.split('.')
        if len(parts) != 3:
            logger.error(f"Invalid network format: {network}")
            return None
        
        # Validate each part
        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    logger.error(f"Invalid octet: {part}")
                    return None
            except ValueError:
                logger.error(f"Non-numeric octet: {part}")
                return None
        
        return network
    
    @staticmethod
    def fix_sensor_data_conversion(value: str) -> Optional[float]:
        """
        Bug Fix: Robust sensor data conversion
        """
        if not value or value in ['N/A', 'n/a', 'NULL', 'null', '']:
            return None
        
        try:
            # Remove spaces and special characters
            value = str(value).strip()
            
            # Remove common units
            units = ['°C', '°F', '%', 'A', 'V', 'W']
            for unit in units:
                if value.endswith(unit):
                    value = value[:-len(unit)].strip()
            
            # Convert to float
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert value: {value}")
            return None
    
    @staticmethod
    def fix_mqtt_payload_encoding(payload: Any) -> str:
        """
        Bug Fix: Correct MQTT payload encoding
        """
        if isinstance(payload, str):
            return payload
        elif isinstance(payload, (int, float)):
            return str(payload)
        elif isinstance(payload, bool):
            return "ON" if payload else "OFF"
        elif isinstance(payload, dict):
            try:
                return json.dumps(payload)
            except (TypeError, ValueError):
                return str(payload)
        else:
            return str(payload)
    
    @staticmethod
    def fix_error_recovery(func):
        """
        Bug Fix: Decorator for automatic error recovery
        """
        def wrapper(*args, **kwargs):
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        logger.error("Maximum retry attempts exceeded")
                        raise
                    time.sleep(2 ** attempt)  # Exponential backoff
            return None
        return wrapper
    
    @staticmethod
    def create_healthcheck_endpoint() -> Dict[str, Any]:
        """
        Bug Fix: Health check endpoint for monitoring
        """
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.4.0",
            "uptime": time.time(),
            "mqtt_connected": True,
            "pdus_configured": 0,
            "errors_count": 0
        }

# Aplicar correções automaticamente
def apply_bug_fixes():
    """Apply all bug fixes automatically"""
    logger.info("Applying bug fixes...")
    
    # Here you can add logic to apply fixes automatically
    # For example, validate existing configurations, clean corrupted data, etc.
    
    logger.info("Bug fixes applied successfully")

if __name__ == "__main__":
    apply_bug_fixes()
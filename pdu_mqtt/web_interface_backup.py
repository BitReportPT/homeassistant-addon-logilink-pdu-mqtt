#!/usr/bin/env python3
"""
Web Interface for PDU Discovery and Configuration
Modern visual interface for discovering PDUs on the network
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from xml.etree import ElementTree as ET
import logging
import re
from device_detection import DeviceDiscovery

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load translations
def load_translations():
    """Load translations from JSON file"""
    try:
        translations_path = os.path.join(os.path.dirname(__file__), 'translations.json')
        with open(translations_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading translations: {e}")
        return {"en": {}, "pt": {}}

TRANSLATIONS = load_translations()

def detect_language(request):
    """Detect user's preferred language from Accept-Language header"""
    accept_language = request.headers.get('Accept-Language', '')
    
    # Check for Portuguese variants
    if re.search(r'pt(-[A-Z]{2})?', accept_language, re.IGNORECASE):
        return 'pt'
    
    # Default to English
    return 'en'

def get_translations(lang='en'):
    """Get translations for specified language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS.get('en', {}))

class ShellyController:
    """Controller for Shelly devices"""
    
    def toggle_shelly_relay(self, ip, channel=0, generation=1):
        """Toggle Shelly relay"""
        try:
            if generation == 1:
                response = requests.get(f"http://{ip}/relay/{channel}?turn=toggle", timeout=5)
            else:
                response = requests.post(f"http://{ip}/rpc/Switch.Toggle", 
                                       json={"id": channel}, timeout=5)
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error toggling Shelly relay: {e}")
            return False
    
    def get_shelly_status(self, ip, generation=1):
        """Get Shelly device status"""
        try:
            if generation == 1:
                response = requests.get(f"http://{ip}/status", timeout=5)
            else:
                response = requests.get(f"http://{ip}/rpc/Shelly.GetStatus", timeout=5)
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error getting Shelly status: {e}")
        
        return None
    
    def test_shelly_credentials(self, ip, username=None, password=None):
        """Test Shelly device connection"""
        try:
            auth = (username, password) if username and password else None
            
            # Test Gen 1 API
            response = requests.get(f"http://{ip}/status", auth=auth, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'mac' in data:
                    result = {
                        "success": True,
                        "message": "Connection successful",
                        "mac": data.get('mac'),
                        "device_type": "Shelly Gen 1"
                    }
                    
                    # Get additional info
                    if 'relays' in data:
                        result["relay_count"] = len(data['relays'])
                        result["relay_states"] = [relay.get('ison', False) for relay in data['relays']]
                    
                    if 'meters' in data:
                        result["power_measurement"] = True
                        result["power"] = [meter.get('power', 0) for meter in data['meters']]
                    
                    if 'temperature' in data:
                        result["temperature"] = data['temperature']
                    
                    return result
            
            # Test Gen 2 API
            response = requests.get(f"http://{ip}/rpc/Shelly.GetDeviceInfo", auth=auth, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    return {
                        "success": True,
                        "message": "Connection successful",
                        "mac": data['result'].get('mac'),
                        "device_type": "Shelly Gen 2",
                        "model": data['result'].get('model')
                    }
            
            return {
                "success": False,
                "error": "Not a Shelly device or connection failed"
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

class PDUController:
    """Controller for PDU devices"""
    
    def test_pdu_credentials(self, ip, username, password):
        """Test PDU credentials"""
        try:
            auth = (username, password)
            
            # Test LogiLink/Intellinet endpoint
            response = requests.get(f"http://{ip}/status.xml", auth=auth, timeout=5)
            if response.status_code == 200 and "<response>" in response.text:
                # Parse XML to get outlet information
                try:
                    root = ET.fromstring(response.text)
                    outlets = root.findall(".//outlet")
                    
                    return {
                        "success": True,
                        "outlet_count": len(outlets),
                        "outlets": [outlet.get("id") for outlet in outlets],
                        "message": "Connection successful"
                    }
                except ET.ParseError:
                    return {
                        "success": True,
                        "outlet_count": "Unknown",
                        "message": "Connection successful but couldn't parse XML"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Authentication failed (HTTP {response.status_code})"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
        
    def test_pdu_endpoint(self, ip, timeout=2):
        """Test if an IP has a PDU endpoint"""
        try:
            # Test status.xml endpoint
            url = f"http://{ip}/status.xml"
            response = requests.get(url, timeout=timeout)
            
            if response.status_code == 200 and "<response>" in response.text:
                return {
                    "ip": ip,
                    "status": "found",
                    "endpoint": "status.xml",
                    "type": "LogiLink/Intellinet",
                    "auth_required": False
                }
            elif response.status_code == 401:
                return {
                    "ip": ip,
                    "status": "found",
                    "endpoint": "status.xml",
                    "type": "LogiLink/Intellinet",
                    "auth_required": True
                }
            
            # Test other common PDU endpoints
            endpoints = ["/", "/index.html", "/status", "/api/status"]
            for endpoint in endpoints:
                try:
                    url = f"http://{ip}{endpoint}"
                    response = requests.get(url, timeout=timeout)
                    if response.status_code == 200 and any(keyword in response.text.lower() for keyword in ["pdu", "outlet", "power", "logilink", "intellinet"]):
                        return {
                            "ip": ip,
                            "status": "found",
                            "endpoint": endpoint,
                            "type": "Generic PDU",
                            "auth_required": False
                        }
                except:
                    continue
                    
            return None
            
        except requests.exceptions.RequestException:
            return None
        except Exception as e:
            return None

    def scan_network(self, network_prefix="192.168.1", start=1, end=254, max_workers=50):
        """Scan network for PDUs"""
        self.scanning = True
        self.discovered_pdus = []
        self.scan_progress = 0
        
        logger.info(f"Scanning network {network_prefix}.{start}-{end} for PDUs...")
        
        total_ips = end - start + 1
        processed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create futures for all IPs
            future_to_ip = {
                executor.submit(self.test_pdu_endpoint, f"{network_prefix}.{i}"): f"{network_prefix}.{i}"
                for i in range(start, end + 1)
            }
            
            # Process completed futures
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    result = future.result()
                    if result:
                        self.discovered_pdus.append(result)
                        logger.info(f"Found PDU at {result['ip']}")
                except Exception as e:
                    pass
                
                processed += 1
                self.scan_progress = int((processed / total_ips) * 100)
        
        self.scanning = False
        logger.info(f"Scan complete. Found {len(self.discovered_pdus)} PDUs")
        return self.discovered_pdus

    def test_credentials(self, ip, username="admin", password="admin"):
        """Test PDU credentials"""
        try:
            url = f"http://{ip}/status.xml"
            response = requests.get(url, auth=(username, password), timeout=10)
            
            if response.status_code == 200 and "<response>" in response.text:
                # Parse XML to get device info
                try:
                    xml = ET.fromstring(response.text)
                    
                    # Get outlet status
                    outlets = []
                    for i in range(8):
                        tag = f"outletStat{i}"
                        val = xml.findtext(tag)
                        outlets.append(val.lower() if val else "off")
                    
                    # Get sensor data
                    temp = xml.findtext("tempBan")
                    humidity = xml.findtext("humBan")
                    current = xml.findtext("curBan")
                    
                    return {
                        "success": True,
                        "outlets": outlets,
                        "temperature": temp,
                        "humidity": humidity,
                        "current": current,
                        "outlet_count": len([x for x in outlets if x])
                    }
                except ET.ParseError:
                    return {"success": True, "outlets": [], "outlet_count": 0}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

# Global discovery instance
discovery = PDUDiscovery()

@app.route('/')
def index():
    """Main interface page"""
    lang = detect_language(request)
    translations = get_translations(lang)
    return render_template('index.html', lang=lang, t=translations)

@app.route('/api/scan', methods=['POST'])
def start_scan():
    """Start network scan for PDUs"""
    data = request.json
    network = data.get('network', '192.168.1')
    start_ip = data.get('start', 1)
    end_ip = data.get('end', 254)
    
    if discovery.scanning:
        return jsonify({"error": "Scan already in progress"}), 400
    
    # Start scan in background thread
    thread = threading.Thread(
        target=discovery.scan_network,
        args=(network, start_ip, end_ip)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "Scan started", "status": "scanning"})

@app.route('/api/scan/status')
def scan_status():
    """Get scan status and results"""
    return jsonify({
        "scanning": discovery.scanning,
        "progress": discovery.scan_progress,
        "discovered_pdus": discovery.discovered_pdus
    })

@app.route('/api/test_credentials', methods=['POST'])
def test_credentials():
    """Test PDU credentials"""
    data = request.json
    ip = data.get('ip')
    username = data.get('username', 'admin')
    password = data.get('password', 'admin')
    
    if not ip:
        return jsonify({"error": "IP address required"}), 400
    
    result = discovery.test_credentials(ip, username, password)
    return jsonify(result)

@app.route('/api/save_config', methods=['POST'])
def save_config():
    """Save PDU configuration"""
    data = request.json
    pdus = data.get('pdus', [])
    
    try:
        # Load existing config
        config_file = '/data/options.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {
                "mqtt_host": "localhost",
                "mqtt_port": 1883,
                "mqtt_user": "",
                "mqtt_password": "",
                "mqtt_topic": "pdu"
            }
        
        # Update PDU list
        config['pdu_list'] = pdus
        
        # Save config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return jsonify({"message": "Configuration saved successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/load_config')
def load_config():
    """Load current configuration"""
    try:
        config_file = '/data/options.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
            return jsonify(config)
        else:
            return jsonify({"pdu_list": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_web_interface(host='0.0.0.0', port=8099):
    """Run the web interface"""
    logger.info(f"Starting PDU Discovery Web Interface on {host}:{port}")
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    run_web_interface()
#!/usr/bin/env python3
"""
Web Interface for Device Discovery and Configuration
Modern visual interface for discovering PDUs, Shelly devices, and other network devices
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
from ha_theme_integration import ha_theme_integration

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

# Global instances
device_discovery = DeviceDiscovery()
shelly_controller = ShellyController()
pdu_controller = PDUController()

@app.route('/')
def index():
    """Main interface page"""
    lang = detect_language(request)
    translations = get_translations(lang)
    theme_info = ha_theme_integration.get_theme_info()
    return render_template('index.html', lang=lang, t=translations, theme_info=theme_info)

@app.route('/api/scan', methods=['POST'])
def start_scan():
    """Start device discovery scan"""
    try:
        data = request.get_json()
        network = data.get('network', '192.168.1')
        start_ip = int(data.get('start', 1))
        end_ip = int(data.get('end', 254))
        
        # Start scan in background thread
        thread = threading.Thread(
            target=device_discovery.scan_network,
            args=(network, start_ip, end_ip)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'status': 'started', 'message': 'Scan started'})
    except Exception as e:
        logger.error(f"Error starting scan: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/status', methods=['GET'])
def get_scan_status():
    """Get current scan status"""
    try:
        status = device_discovery.get_scan_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting scan status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test_credentials', methods=['POST'])
def test_credentials():
    """Test device credentials"""
    try:
        data = request.get_json()
        ip = data.get('ip')
        username = data.get('username', 'admin')
        password = data.get('password', 'admin')
        device_type = data.get('device_type', 'pdu')
        
        if device_type.lower() == 'shelly':
            result = shelly_controller.test_shelly_credentials(ip, username, password)
        else:
            result = pdu_controller.test_pdu_credentials(ip, username, password)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error testing credentials: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/shelly/toggle', methods=['POST'])
def toggle_shelly():
    """Toggle Shelly relay"""
    try:
        data = request.get_json()
        ip = data.get('ip')
        channel = data.get('channel', 0)
        generation = data.get('generation', 1)
        
        success = shelly_controller.toggle_shelly_relay(ip, channel, generation)
        
        return jsonify({'success': success})
    except Exception as e:
        logger.error(f"Error toggling Shelly: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/shelly/status', methods=['GET'])
def get_shelly_status():
    """Get Shelly device status"""
    try:
        ip = request.args.get('ip')
        generation = int(request.args.get('generation', 1))
        
        status = shelly_controller.get_shelly_status(ip, generation)
        
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        logger.error(f"Error getting Shelly status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/save_config', methods=['POST'])
def save_config():
    """Save device configuration"""
    try:
        data = request.get_json()
        devices = data.get('devices', [])
        
        # Create configuration structure
        config = {
            'device_list': devices,
            'mqtt': {
                'host': 'localhost',
                'port': 1883,
                'topic_prefix': 'devices'
            }
        }
        
        # Save to config file
        config_path = os.path.join(os.path.dirname(__file__), 'device_config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Configuration saved'})
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/load_config', methods=['GET'])
def load_config():
    """Load device configuration"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'device_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            return jsonify(config)
        else:
            return jsonify({'device_list': []})
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return jsonify({'device_list': []})

@app.route('/api/ha_theme', methods=['GET'])
def get_ha_theme():
    """Get Home Assistant theme information"""
    try:
        theme_info = ha_theme_integration.get_theme_info()
        return jsonify(theme_info)
    except Exception as e:
        logger.error(f"Error getting HA theme: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ha_theme/css', methods=['GET'])
def get_ha_theme_css():
    """Get Home Assistant theme CSS"""
    try:
        theme_name = request.args.get('theme')
        css = ha_theme_integration.generate_css_variables(theme_name)
        
        response = app.response_class(
            response=css,
            mimetype='text/css'
        )
        
        # Add caching headers
        response.headers['Cache-Control'] = 'public, max-age=300'  # 5 minutes
        return response
    except Exception as e:
        logger.error(f"Error generating theme CSS: {e}")
        return app.response_class(
            response=f"/* Error generating theme CSS: {e} */",
            mimetype='text/css'
        ), 500

@app.route('/api/ha_theme/refresh', methods=['POST'])
def refresh_ha_theme():
    """Refresh Home Assistant theme cache"""
    try:
        ha_theme_integration.cached_theme = None
        theme_info = ha_theme_integration.get_theme_info()
        return jsonify(theme_info)
    except Exception as e:
        logger.error(f"Error refreshing HA theme: {e}")
        return jsonify({'error': str(e)}), 500

def run_server(host='0.0.0.0', port=8099):
    """Run the web interface server"""
    try:
        logger.info(f"Starting Device Discovery Web Interface on {host}:{port}")
        app.run(host=host, port=port, debug=False, threaded=True)
    except Exception as e:
        logger.error(f"Error starting web server: {e}")

if __name__ == '__main__':
    run_server()
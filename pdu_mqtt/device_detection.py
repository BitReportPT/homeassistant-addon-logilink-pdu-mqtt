#!/usr/bin/env python3
"""
Advanced Device Detection System
Supports PDUs, Shelly devices, and other network devices
"""

import requests
import json
import re
import logging
from xml.etree import ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class DeviceDetector:
    def __init__(self):
        self.device_patterns = {
            'shelly': {
                'endpoints': ['/status', '/settings', '/shelly'],
                'keywords': ['shelly', 'allterco', 'generation'],
                'headers': {'User-Agent': 'Mozilla/5.0'},
                'ports': [80]
            },
            'pdu_logilink': {
                'endpoints': ['/status.xml'],
                'keywords': ['<response>', '<outlet', '<status>'],
                'headers': {},
                'ports': [80]
            },
            'pdu_generic': {
                'endpoints': ['/', '/index.html', '/status', '/api/status', '/cgi-bin/status.cgi'],
                'keywords': ['pdu', 'outlet', 'power distribution', 'logilink', 'intellinet', 'switched outlet'],
                'headers': {},
                'ports': [80, 8080]
            },
            'false_positive_filters': {
                'keywords': ['iptv', 'tv box', 'android tv', 'kodi', 'plex', 'router', 'access point', 'switch'],
                'titles': ['iptv', 'tv', 'media', 'router', 'access point', 'switch', 'modem']
            }
        }
    
    def detect_shelly_device(self, ip, timeout=3):
        """Detect Shelly devices and get their capabilities"""
        try:
            # Test Shelly Gen 1 API
            response = requests.get(f"http://{ip}/status", timeout=timeout)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'mac' in data and ('relays' in data or 'switches' in data or 'lights' in data):
                        device_info = self.get_shelly_info(ip, data)
                        return {
                            'ip': ip,
                            'type': 'Shelly',
                            'model': device_info.get('model', 'Unknown'),
                            'generation': device_info.get('generation', 1),
                            'capabilities': device_info.get('capabilities', []),
                            'channels': device_info.get('channels', 0),
                            'auth_required': False,
                            'endpoints': ['/status', '/relay/0', '/settings'],
                            'mqtt_available': True,
                            'compatible': True
                        }
                except (json.JSONDecodeError, KeyError):
                    pass
            
            # Test Shelly Gen 2 API
            response = requests.get(f"http://{ip}/rpc/Shelly.GetDeviceInfo", timeout=timeout)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'result' in data and 'id' in data['result']:
                        device_info = self.get_shelly_gen2_info(ip, data['result'])
                        return {
                            'ip': ip,
                            'type': 'Shelly Gen2',
                            'model': device_info.get('model', 'Unknown'),
                            'generation': 2,
                            'capabilities': device_info.get('capabilities', []),
                            'channels': device_info.get('channels', 0),
                            'auth_required': False,
                            'endpoints': ['/rpc/Shelly.GetStatus', '/rpc/Switch.Toggle'],
                            'mqtt_available': True,
                            'compatible': True
                        }
                except (json.JSONDecodeError, KeyError):
                    pass
                    
        except requests.exceptions.RequestException:
            pass
        return None
    
    def get_shelly_info(self, ip, status_data):
        """Extract Shelly device information from Gen 1 API"""
        info = {
            'model': 'Shelly',
            'generation': 1,
            'capabilities': [],
            'channels': 0
        }
        
        # Get device info
        try:
            settings_response = requests.get(f"http://{ip}/settings", timeout=2)
            if settings_response.status_code == 200:
                settings = settings_response.json()
                info['model'] = settings.get('device', {}).get('type', 'Shelly')
        except:
            pass
        
        # Count channels and capabilities
        if 'relays' in status_data:
            info['channels'] = len(status_data['relays'])
            info['capabilities'].append('relay_control')
        
        if 'switches' in status_data:
            info['capabilities'].append('switch_input')
        
        if 'lights' in status_data:
            info['capabilities'].append('light_control')
        
        if 'meters' in status_data:
            info['capabilities'].append('power_measurement')
        
        return info
    
    def get_shelly_gen2_info(self, ip, device_info):
        """Extract Shelly device information from Gen 2 API"""
        info = {
            'model': device_info.get('model', 'Shelly Gen2'),
            'generation': 2,
            'capabilities': [],
            'channels': 0
        }
        
        # Get switch status to count channels
        try:
            status_response = requests.get(f"http://{ip}/rpc/Shelly.GetStatus", timeout=2)
            if status_response.status_code == 200:
                status = status_response.json()
                if 'result' in status:
                    result = status['result']
                    if 'switch:0' in result:
                        # Count switches
                        switch_count = 0
                        for key in result:
                            if key.startswith('switch:'):
                                switch_count += 1
                        info['channels'] = switch_count
                        info['capabilities'].append('switch_control')
                    
                    if 'light:0' in result:
                        info['capabilities'].append('light_control')
                    
                    if 'pm1:0' in result:
                        info['capabilities'].append('power_measurement')
        except:
            pass
        
        return info
    
    def detect_pdu_device(self, ip, timeout=3):
        """Detect PDU devices"""
        try:
            # Test LogiLink/Intellinet specific endpoint
            response = requests.get(f"http://{ip}/status.xml", timeout=timeout)
            if response.status_code == 200 and "<response>" in response.text:
                outlet_count = response.text.count("<outlet")
                return {
                    'ip': ip,
                    'type': 'PDU',
                    'model': 'LogiLink/Intellinet',
                    'outlets': outlet_count,
                    'auth_required': False,
                    'endpoints': ['/status.xml', '/outlet.xml'],
                    'compatible': True
                }
            elif response.status_code == 401:
                return {
                    'ip': ip,
                    'type': 'PDU',
                    'model': 'LogiLink/Intellinet',
                    'outlets': 'Unknown',
                    'auth_required': True,
                    'endpoints': ['/status.xml', '/outlet.xml'],
                    'compatible': True
                }
        except:
            pass
        
        # Test generic PDU endpoints
        endpoints = ["/", "/index.html", "/status", "/api/status", "/cgi-bin/status.cgi"]
        for endpoint in endpoints:
            try:
                response = requests.get(f"http://{ip}{endpoint}", timeout=timeout)
                if response.status_code == 200:
                    content = response.text.lower()
                    if any(keyword in content for keyword in ["pdu", "outlet", "power distribution", "switched outlet"]):
                        # Check if it's not a false positive
                        if not self.is_false_positive(content):
                            return {
                                'ip': ip,
                                'type': 'PDU',
                                'model': 'Generic PDU',
                                'outlets': 'Unknown',
                                'auth_required': False,
                                'endpoints': [endpoint],
                                'compatible': False
                            }
            except:
                continue
        
        return None
    
    def is_false_positive(self, content):
        """Check if the detected device is a false positive"""
        false_positive_keywords = self.device_patterns['false_positive_filters']['keywords']
        
        for keyword in false_positive_keywords:
            if keyword in content.lower():
                return True
        
        # Check for common false positive patterns
        if re.search(r'iptv|tv.*box|android.*tv|media.*player|router|access.*point', content.lower()):
            return True
        
        return False
    
    def detect_device(self, ip, timeout=3):
        """Detect any supported device at the given IP"""
        # First try Shelly detection
        shelly_result = self.detect_shelly_device(ip, timeout)
        if shelly_result:
            return shelly_result
        
        # Then try PDU detection
        pdu_result = self.detect_pdu_device(ip, timeout)
        if pdu_result:
            return pdu_result
        
        # Check for basic web interface (potential unknown device)
        try:
            response = requests.get(f"http://{ip}/", timeout=timeout)
            if response.status_code == 200:
                content = response.text.lower()
                if not self.is_false_positive(content):
                    # Extract title if available
                    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                    title = title_match.group(1) if title_match else 'Unknown Device'
                    
                    return {
                        'ip': ip,
                        'type': 'Unknown Device',
                        'model': title[:50],  # Truncate long titles
                        'auth_required': False,
                        'endpoints': ['/'],
                        'compatible': False
                    }
        except:
            pass
        
        return None

class DeviceDiscovery:
    def __init__(self):
        self.scanning = False
        self.discovered_devices = []
        self.scan_progress = 0
        self.detector = DeviceDetector()
    
    def scan_network(self, network_prefix="192.168.1", start=1, end=254, max_workers=50):
        """Scan network for supported devices"""
        self.scanning = True
        self.discovered_devices = []
        self.scan_progress = 0
        
        logger.info(f"Scanning network {network_prefix}.{start}-{end} for devices...")
        
        total_ips = end - start + 1
        processed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create futures for all IPs
            future_to_ip = {
                executor.submit(self.detector.detect_device, f"{network_prefix}.{i}"): f"{network_prefix}.{i}"
                for i in range(start, end + 1)
            }
            
            # Process completed futures
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    result = future.result()
                    if result:
                        self.discovered_devices.append(result)
                        logger.info(f"Found device: {result['type']} at {ip}")
                except Exception as e:
                    logger.debug(f"Error checking {ip}: {e}")
                
                processed += 1
                self.scan_progress = int((processed / total_ips) * 100)
        
        self.scanning = False
        logger.info(f"Scan complete. Found {len(self.discovered_devices)} devices.")
        return self.discovered_devices
    
    def get_scan_status(self):
        """Get current scan status"""
        return {
            'scanning': self.scanning,
            'progress': self.scan_progress,
            'discovered_devices': self.discovered_devices
        }
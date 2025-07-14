import requests
import logging
from xml.etree import ElementTree as ET
from typing import Dict, Any, Optional, List
import json

logger = logging.getLogger(__name__)

class PDUExtended:
    """Extended PDU control class with full feature support"""
    
    def __init__(self, host: str, username: str = "admin", password: str = "admin"):
        self.host = host
        self.auth = (username, password)
        self.session = requests.Session()
        self.base_url = f"http://{self.host}"
        
        # URLs for different functionalities
        self.urls = {
            'status': f"{self.base_url}/status.xml",
            'control': f"{self.base_url}/control_outlet.htm",
            'config': f"{self.base_url}/config.xml",
            'network': f"{self.base_url}/network.htm",
            'outlet_config': f"{self.base_url}/outlet_config.htm",
            'threshold': f"{self.base_url}/threshold.htm",
            'snmp': f"{self.base_url}/snmp.htm",
            'email': f"{self.base_url}/email.htm",
            'system': f"{self.base_url}/system.htm",
            'users': f"{self.base_url}/users.htm",
            'logs': f"{self.base_url}/logs.htm"
        }
        
        logger.info(f"PDUExtended initialized for host: {self.host}")

    def get_full_status(self) -> Dict[str, Any]:
        """Get complete PDU status including all sensors and outlet states"""
        try:
            r = self.session.get(self.urls['status'], auth=self.auth, timeout=10)
            if r.status_code != 200:
                logger.error(f"HTTP {r.status_code} from {self.host}")
                return {}

            xml = ET.fromstring(r.text)
            
            # Extract all available data
            status = {
                "outlets": [],
                "sensors": {
                    "temperature": {
                        "value": xml.findtext("tempBan"),
                        "unit": "°C"
                    },
                    "humidity": {
                        "value": xml.findtext("humBan"),
                        "unit": "%"
                    },
                    "current": {
                        "value": xml.findtext("curBan"),
                        "unit": "A"
                    }
                },
                "device": {
                    "model": xml.findtext("model", ""),
                    "version": xml.findtext("version", ""),
                    "mac": xml.findtext("mac", ""),
                    "uptime": xml.findtext("uptime", "")
                }
            }
            
            # Get outlet states and names
            for i in range(8):
                outlet_num = i + 1
                outlet_data = {
                    "number": outlet_num,
                    "state": xml.findtext(f"outletStat{i}", "off").lower(),
                    "name": xml.findtext(f"outletName{i}", f"Outlet {outlet_num}"),
                    "delay_on": xml.findtext(f"delayOn{i}", "0"),
                    "delay_off": xml.findtext(f"delayOff{i}", "0")
                }
                
                # Check if individual outlet power monitoring is available
                outlet_power = xml.findtext(f"outletPower{i}")
                if outlet_power:
                    outlet_data["power"] = outlet_power
                    
                status["outlets"].append(outlet_data)
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting full status: {e}")
            return {}

    def get_network_config(self) -> Dict[str, Any]:
        """Get network configuration"""
        try:
            r = self.session.get(self.urls['config'], auth=self.auth, timeout=10)
            if r.status_code != 200:
                return {}
                
            xml = ET.fromstring(r.text)
            
            return {
                "ip": xml.findtext("ip", ""),
                "netmask": xml.findtext("netmask", ""),
                "gateway": xml.findtext("gateway", ""),
                "dns1": xml.findtext("dns1", ""),
                "dns2": xml.findtext("dns2", ""),
                "dhcp": xml.findtext("dhcp", "0") == "1",
                "hostname": xml.findtext("hostname", ""),
                "http_port": xml.findtext("http_port", "80"),
                "https_port": xml.findtext("https_port", "443")
            }
            
        except Exception as e:
            logger.error(f"Error getting network config: {e}")
            return {}

    def set_network_config(self, config: Dict[str, Any]) -> bool:
        """Set network configuration"""
        try:
            payload = {
                "ip": config.get("ip", ""),
                "netmask": config.get("netmask", ""),
                "gateway": config.get("gateway", ""),
                "dns1": config.get("dns1", ""),
                "dns2": config.get("dns2", ""),
                "dhcp": "1" if config.get("dhcp", False) else "0",
                "hostname": config.get("hostname", ""),
                "apply": "1"
            }
            
            r = self.session.post(self.urls['network'], data=payload, auth=self.auth, timeout=10)
            return r.status_code == 200
            
        except Exception as e:
            logger.error(f"Error setting network config: {e}")
            return False

    def set_outlet(self, outlet_num: int, state: bool) -> bool:
        """Control outlet on/off state"""
        if outlet_num < 1 or outlet_num > 8:
            raise ValueError("Outlet number must be 1-8")

        try:
            outlet_key = f"outlet{outlet_num - 1}"
            op = "0" if state else "1"  # 0 = ON, 1 = OFF
            payload = {outlet_key: "1", "op": op}
            
            r = self.session.get(self.urls['control'], params=payload, auth=self.auth, timeout=10)
            return r.status_code == 200
            
        except Exception as e:
            logger.error(f"Error controlling outlet: {e}")
            return False

    def set_outlet_config(self, outlet_num: int, config: Dict[str, Any]) -> bool:
        """Configure outlet settings (name, delays, etc.)"""
        if outlet_num < 1 or outlet_num > 8:
            raise ValueError("Outlet number must be 1-8")

        try:
            payload = {
                f"outlet{outlet_num - 1}_name": config.get("name", f"Outlet {outlet_num}"),
                f"outlet{outlet_num - 1}_delay_on": config.get("delay_on", "0"),
                f"outlet{outlet_num - 1}_delay_off": config.get("delay_off", "0"),
                "apply": "1"
            }
            
            r = self.session.post(self.urls['outlet_config'], data=payload, auth=self.auth, timeout=10)
            return r.status_code == 200
            
        except Exception as e:
            logger.error(f"Error setting outlet config: {e}")
            return False

    def get_thresholds(self) -> Dict[str, Any]:
        """Get sensor threshold settings"""
        try:
            r = self.session.get(self.urls['config'], auth=self.auth, timeout=10)
            if r.status_code != 200:
                return {}
                
            xml = ET.fromstring(r.text)
            
            return {
                "temperature": {
                    "min": xml.findtext("temp_min", ""),
                    "max": xml.findtext("temp_max", ""),
                    "enabled": xml.findtext("temp_alert", "0") == "1"
                },
                "humidity": {
                    "min": xml.findtext("hum_min", ""),
                    "max": xml.findtext("hum_max", ""),
                    "enabled": xml.findtext("hum_alert", "0") == "1"
                },
                "current": {
                    "min": xml.findtext("cur_min", ""),
                    "max": xml.findtext("cur_max", ""),
                    "enabled": xml.findtext("cur_alert", "0") == "1"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting thresholds: {e}")
            return {}

    def set_thresholds(self, thresholds: Dict[str, Any]) -> bool:
        """Set sensor threshold settings"""
        try:
            payload = {}
            
            if "temperature" in thresholds:
                temp = thresholds["temperature"]
                payload.update({
                    "temp_min": temp.get("min", "0"),
                    "temp_max": temp.get("max", "50"),
                    "temp_alert": "1" if temp.get("enabled", False) else "0"
                })
                
            if "humidity" in thresholds:
                hum = thresholds["humidity"]
                payload.update({
                    "hum_min": hum.get("min", "0"),
                    "hum_max": hum.get("max", "100"),
                    "hum_alert": "1" if hum.get("enabled", False) else "0"
                })
                
            if "current" in thresholds:
                cur = thresholds["current"]
                payload.update({
                    "cur_min": cur.get("min", "0"),
                    "cur_max": cur.get("max", "16"),
                    "cur_alert": "1" if cur.get("enabled", False) else "0"
                })
                
            payload["apply"] = "1"
            
            r = self.session.post(self.urls['threshold'], data=payload, auth=self.auth, timeout=10)
            return r.status_code == 200
            
        except Exception as e:
            logger.error(f"Error setting thresholds: {e}")
            return False

    def reboot(self) -> bool:
        """Reboot the PDU"""
        try:
            payload = {"reboot": "1", "confirm": "yes"}
            r = self.session.post(self.urls['system'], data=payload, auth=self.auth, timeout=10)
            return r.status_code == 200
            
        except Exception as e:
            logger.error(f"Error rebooting PDU: {e}")
            return False

    def get_logs(self) -> List[str]:
        """Get system logs"""
        try:
            r = self.session.get(self.urls['logs'], auth=self.auth, timeout=10)
            if r.status_code != 200:
                return []
                
            # Parse logs from response (format depends on PDU model)
            # This is a simplified example
            logs = []
            for line in r.text.split('\n'):
                if line.strip():
                    logs.append(line.strip())
                    
            return logs
            
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return []

    def set_snmp(self, config: Dict[str, Any]) -> bool:
        """Configure SNMP settings"""
        try:
            payload = {
                "snmp_enabled": "1" if config.get("enabled", False) else "0",
                "snmp_community": config.get("community", "public"),
                "snmp_port": config.get("port", "161"),
                "snmp_trap_enabled": "1" if config.get("trap_enabled", False) else "0",
                "snmp_trap_host": config.get("trap_host", ""),
                "snmp_trap_port": config.get("trap_port", "162"),
                "apply": "1"
            }
            
            r = self.session.post(self.urls['snmp'], data=payload, auth=self.auth, timeout=10)
            return r.status_code == 200
            
        except Exception as e:
            logger.error(f"Error setting SNMP config: {e}")
            return False

    def set_email_alerts(self, config: Dict[str, Any]) -> bool:
        """Configure email alert settings"""
        try:
            payload = {
                "email_enabled": "1" if config.get("enabled", False) else "0",
                "smtp_server": config.get("smtp_server", ""),
                "smtp_port": config.get("smtp_port", "25"),
                "smtp_auth": "1" if config.get("smtp_auth", False) else "0",
                "smtp_user": config.get("smtp_user", ""),
                "smtp_pass": config.get("smtp_pass", ""),
                "email_from": config.get("from", ""),
                "email_to": config.get("to", ""),
                "apply": "1"
            }
            
            r = self.session.post(self.urls['email'], data=payload, auth=self.auth, timeout=10)
            return r.status_code == 200
            
        except Exception as e:
            logger.error(f"Error setting email config: {e}")
            return False 
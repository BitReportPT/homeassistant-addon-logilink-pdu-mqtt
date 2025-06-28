import requests
import logging
from xml.etree import ElementTree as ET

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDU:
    def __init__(self, host, username="admin", password="admin"):
        self.host = host
        self.auth = (username, password)
        self.session = requests.Session()
        self.status_url = f"http://{self.host}/status.xml"
        self.control_url = f"http://{self.host}/control_outlet.htm"
        logger.info(f"PDU initialized for host: {self.host}")

    def status(self):
        try:
            logger.debug(f"Fetching status from {self.status_url}")
            r = self.session.get(self.status_url, auth=self.auth, timeout=10)
            
            if r.status_code != 200:
                logger.error(f"HTTP {r.status_code} from {self.host}: {r.text}")
            return {}

            if "<response>" not in r.text:
                logger.error(f"Invalid XML response from {self.host}: {r.text[:200]}")
                return {}

        xml = ET.fromstring(r.text)
        data = {
            "outlets": [],
            "tempBan": xml.findtext("tempBan"),
            "humBan": xml.findtext("humBan"),
            "curBan": xml.findtext("curBan")
        }
            
        for i in range(8):
            tag = f"outletStat{i}"
            val = xml.findtext(tag)
            data["outlets"].append(val.lower() if val else "off")
            
            logger.debug(f"Status for {self.host}: {data}")
        return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {self.host}: {e}")
            return {}
        except ET.ParseError as e:
            logger.error(f"XML parse error for {self.host}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error for {self.host}: {e}")
            return {}

    def set_outlet(self, outlet_num, state):
        if outlet_num < 1 or outlet_num > 8:
            raise ValueError("Outlet number must be 1-8")

        try:
        # outletX is zero-indexed
        outlet_key = f"outlet{outlet_num - 1}"
        op = "0" if state else "1"  # 0 = ON, 1 = OFF
        payload = {outlet_key: "1", "op": op}
            
            logger.info(f"Setting {self.host} outlet {outlet_num} to {'ON' if state else 'OFF'}")
            
            r = self.session.get(self.control_url, params=payload, auth=self.auth, timeout=10)
            
            if r.status_code != 200:
                logger.error(f"Failed to control outlet {outlet_num} on {self.host}: HTTP {r.status_code}")
                return False
                
            logger.info(f"Successfully set {self.host} outlet {outlet_num} to {'ON' if state else 'OFF'}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error controlling outlet {outlet_num} on {self.host}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error controlling outlet {outlet_num} on {self.host}: {e}")
            return False
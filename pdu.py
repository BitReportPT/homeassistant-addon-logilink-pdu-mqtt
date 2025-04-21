import requests

class PDU:
    def __init__(self, host, username="admin", password="admin"):
        self.host = host
        self.auth = (username, password)
        self.session = requests.Session()
        self.status_url = f"http://{self.host}/status.xml"
        self.control_url = f"http://{self.host}/control_outlet.htm"

    def status(self):
        r = self.session.get(self.status_url, auth=self.auth, timeout=5)
        if r.status_code != 200 or "<response>" not in r.text:
            return {}

        from xml.etree import ElementTree as ET
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
        return data

    def set_outlet(self, outlet_num, state):
        if outlet_num < 1 or outlet_num > 8:
            raise ValueError("Outlet number must be 1-8")

        # outletX is zero-indexed
        outlet_key = f"outlet{outlet_num - 1}"
        op = "0" if state else "1"  # 0 = ON, 1 = OFF
        payload = {outlet_key: "1", "op": op}
        self.session.get(self.control_url, params=payload, auth=self.auth, timeout=5)
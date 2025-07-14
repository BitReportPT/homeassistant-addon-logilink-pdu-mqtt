#!/usr/bin/env python3
"""
PDU Discovery Script
Automatically finds LogiLink/Intellinet PDUs on the network
"""

import requests
import threading
import time
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_pdu_endpoint(ip, timeout=2):
    """Test if an IP has a PDU endpoint"""
    try:
        # Test status.xml endpoint
        url = f"http://{ip}/status.xml"
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 200 and "<response>" in response.text:
            return ip, "status.xml", response.text[:200]
        elif response.status_code == 401:
            return ip, "status.xml (auth required)", "Requires authentication"
        
        # Test other common PDU endpoints
        endpoints = ["/", "/index.html", "/status", "/api/status"]
        for endpoint in endpoints:
            try:
                url = f"http://{ip}{endpoint}"
                response = requests.get(url, timeout=timeout)
                if response.status_code == 200 and any(keyword in response.text.lower() for keyword in ["pdu", "outlet", "power", "logilink", "intellinet"]):
                    return ip, endpoint, response.text[:200]
            except:
                continue
                
        return None
        
    except requests.exceptions.RequestException:
        return None
    except Exception as e:
        return None

def scan_network(network_prefix="192.168.1", start=1, end=254, max_workers=50):
    """Scan network for PDUs"""
    print(f"🔍 Scanning network {network_prefix}.{start}-{end} for PDUs...")
    print("This may take a few minutes...")
    
    found_pdus = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create futures for all IPs
        future_to_ip = {
            executor.submit(test_pdu_endpoint, f"{network_prefix}.{i}"): f"{network_prefix}.{i}"
            for i in range(start, end + 1)
        }
        
        # Process completed futures
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                result = future.result()
                if result:
                    ip, endpoint, response = result
                    found_pdus.append({
                        "ip": ip,
                        "endpoint": endpoint,
                        "response_preview": response
                    })
                    print(f"✅ Found PDU at {ip} ({endpoint})")
            except Exception as e:
                pass
    
    return found_pdus

def test_pdu_credentials(ip, usernames=["admin", "root", "user"], passwords=["admin", "password", "1234", ""]):
    """Test common PDU credentials"""
    print(f"🔐 Testing credentials for {ip}...")
    
    for username in usernames:
        for password in passwords:
            try:
                url = f"http://{ip}/status.xml"
                response = requests.get(url, auth=(username, password), timeout=3)
                
                if response.status_code == 200 and "<response>" in response.text:
                    print(f"✅ Valid credentials found: {username}:{password}")
                    return username, password
                    
            except:
                continue
    
    print(f"❌ No valid credentials found for {ip}")
    return None, None

def main():
    print("🚀 PDU Discovery Tool")
    print("=" * 50)
    
    # Get network from user
    if len(sys.argv) > 1:
        network = sys.argv[1]
    else:
        network = input("Enter network prefix (e.g., 192.168.1): ").strip()
    
    if not network:
        network = "192.168.1"
    
    # Scan for PDUs
    pdus = scan_network(network)
    
    if not pdus:
        print("❌ No PDUs found on the network")
        return
    
    print(f"\n🎉 Found {len(pdus)} potential PDU(s):")
    print("=" * 50)
    
    # Test credentials for each found PDU
    working_pdus = []
    
    for pdu in pdus:
        print(f"\n📡 Testing PDU at {pdu['ip']}...")
        username, password = test_pdu_credentials(pdu['ip'])
        
        if username and password:
            working_pdus.append({
                "name": f"pdu_{pdu['ip'].replace('.', '_')}",
                "host": pdu['ip'],
                "username": username,
                "password": password
            })
    
    if working_pdus:
        print(f"\n✅ Found {len(working_pdus)} working PDU(s):")
        print("=" * 50)
        
        for i, pdu in enumerate(working_pdus, 1):
            print(f"{i}. {pdu['name']} - {pdu['host']} ({pdu['username']}:{pdu['password']})")
        
        # Generate configuration
        config = {
            "mqtt_host": "localhost",
            "mqtt_port": 1883,
            "mqtt_user": "mqttuser",
            "mqtt_password": "mqttpass",
            "mqtt_topic": "pdu",
            "pdu_list": working_pdus
        }
        
        print(f"\n📋 Generated configuration:")
        print(json.dumps(config, indent=2))
        
        # Save to file
        with open("discovered_pdus.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"\n💾 Configuration saved to 'discovered_pdus.json'")
        print("You can copy this configuration to your Home Assistant add-on!")
        
    else:
        print("❌ No PDUs with working credentials found")

if __name__ == "__main__":
    main() 
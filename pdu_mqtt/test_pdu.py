#!/usr/bin/env python3
"""
Test script for LogiLink PDU connectivity
"""

import sys
import json
from pdu import PDU

def test_pdu_connection(host, username="admin", password="admin"):
    """Test PDU connection and basic functionality"""
    print(f"Testing PDU connection to {host}...")
    
    try:
        # Initialize PDU
        pdu = PDU(host, username, password)
        print(f"✓ PDU initialized successfully")
        
        # Test status retrieval
        print("Fetching status...")
        status = pdu.status()
        
        if not status:
            print("✗ Failed to retrieve status")
            return False
            
        print("✓ Status retrieved successfully")
        print(f"  Outlets: {status.get('outlets', [])}")
        print(f"  Temperature: {status.get('tempBan', 'N/A')}°C")
        print(f"  Humidity: {status.get('humBan', 'N/A')}%")
        print(f"  Current: {status.get('curBan', 'N/A')}A")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_pdu.py <pdu_host> [username] [password]")
        print("Example: python test_pdu.py 192.168.1.112 admin admin")
        sys.exit(1)
    
    host = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else "admin"
    password = sys.argv[3] if len(sys.argv) > 3 else "admin"
    
    success = test_pdu_connection(host, username, password)
    
    if success:
        print("\n✓ PDU test completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ PDU test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 
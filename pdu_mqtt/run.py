import time
import os
import json
import logging
import paho.mqtt.client as mqtt
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import PDU class from the same directory
from pdu import PDU

# Configuration from environment variables
mqtt_host = os.getenv('MQTT_HOST', 'localhost')
mqtt_port = int(os.getenv('MQTT_PORT', 1883))
mqtt_user = os.getenv('MQTT_USER')
mqtt_password = os.getenv('MQTT_PASSWORD')
mqtt_topic = os.getenv('MQTT_TOPIC', 'pdu')
pdu_list = json.loads(os.getenv('PDU_LIST', '[]'))
auto_discovery = os.getenv('AUTO_DISCOVERY', 'false').lower() == 'true'
discovery_network = os.getenv('DISCOVERY_NETWORK', '192.168.1')

logger.info(f"Starting PDU MQTT Bridge")
logger.info(f"MQTT Host: {mqtt_host}:{mqtt_port}")
logger.info(f"MQTT Topic: {mqtt_topic}")
logger.info(f"Auto Discovery: {auto_discovery}")
logger.info(f"PDU List: {[p['name'] for p in pdu_list]}")

# Initialize MQTT client with compatible version
client = mqtt.Client(protocol=mqtt.MQTTv311)
if mqtt_user and mqtt_password:
    client.username_pw_set(mqtt_user, mqtt_password)

def discover_pdus():
    """Auto-discover PDUs on the network"""
    logger.info(f"Starting auto-discovery on network {discovery_network}")
    
    from discover_pdus import scan_network, test_pdu_credentials
    
    # Scan for PDUs
    found_pdus = scan_network(discovery_network)
    
    if not found_pdus:
        logger.warning("No PDUs found during auto-discovery")
        return []
    
    # Test credentials for found PDUs
    working_pdus = []
    for pdu in found_pdus:
        username, password = test_pdu_credentials(pdu['ip'])
        if username and password:
            working_pdus.append({
                "name": f"pdu_{pdu['ip'].replace('.', '_')}",
                "host": pdu['ip'],
                "username": username,
                "password": password
            })
            logger.info(f"Auto-discovered PDU: {pdu['ip']} ({username}:{password})")
    
    return working_pdus

def publish_status(pdu_name, pdu):
    try:
        status = pdu.status()
        if not status:
            logger.warning(f"No status data received from {pdu_name}")
            return
            
        # Publish outlet states
        for i in range(8):
            outlet = f"outlet{i+1}"
            state = status['outlets'][i] if i < len(status['outlets']) else "off"
            topic = f"{mqtt_topic}/{pdu_name}/{outlet}"
            client.publish(topic, state, retain=True)
            logger.debug(f"Published {topic}: {state}")
        
        # Publish sensor data
        if status.get('tempBan'):
            client.publish(f"{mqtt_topic}/{pdu_name}/temperature", status['tempBan'], retain=True)
            logger.debug(f"Published temperature for {pdu_name}: {status['tempBan']}")
            
        if status.get('humBan'):
            client.publish(f"{mqtt_topic}/{pdu_name}/humidity", status['humBan'], retain=True)
            logger.debug(f"Published humidity for {pdu_name}: {status['humBan']}")
            
        if status.get('curBan'):
            client.publish(f"{mqtt_topic}/{pdu_name}/current", status['curBan'], retain=True)
            logger.debug(f"Published current for {pdu_name}: {status['curBan']}")
            
    except Exception as e:
        logger.error(f"Error publishing status for {pdu_name}: {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Successfully connected to MQTT broker")
        # Subscribe to control topics for all PDUs
        for p in loaded_pdus:
            for i in range(8):
                outlet = f"{mqtt_topic}/{p['name']}/outlet{i+1}/set"
                client.subscribe(outlet)
                logger.info(f"Subscribed to {outlet}")
    else:
        logger.error(f"Failed to connect to MQTT broker with code {rc}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.warning(f"Unexpected disconnection from MQTT broker (rc={rc})")

def on_message(client, userdata, msg):
    try:
        topic_parts = msg.topic.split("/")
        if len(topic_parts) >= 4 and topic_parts[-1] == "set":
            pdu_name = topic_parts[-3]
            outlet_num = int(topic_parts[-2].replace("outlet", ""))
            action = msg.payload.decode().lower()
            
            logger.info(f"Received command: {pdu_name} outlet {outlet_num} -> {action}")
            
            pdu = next((x['pdu'] for x in loaded_pdus if x['name'] == pdu_name), None)
            if pdu:
                success = pdu.set_outlet(outlet_num, action == "on")
                if success:
                    # Publish updated status
                    publish_status(pdu_name, pdu)
                else:
                    logger.error(f"Failed to control outlet {outlet_num} on {pdu_name}")
            else:
                logger.error(f"PDU {pdu_name} not found")
    except Exception as e:
        logger.error(f"Error processing MQTT message: {e}")

# Set up MQTT callbacks
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

# Initialize PDUs (manual + auto-discovery)
loaded_pdus = []

# Add manually configured PDUs
for entry in pdu_list:
    try:
        pdu = PDU(entry["host"], username=entry["username"], password=entry["password"])
        loaded_pdus.append({
            "name": entry["name"],
            "pdu": pdu
        })
        logger.info(f"Initialized manual PDU: {entry['name']} at {entry['host']}")
    except Exception as e:
        logger.error(f"Failed to initialize manual PDU {entry['name']}: {e}")

# Auto-discovery if enabled
if auto_discovery:
    try:
        discovered_pdus = discover_pdus()
        for entry in discovered_pdus:
            try:
                pdu = PDU(entry["host"], username=entry["username"], password=entry["password"])
                loaded_pdus.append({
                    "name": entry["name"],
                    "pdu": pdu
                })
                logger.info(f"Initialized discovered PDU: {entry['name']} at {entry['host']}")
            except Exception as e:
                logger.error(f"Failed to initialize discovered PDU {entry['name']}: {e}")
    except Exception as e:
        logger.error(f"Auto-discovery failed: {e}")

if not loaded_pdus:
    logger.error("No PDUs were successfully initialized. Exiting.")
    sys.exit(1)

logger.info(f"Total PDUs loaded: {len(loaded_pdus)}")

# Connect to MQTT broker
try:
    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_start()
    logger.info("MQTT client started")
except Exception as e:
    logger.error(f"Failed to connect to MQTT broker: {e}")
    sys.exit(1)

# Main loop with parallel processing
logger.info("Starting main loop...")
try:
    while True:
        # Use ThreadPoolExecutor for parallel PDU status updates
        with ThreadPoolExecutor(max_workers=len(loaded_pdus)) as executor:
            futures = []
            for entry in loaded_pdus:
                future = executor.submit(publish_status, entry["name"], entry["pdu"])
                futures.append(future)
            
            # Wait for all futures to complete
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error in parallel processing: {e}")
        
        time.sleep(15)
except KeyboardInterrupt:
    logger.info("Shutting down...")
    client.loop_stop()
    client.disconnect()
except Exception as e:
    logger.error(f"Unexpected error in main loop: {e}")
    client.loop_stop()
    client.disconnect()
    sys.exit(1)
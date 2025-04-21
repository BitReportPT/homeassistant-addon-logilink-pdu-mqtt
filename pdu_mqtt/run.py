import time
import os
import json
import paho.mqtt.client as mqtt
import sys

sys.path.insert(0, '/app/pduapi')
from pdu import PDU

mqtt_host = os.getenv('MQTT_HOST', 'localhost')
mqtt_port = int(os.getenv('MQTT_PORT', 1883))
mqtt_user = os.getenv('MQTT_USER')
mqtt_password = os.getenv('MQTT_PASSWORD')
mqtt_topic = os.getenv('MQTT_TOPIC', 'pdu')
pdu_list = json.loads(os.getenv('PDU_LIST', '[]'))

client = mqtt.Client(protocol=mqtt.MQTTv311, callback_api_version=5)
if mqtt_user and mqtt_password:
    client.username_pw_set(mqtt_user, mqtt_password)

def publish_status(pdu_name, pdu):
    status = pdu.status()
    for i in range(8):
        outlet = f"outlet{i+1}"
        state = status['outlets'][i]
        client.publish(f"{mqtt_topic}/{pdu_name}/{outlet}", state, retain=True)
    if 'tempBan' in status:
        client.publish(f"{mqtt_topic}/{pdu_name}/temperature", status['tempBan'], retain=True)
    if 'humBan' in status:
        client.publish(f"{mqtt_topic}/{pdu_name}/humidity", status['humBan'], retain=True)
    if 'curBan' in status:
        client.publish(f"{mqtt_topic}/{pdu_name}/current", status['curBan'], retain=True)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    for p in pdu_list:
        for i in range(8):
            outlet = f"{mqtt_topic}/{p['name']}/outlet{i+1}/set"
            client.subscribe(outlet)

def on_message(client, userdata, msg):
    topic_parts = msg.topic.split("/")
    if len(topic_parts) >= 4 and topic_parts[-1] == "set":
        pdu_name = topic_parts[-3]
        outlet_num = int(topic_parts[-2].replace("outlet", ""))
        action = msg.payload.decode().lower()
        pdu = next((x['pdu'] for x in loaded_pdus if x['name'] == pdu_name), None)
        if pdu:
            pdu.set_outlet(outlet_num, action == "on")
            publish_status(pdu_name, pdu)

client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_host, mqtt_port, 60)
client.loop_start()

loaded_pdus = []
for entry in pdu_list:
    loaded_pdus.append({
        "name": entry["name"],
        "pdu": PDU(entry["host"], username=entry["username"], password=entry["password"])
    })

while True:
    for entry in loaded_pdus:
        publish_status(entry["name"], entry["pdu"])
    time.sleep(15)
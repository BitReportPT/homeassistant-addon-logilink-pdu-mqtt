# LogiLink PDU MQTT Bridge - Complete Feature List

## Overview

This extended version of the PDU MQTT Bridge exposes ALL features available in the LogiLink PDU8P01 web interface via MQTT topics.

## MQTT Topics Structure

Base topic: `pdu/{pdu_name}/`

### 1. Outlet Control & Status

#### Basic Control
- **State**: `pdu/{pdu_name}/outlet{1-8}/state` (ON/OFF)
- **Control**: `pdu/{pdu_name}/outlet{1-8}/set` (ON/OFF)
- **Name**: `pdu/{pdu_name}/outlet{1-8}/name` (outlet custom name)
- **Power**: `pdu/{pdu_name}/outlet{1-8}/power` (power consumption in W, if available)

#### Outlet Configuration
- **Get Config**: `pdu/{pdu_name}/outlet/{1-8}/config` (JSON)
- **Set Config**: `pdu/{pdu_name}/outlet/{1-8}/config/set` (JSON)

Example config JSON:
```json
{
  "name": "Server 1",
  "delay_on": "5",
  "delay_off": "10"
}
```

### 2. Sensor Data

- **Temperature**: `pdu/{pdu_name}/sensor/temperature` (°C)
- **Humidity**: `pdu/{pdu_name}/sensor/humidity` (%)
- **Current**: `pdu/{pdu_name}/sensor/current` (A)

### 3. Network Configuration

#### Get Current Config
- **Topic**: `pdu/{pdu_name}/network/config` (JSON)

#### Set Network Config
- **Topic**: `pdu/{pdu_name}/network/set` (JSON)

Example network config:
```json
{
  "ip": "192.168.1.215",
  "netmask": "255.255.255.0",
  "gateway": "192.168.1.1",
  "dns1": "8.8.8.8",
  "dns2": "8.8.4.4",
  "dhcp": false,
  "hostname": "pdu-rack-01",
  "http_port": "80",
  "https_port": "443"
}
```

### 4. Threshold Configuration

#### Get/Set Temperature Thresholds
- **Get**: `pdu/{pdu_name}/threshold/temperature` (JSON)
- **Set**: `pdu/{pdu_name}/threshold/temperature/set` (JSON)

#### Get/Set Humidity Thresholds
- **Get**: `pdu/{pdu_name}/threshold/humidity` (JSON)
- **Set**: `pdu/{pdu_name}/threshold/humidity/set` (JSON)

#### Get/Set Current Thresholds
- **Get**: `pdu/{pdu_name}/threshold/current` (JSON)
- **Set**: `pdu/{pdu_name}/threshold/current/set` (JSON)

Example threshold config:
```json
{
  "min": "10",
  "max": "30",
  "enabled": true
}
```

### 5. SNMP Configuration

- **Set Config**: `pdu/{pdu_name}/snmp/set` (JSON)

Example SNMP config:
```json
{
  "enabled": true,
  "community": "public",
  "port": "161",
  "trap_enabled": true,
  "trap_host": "192.168.1.100",
  "trap_port": "162"
}
```

### 6. Email Alert Configuration

- **Set Config**: `pdu/{pdu_name}/email/set` (JSON)

Example email config:
```json
{
  "enabled": true,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": "587",
  "smtp_auth": true,
  "smtp_user": "alerts@example.com",
  "smtp_pass": "password",
  "from": "pdu@example.com",
  "to": "admin@example.com"
}
```

### 7. System Control

- **Reboot**: `pdu/{pdu_name}/system/reboot` (send "REBOOT")
- **Status**: `pdu/{pdu_name}/system/status` (status messages)
- **Device Info**: `pdu/{pdu_name}/device/info` (JSON with model, version, MAC, uptime)

### 8. Home Assistant Discovery

When enabled, the bridge automatically publishes discovery messages for:

#### Switches (8 outlets)
- Entity IDs: `switch.{pdu_name}_outlet1` through `switch.{pdu_name}_outlet8`

#### Sensors
- Temperature: `sensor.{pdu_name}_temperature`
- Humidity: `sensor.{pdu_name}_humidity`
- Current: `sensor.{pdu_name}_current`

## Usage Examples

### 1. Turn on outlet 1
```bash
mosquitto_pub -h 192.168.1.241 -u mqttuser -P mqttpass \
  -t "pdu/rack_01/outlet1/set" -m "ON"
```

### 2. Configure outlet name and delays
```bash
mosquitto_pub -h 192.168.1.241 -u mqttuser -P mqttpass \
  -t "pdu/rack_01/outlet/1/config/set" \
  -m '{"name": "Main Server", "delay_on": "10", "delay_off": "5"}'
```

### 3. Set temperature alert thresholds
```bash
mosquitto_pub -h 192.168.1.241 -u mqttuser -P mqttpass \
  -t "pdu/rack_01/threshold/temperature/set" \
  -m '{"min": "15", "max": "28", "enabled": true}'
```

### 4. Configure network settings
```bash
mosquitto_pub -h 192.168.1.241 -u mqttuser -P mqttpass \
  -t "pdu/rack_01/network/set" \
  -m '{"ip": "192.168.1.216", "netmask": "255.255.255.0", "gateway": "192.168.1.1"}'
```

### 5. Reboot PDU
```bash
mosquitto_pub -h 192.168.1.241 -u mqttuser -P mqttpass \
  -t "pdu/rack_01/system/reboot" -m "REBOOT"
```

## Monitoring Examples

### 1. Subscribe to all outlet states
```bash
mosquitto_sub -h 192.168.1.241 -u mqttuser -P mqttpass \
  -t "pdu/rack_01/outlet+/state" -v
```

### 2. Monitor sensor data
```bash
mosquitto_sub -h 192.168.1.241 -u mqttuser -P mqttpass \
  -t "pdu/rack_01/sensor/+" -v
```

### 3. Watch for configuration changes
```bash
mosquitto_sub -h 192.168.1.241 -u mqttuser -P mqttpass \
  -t "pdu/rack_01/+/config" -v
```

## Home Assistant Integration

### Automation Example
```yaml
automation:
  - alias: "PDU Temperature Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.rack_01_temperature
        above: 30
    action:
      - service: notify.mobile_app
        data:
          title: "PDU Temperature Alert"
          message: "Rack temperature is {{ states('sensor.rack_01_temperature') }}°C"
```

### Script Example
```yaml
script:
  reboot_server_sequence:
    sequence:
      - service: switch.turn_off
        entity_id: switch.rack_01_outlet1
      - delay: "00:00:10"
      - service: switch.turn_on
        entity_id: switch.rack_01_outlet1
```

## Advanced Features

### 1. Bulk Outlet Control
You can create scripts to control multiple outlets:

```python
import paho.mqtt.client as mqtt
import time

client = mqtt.Client()
client.username_pw_set("mqttuser", "mqttpass")
client.connect("192.168.1.241", 1883)

# Turn off all outlets
for i in range(1, 9):
    client.publish(f"pdu/rack_01/outlet{i}/set", "OFF")
    time.sleep(1)

# Turn on in sequence with delays
for i in range(1, 9):
    client.publish(f"pdu/rack_01/outlet{i}/set", "ON")
    time.sleep(5)
```

### 2. Configuration Backup
Subscribe to all config topics to backup PDU settings:

```bash
mosquitto_sub -h 192.168.1.241 -u mqttuser -P mqttpass \
  -t "pdu/rack_01/+/config" -t "pdu/rack_01/network/config" \
  -t "pdu/rack_01/threshold/+" -C 10 > pdu_backup.txt
```

## Notes

1. All configuration changes require JSON payloads
2. Status topics use `retain=true` for persistence
3. The bridge polls PDU status every 30 seconds
4. Network changes may cause temporary disconnection
5. Some features may vary depending on PDU firmware version 
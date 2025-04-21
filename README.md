# LogiLink PDU MQTT Bridge

A native Home Assistant add-on that connects to one or multiple LogiLink PDU8P01 (rack-mounted, IP-controlled smart power distribution units) and publishes their status and controls via MQTT. Includes temperature, humidity, and current monitoring.

## ✅ Features

- Control 8 power outlets per PDU (on/off)
- Read PDU environment sensors: **temperature**, **humidity**, **current**
- Multi-PDU support (each with a unique name)
- MQTT integration (with `retain: true`)
- Full configuration via UI
- Compatible with the **latest Home Assistant version** (2024+)
- Ready to use as a **custom repository in HACS**

## 🚀 Installation (via HACS)

1. Upload this repository to your GitHub:  
   Example: `https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt`

2. In Home Assistant:
   - Go to `Settings → Add-ons → ... (top right) → Repositories`
   - Add your GitHub link as **type: Add-on repository**
   - It will appear in the add-on store as **LogiLink PDU MQTT Bridge**

3. Install and configure it via the UI

## ⚙️ Configuration Options

Example:

```yaml
mqtt_host: "192.168.1.10"
mqtt_port: 1883
mqtt_user: "ha"
mqtt_password: "supersecure"
mqtt_topic: "pdu"
pdu_list:
  - name: rack_01
    host: "192.168.1.100"
    username: "admin"
    password: "admin"
```

## 📡 MQTT Topics

| Topic                                | Type        | Description               |
|--------------------------------------|-------------|---------------------------|
| `pdu/rack_01/outlet1` to `outlet8`   | State       | Current outlet state      |
| `pdu/rack_01/outletX/set`            | Command     | Send "on" or "off"        |
| `pdu/rack_01/temperature`            | Sensor      | Temperature (°C)          |
| `pdu/rack_01/humidity`               | Sensor      | Humidity (%)              |
| `pdu/rack_01/current`                | Sensor      | Current usage (A)         |

## 🧩 Integration in Home Assistant (example)

```yaml
mqtt:
  switch:
    - name: "Rack 01 - Outlet 1"
      state_topic: "pdu/rack_01/outlet1"
      command_topic: "pdu/rack_01/outlet1/set"
      payload_on: "on"
      payload_off: "off"
      retain: true

  sensor:
    - name: "Rack 01 - Temperature"
      state_topic: "pdu/rack_01/temperature"
      unit_of_measurement: "°C"
```

## 📦 Compatibility

- Tested with: LogiLink PDU8P01
- May work with other similar HTTP/XML-based smart PDUs
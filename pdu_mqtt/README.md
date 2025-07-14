# LogiLink & Intellinet PDU MQTT Bridge

![Supports amd64 Architecture][amd64-shield]
![Supports aarch64 Architecture][aarch64-shield]
![Supports armv7 Architecture][armv7-shield]

[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg

## About

This Home Assistant add-on provides MQTT integration for LogiLink PDU8P01 and Intellinet 163682 (8x IEC-C13 smart PDU) devices. It allows you to monitor and control individual power outlets through MQTT, with automatic Home Assistant discovery support.

## Features

- **Multi-PDU Support**: Control multiple PDU devices from a single add-on
- **MQTT Integration**: Full MQTT support with Home Assistant auto-discovery
- **Individual Outlet Control**: Control each of the 8 outlets independently
- **Real-time Monitoring**: Monitor power consumption and outlet status
- **Automatic Discovery**: Automatically creates Home Assistant entities
- **Secure Communication**: Supports MQTT authentication

## Installation

1. Add this repository to your Home Assistant Supervisor
2. Install the "LogiLink & Intellinet PDU MQTT Bridge" add-on
3. Configure the add-on (see configuration section below)
4. Start the add-on

## Configuration

Add your PDU devices and MQTT settings to the add-on configuration:

```yaml
mqtt_host: "192.168.1.241"
mqtt_port: 1883
mqtt_user: "mqttuser"
mqtt_password: "mqttpass"
mqtt_topic: "pdu"
pdu_list:
  - name: "rack_01"
    host: "192.168.1.215"
    username: "admin"
    password: "admin"
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `mqtt_host` | string | `localhost` | MQTT broker hostname or IP address |
| `mqtt_port` | int | `1883` | MQTT broker port |
| `mqtt_user` | string | - | MQTT username (optional) |
| `mqtt_password` | string | - | MQTT password (optional) |
| `mqtt_topic` | string | `pdu` | Base MQTT topic for PDU devices |
| `pdu_list` | list | - | List of PDU devices to control |

### PDU Configuration

Each PDU in the `pdu_list` requires:

| Option | Type | Description |
|--------|------|-------------|
| `name` | string | Unique identifier for the PDU |
| `host` | string | PDU IP address or hostname |
| `username` | string | PDU web interface username |
| `password` | string | PDU web interface password |

## Usage

Once configured and started, the add-on will:

1. Connect to your MQTT broker
2. Discover configured PDU devices
3. Create Home Assistant entities for each outlet
4. Publish device status and accept control commands via MQTT

### MQTT Topics

The add-on uses the following MQTT topic structure:

- `pdu/{pdu_name}/outlet{N}/state` - Outlet state (ON/OFF)
- `pdu/{pdu_name}/outlet{N}/set` - Control outlet (ON/OFF)
- `pdu/{pdu_name}/outlet{N}/power` - Power consumption (if supported)

### Home Assistant Integration

Entities are automatically created in Home Assistant:

- **Switches**: `switch.{pdu_name}_outlet{N}` - Control each outlet
- **Sensors**: `sensor.{pdu_name}_outlet{N}_power` - Power consumption monitoring

## Supported Devices

- LogiLink PDU8P01 (8x IEC-C13 smart PDU)
- Intellinet 163682 (8x IEC-C13 smart PDU)

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/your-username/homeassistant-addon-logilink-pdu-mqtt).

## License

This add-on is licensed under the MIT License. 
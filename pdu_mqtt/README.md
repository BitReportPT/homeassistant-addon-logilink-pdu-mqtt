# Device MQTT Bridge (PDU & Shelly)

An advanced Home Assistant add-on that provides MQTT integration for PDUs and Shelly devices with visual discovery capabilities.

## Features

### Device Support
- **PDU Devices**: LogiLink PDU8P01, Intellinet 163682, and other compatible PDUs
- **Shelly Devices**: Generation 1 and 2 devices (1PM, 4PM, Plus 1PM, Pro 4PM, etc.)
- **Intelligent Detection**: Automatically identifies device types and capabilities
- **False Positive Filtering**: Excludes IPTV boxes, routers, and other non-target devices

### Visual Discovery Interface
- **Multi-language Support**: English and Portuguese with automatic detection
- **Real-time Scanning**: Network scanning with progress visualization
- **Device Cards**: Rich information display for each discovered device
- **Credential Testing**: Built-in connection testing for all device types
- **Live Control**: Toggle Shelly relays directly from the interface

### MQTT Integration
- **Home Assistant Discovery**: Automatic entity creation
- **Real-time Updates**: Live status monitoring and control
- **Flexible Configuration**: Support for multiple device types in one configuration

## Supported Devices

### PDU Devices
- LogiLink PDU8P01
- Intellinet 163682
- Generic PDUs with XML API

### Shelly Devices
- **Generation 1**: 1, 1PM, 2.5, 4Pro, EM, etc.
- **Generation 2**: Plus 1, Plus 1PM, Pro 1PM, Pro 4PM, etc.
- **Features**: Relay control, power measurement, temperature sensing

## Installation

1. Add this repository to your Home Assistant Supervisor
2. Install the "Device MQTT Bridge" add-on
3. Configure your MQTT broker settings
4. Start the add-on
5. Access the web interface at `http://homeassistant.local:8099`

## Configuration

### Basic Configuration
```yaml
mqtt_host: "localhost"
mqtt_port: 1883
mqtt_user: ""
mqtt_password: ""
mqtt_topic: "devices"
auto_discovery: true
discovery_network: "192.168.1"
discovery_range_start: 1
discovery_range_end: 254
device_list: []
```

### Device List Format
The `device_list` can contain both PDUs and Shelly devices:

```yaml
device_list:
  - name: "pdu_server_rack"
    host: "192.168.1.100"
    type: "PDU"
    username: "admin"
    password: "admin"
  - name: "shelly_kitchen_lights"
    host: "192.168.1.101"
    type: "Shelly"
    username: ""
    password: ""
```

## Web Interface

The visual discovery interface provides:

1. **Network Scanning**: Automatic discovery of devices on your network
2. **Device Information**: Detailed information about each discovered device
3. **Credential Testing**: Verify connection to devices before adding them
4. **Live Control**: Control Shelly devices directly from the interface
5. **Configuration Management**: Add/remove devices from your configuration

### Device Detection

The system intelligently identifies:

- **PDU Devices**: By checking for `/status.xml` endpoints and PDU-specific keywords
- **Shelly Devices**: By testing Generation 1 and 2 APIs and device signatures
- **False Positives**: Filters out IPTV boxes, routers, and other non-target devices

### Shelly Integration

For Shelly devices, the system provides:

- **Automatic Generation Detection**: Identifies Gen 1 vs Gen 2 devices
- **Capability Discovery**: Detects relay count, power measurement, sensors
- **Direct Control**: Toggle relays without needing MQTT
- **Status Monitoring**: Real-time device status updates

## MQTT Topics

### PDU Devices
- Status: `devices/pdu_name/status`
- Control: `devices/pdu_name/outlet_X/set`
- Sensors: `devices/pdu_name/temperature`, `devices/pdu_name/current`

### Shelly Devices
- Status: `devices/shelly_name/status`
- Control: `devices/shelly_name/relay_X/set`
- Power: `devices/shelly_name/power_X`

## Language Support

The interface automatically detects your browser language and supports:
- **English** (default)
- **Portuguese** (pt, pt-PT, pt-BR)

## Troubleshooting

### Common Issues

1. **Device Not Detected**
   - Ensure the device is on the same network
   - Check if the device has a web interface
   - Verify the device is not filtered as a false positive

2. **Shelly Device Not Responding**
   - Check if the device is in AP mode
   - Verify network connectivity
   - Ensure the device firmware is up to date

3. **PDU Authentication Fails**
   - Default credentials are usually `admin/admin`
   - Some devices may require different credentials
   - Check device documentation for default login

### Logs

Check the Home Assistant logs for detailed error messages:
```
Settings -> System -> Logs -> Device MQTT Bridge
```

## Advanced Features

### Device Control API

The add-on provides REST API endpoints for device control:

- `POST /api/shelly/toggle` - Toggle Shelly relay
- `GET /api/shelly/status` - Get Shelly device status
- `POST /api/test_credentials` - Test device credentials

### Custom Device Types

The system can be extended to support additional device types by modifying the `device_detection.py` file.

## Version History

- **1.4.0**: Added Shelly device support, improved detection, multi-language interface
- **1.3.4**: Basic PDU support with visual discovery
- **1.3.0**: Initial release with LogiLink/Intellinet PDU support

## Support

For issues and feature requests, please create an issue in the GitHub repository.

## License

This project is licensed under the MIT License. 
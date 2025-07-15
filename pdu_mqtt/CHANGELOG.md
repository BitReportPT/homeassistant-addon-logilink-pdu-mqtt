# Changelog

All notable changes to this project will be documented in this file.

## [1.4.0] - 2024-12-15

### Added
- **Shelly Device Support**: Complete support for Shelly Generation 1 and 2 devices
- **Advanced Device Detection**: Intelligent device identification with false positive filtering
- **Multi-language Interface**: Support for English and Portuguese with automatic detection
- **Enhanced Web Interface**: Improved visual discovery with device-specific information
- **Live Device Control**: Toggle Shelly relays directly from the web interface
- **Device Capability Detection**: Automatic identification of device features and channels
- **Improved Error Handling**: Better error messages and connection stability
- **REST API**: Additional endpoints for device control and status monitoring

### Changed
- **Renamed Add-on**: From "PDU MQTT Bridge" to "Device MQTT Bridge (PDU & Shelly)"
- **Configuration Format**: Updated to support multiple device types with `device_list`
- **Interface Language**: Changed from Portuguese to English by default
- **Device Cards**: Enhanced with device-specific icons and information
- **Scan Results**: Now shows all compatible devices, not just PDUs

### Enhanced
- **Device Detection**: 
  - Shelly Gen 1 API support (`/status`, `/settings`)
  - Shelly Gen 2 API support (`/rpc/Shelly.GetDeviceInfo`, `/rpc/Shelly.GetStatus`)
  - Improved PDU detection with multiple endpoint testing
  - False positive filtering for IPTV boxes, routers, and other devices
- **Web Interface**:
  - Real-time device control capabilities
  - Device-specific credential testing
  - Enhanced visual feedback and progress indicators
  - Responsive design with modern UI components
- **MQTT Integration**:
  - Support for both PDU and Shelly device types
  - Enhanced topic structure for mixed device environments
  - Improved Home Assistant auto-discovery

### Fixed
- **Language Issues**: Corrected Portuguese grammar and added proper English defaults
- **Device Compatibility**: Better handling of different device API versions
- **Connection Stability**: Improved error handling and timeout management
- **UI Responsiveness**: Fixed layout issues and improved mobile compatibility

### Technical Improvements
- **Modular Architecture**: Separated device detection into `device_detection.py`
- **Translation System**: Implemented proper i18n with `translations.json`
- **Controller Classes**: Dedicated controllers for PDU and Shelly devices
- **API Expansion**: Additional REST endpoints for device management
- **Docker Integration**: Updated Dockerfile to include all new components

## [1.3.4] - 2024-12-14

### Added
- **Visual Discovery Interface**: Web-based PDU discovery at port 8099
- **Real-time Scanning**: Network scanning with progress visualization
- **Credential Testing**: Built-in connection testing for discovered devices
- **Configuration Management**: Visual configuration without manual YAML editing

### Fixed
- **Infinite Loop**: Fixed status publishing loop with proper error handling
- **Missing Dependencies**: Added Flask and werkzeug to requirements
- **Logging Spam**: Changed excessive INFO logging to DEBUG level
- **paho-mqtt Compatibility**: Added compatibility layer for different API versions

## [1.3.0] - 2024-12-13

### Added
- **Initial Release**: Basic PDU support for LogiLink and Intellinet devices
- **MQTT Integration**: Full Home Assistant auto-discovery support
- **Multi-PDU Support**: Control multiple PDU devices from single add-on
- **Outlet Control**: Individual control of all 8 outlets per PDU
- **Real-time Monitoring**: Status updates and sensor data

### Features
- LogiLink PDU8P01 support
- Intellinet 163682 support
- XML API integration
- Home Assistant entity creation
- MQTT authentication support

## Migration Guide

### From 1.3.x to 1.4.0

1. **Configuration Update**: Replace `pdu_list` with `device_list` in your configuration
2. **Device Types**: Add `type: "PDU"` to existing PDU entries
3. **New Features**: Explore the enhanced web interface for device discovery
4. **Shelly Integration**: Add Shelly devices to your configuration using the discovery interface

### Example Migration

**Before (1.3.x)**:
```yaml
pdu_list:
  - name: "rack_pdu"
    host: "192.168.1.100"
    username: "admin"
    password: "admin"
```

**After (1.4.0)**:
```yaml
device_list:
  - name: "rack_pdu"
    host: "192.168.1.100"
    type: "PDU"
    username: "admin"
    password: "admin"
```

## Future Roadmap

- **Additional Device Types**: Support for more smart home devices
- **Enhanced UI**: More visualization options and control panels
- **Advanced Scheduling**: Built-in scheduling for device control
- **Group Management**: Device grouping and bulk operations
- **Cloud Integration**: Optional cloud connectivity for remote access 
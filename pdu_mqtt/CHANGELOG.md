# Changelog

All notable changes to this add-on will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-07-14

### Added
- **Complete feature merge** - Combined all extended features into main version
- Support for all advanced MQTT topics (configuration, thresholds, network, etc.)
- Device info publishing with model and status
- Subscriptions to all extended control topics ready for future implementation
- Text sensor entity for device information

### Changed
- Major refactoring to merge simple and extended versions
- Improved code organization and structure
- Better error handling for all message types
- Sensor topics now use /sensor/ prefix for consistency
- This is now the single unified version with all features

### Fixed
- Fixed sensor topic paths to match documentation
- Improved connection handling and logging

### Notes
- Extended features (network config, thresholds, etc.) are subscribed but not yet implemented in PDU class
- All MQTT topics are ready for future PDU firmware that supports these features

## [1.2.2] - 2025-06-15

### Added
- **MQTT Discovery implementation** - Entities are now automatically created in Home Assistant
- Discovery messages sent on connection for all switches and sensors
- Each outlet creates a switch entity (switch.rack_01_outlet1, etc.)
- Sensor entities for temperature, humidity, and current

### Fixed
- Fixed "Entity not found" issue in dashboard
- Entities are now properly registered with Home Assistant

### Changed
- Improved connection callback to send discovery after successful connection
- Better logging for discovery process

## [1.2.1] - 2025-05-20

### Added
- Debug logging mode for better troubleshooting
- Comprehensive dashboard with all 8 outlet controls
- Advanced configuration options via dashboard
- Quick actions for All ON/OFF with confirmations
- Power sequence script for sequential outlet control
- Outlet configuration selector in dashboard
- High current alert automation
- Extended PDU control implementation (pdu_extended.py) for future features
- Complete MQTT feature documentation
- Verification guide and test scripts

### Fixed
- Fixed version string consistency across all files
- Improved status publishing with proper error handling
- Added missing debug messages for status updates
- Fixed dashboard to enable all 8 outlets (removed test restrictions)

### Changed
- Enhanced logging to show status updates every 30 seconds
- Improved error messages for better debugging
- Dashboard now shows all outlets as fully functional
- Added confirmation dialogs for critical actions
- Better organization of dashboard controls

### Documentation
- Added MQTT_FEATURES.md with complete topic documentation
- Created VERIFICATION_GUIDE.md for troubleshooting
- Added test_commands.sh for easy MQTT testing
- Updated examples with working configurations

## [1.2.0] - 2025-04-10

### Added
- Full working release with stable operation
- Confirmed MQTT connectivity and PDU control
- Successfully tested with LogiLink PDU8P01 devices

### Fixed
- Fixed MQTT Client deprecation warning by updating to API v2
- Added proper callback signatures for MQTT v2 API
- Updated version string in startup message

### Changed
- Updated MQTT Client to use CallbackAPIVersion.VERSION2
- Added 2-second delay after connection for stability
- This is the first stable production-ready release

### Verified
- MQTT connection working with authentication
- All 8 outlets subscribing to control topics
- PDU initialization and communication confirmed
- No s6-overlay errors after removing init system

## [1.1.9] - 2025-03-18

### Fixed
- Completely resolved s6-overlay-suexec errors by disabling s6-overlay
- Removed all s6-overlay dependencies and service structure
- Add-on now runs Python directly without init system
- Simplified container execution to avoid PID 1 conflicts

### Changed
- Set init: false in config.yaml to disable s6-overlay
- Removed rootfs directory and all s6-overlay service scripts
- Simplified Dockerfile to run Python directly with CMD
- Removed unnecessary build arguments and labels
- Direct Python execution with unbuffered output (-u flag)

### Removed
- Removed s6-overlay service structure (/etc/services.d/)
- Removed bashio dependencies from service scripts
- Removed complex container initialization

## [1.1.8] - 2025-02-22

### Fixed
- Fixed s6-overlay-suexec errors by optimizing PDU instance creation
- PDU instances are now created once at startup and reused in the main loop
- Eliminated repeated PDU initialization that was causing system conflicts
- Improved memory usage and performance by avoiding unnecessary object creation
- Fixed MQTT topic structure to use proper state topics with /state suffix

### Changed
- Refactored main loop to reuse PDU instances instead of creating new ones
- Improved error handling and logging throughout the application
- Updated MQTT message handling for better reliability
- Added proper disconnect callback for MQTT client

### Performance
- Reduced system resource usage by eliminating redundant PDU instantiation
- Improved startup time by creating PDU instances once during initialization
- Better memory management in the main monitoring loop

## [1.1.7] - 2025-02-05

### Fixed
- Fixed persistent s6-overlay-suexec errors by simplifying service scripts
- Replaced bashio calls with standard bash commands in s6-overlay scripts
- Added explicit chmod permissions for s6-overlay scripts in Dockerfile
- Improved script compatibility with s6-overlay environment
- Fixed service initialization to prevent suexec conflicts

### Changed
- Simplified s6-overlay service scripts to use standard bash instead of bashio
- Updated service scripts to use basic echo instead of bashio logging
- Added explicit permission setting for service scripts during build

## [1.1.6] - 2025-01-12

### Fixed
- Fixed s6-overlay integration to prevent "can only run as pid 1" error
- Added proper s6-overlay service structure with rootfs directory
- Removed direct run.sh execution in favor of s6-overlay services
- Added init: true configuration for proper container initialization
- Updated Dockerfile to use s6-overlay service structure
- Added proper service scripts for start and stop handling

### Changed
- Migrated from direct script execution to s6-overlay service management
- Updated container structure to follow Home Assistant s6-overlay conventions

## [1.1.5] - 2024-12-20

### Fixed
- Fixed add-on structure to follow Home Assistant conventions
- Corrected config.yaml and build.yaml formats
- Removed incorrect manifest.json file
- Updated Dockerfile to use Home Assistant base images
- Added proper run.sh script for add-on startup

### Changed
- Restructured add-on to follow official Home Assistant add-on guidelines
- Updated documentation with proper configuration examples

## [1.1.4] - 2024-11-15

### Added
- MQTT Discovery support for automatic Home Assistant entity creation
- Support for multiple PDU devices in single add-on
- Power consumption monitoring (where supported)
- Improved error handling and logging

### Changed
- Refactored code structure for better maintainability
- Updated configuration schema for better validation

## [1.1.3] - 2024-10-10

### Fixed
- Fixed PDU communication reliability issues
- Improved MQTT connection stability
- Better handling of network timeouts

## [1.1.2] - 2024-09-08

### Added
- Support for Intellinet 163682 devices
- Enhanced device discovery functionality
- Better configuration validation

## [1.1.1] - 2024-08-12

### Fixed
- Fixed outlet control commands
- Improved status reporting accuracy
- Better error messages for troubleshooting

## [1.1.0] - 2024-07-15

### Added
- Initial release of LogiLink PDU MQTT Bridge add-on
- Support for LogiLink PDU8P01 devices
- MQTT integration with Home Assistant
- Individual outlet control (8 outlets)
- Basic power monitoring capabilities
- Web interface authentication support 
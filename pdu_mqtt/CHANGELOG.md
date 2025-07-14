# Changelog

All notable changes to this add-on will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.6] - 2025-01-25

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

## [1.1.5] - 2025-01-25

### Fixed
- Fixed add-on structure to follow Home Assistant conventions
- Corrected config.yaml and build.yaml formats
- Removed incorrect manifest.json file
- Updated Dockerfile to use Home Assistant base images
- Added proper run.sh script for add-on startup

### Changed
- Restructured add-on to follow official Home Assistant add-on guidelines
- Updated documentation with proper configuration examples

## [1.1.4] - 2025-01-25

### Added
- MQTT Discovery support for automatic Home Assistant entity creation
- Support for multiple PDU devices in single add-on
- Power consumption monitoring (where supported)
- Improved error handling and logging

### Changed
- Refactored code structure for better maintainability
- Updated configuration schema for better validation

## [1.1.3] - 2025-01-24

### Fixed
- Fixed PDU communication reliability issues
- Improved MQTT connection stability
- Better handling of network timeouts

## [1.1.2] - 2025-01-24

### Added
- Support for Intellinet 163682 devices
- Enhanced device discovery functionality
- Better configuration validation

## [1.1.1] - 2025-01-24

### Fixed
- Fixed outlet control commands
- Improved status reporting accuracy
- Better error messages for troubleshooting

## [1.1.0] - 2025-01-24

### Added
- Initial release of LogiLink PDU MQTT Bridge add-on
- Support for LogiLink PDU8P01 devices
- MQTT integration with Home Assistant
- Individual outlet control (8 outlets)
- Basic power monitoring capabilities
- Web interface authentication support 
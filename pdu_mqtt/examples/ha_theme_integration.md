# Home Assistant Theme Integration

## Overview

The Device MQTT Bridge now includes full integration with Home Assistant's theme system. This means the web interface automatically matches your current Home Assistant theme, providing a seamless visual experience.

## Features

### 🎨 **Automatic Theme Detection**
- Detects your current Home Assistant theme
- Automatically applies theme colors to the web interface
- Updates in real-time when you change themes

### 🌙 **Dark Mode Support**
- Automatic dark mode detection
- Proper contrast adjustments for dark themes
- Smooth transitions between light and dark modes

### 🔄 **Real-time Updates**
- Monitors theme changes every 30 seconds
- Instantly applies new theme without page refresh
- Shows connection status to Home Assistant

### 📊 **Theme Status Indicator**
- Shows current theme name and Home Assistant version
- Visual indicator of connection status
- Green border when connected, red when disconnected

## How It Works

### 1. **Theme Detection**
The system attempts to connect to Home Assistant using various methods:
- Internal add-on URLs (`http://supervisor/core`, `http://homeassistant:8123`)
- Environment variables (`SUPERVISOR_TOKEN`, `HOMEASSISTANT_TOKEN`)
- Configuration file (`/data/options.json`)

### 2. **CSS Variable Extraction**
Once connected, the system:
- Retrieves the current theme configuration
- Extracts CSS variables like `--primary-color`, `--card-background-color`
- Generates dynamic CSS that matches your theme

### 3. **Real-time Application**
The web interface:
- Loads the dynamic CSS as a stylesheet
- Applies theme-specific colors to all elements
- Updates automatically when themes change

## Theme Variables Used

### Primary Colors
- `--primary-color` - Main accent color
- `--accent-color` - Secondary accent color
- `--primary-background-color` - Main background
- `--card-background-color` - Card backgrounds

### Text Colors
- `--primary-text-color` - Main text color
- `--secondary-text-color` - Secondary text color
- `--text-primary-color` - Text on primary backgrounds

### Interface Colors
- `--divider-color` - Borders and dividers
- `--error-color` - Error messages
- `--success-color` - Success messages
- `--warning-color` - Warning messages

### Component Colors
- `--sidebar-background-color` - Sidebar background
- `--app-header-background-color` - Header background
- `--ha-card-border-radius` - Card border radius
- `--ha-card-box-shadow` - Card shadows

## Device-Specific Styling

### Color Coding
- **Shelly Devices**: Green border (`--device-shelly-color`)
- **PDU Devices**: Blue border (`--device-pdu-color`)
- **Unknown Devices**: Gray border (`--device-unknown-color`)

### Visual Indicators
- Compatible devices show with solid borders
- Non-compatible devices show with dashed borders
- Different device types have unique icons

## Configuration

### Environment Variables
```bash
# Home Assistant URL (auto-detected for add-ons)
HOMEASSISTANT_URL=http://homeassistant.local:8123

# Access token (auto-detected for add-ons)
HOMEASSISTANT_TOKEN=your_long_lived_token
```

### API Endpoints
- `GET /api/ha_theme` - Get current theme info
- `GET /api/ha_theme/css` - Get dynamic CSS
- `POST /api/ha_theme/refresh` - Refresh theme cache

## Fallback Behavior

### When Home Assistant is Unavailable
- Falls back to default Material Design theme
- Shows "Default Theme" in status indicator
- Red border indicates disconnection
- Interface remains fully functional

### Theme Variables Fallback
```css
/* Example fallback values */
background: var(--primary-background-color, #fafafa);
color: var(--primary-text-color, #212121);
border: var(--divider-color, #e0e0e0);
```

## Examples

### Light Theme
```css
:root {
  --primary-color: #03a9f4;
  --primary-background-color: #fafafa;
  --card-background-color: #ffffff;
  --primary-text-color: #212121;
}
```

### Dark Theme
```css
:root {
  --primary-color: #bb86fc;
  --primary-background-color: #121212;
  --card-background-color: #1e1e1e;
  --primary-text-color: #ffffff;
}
```

### Custom Theme
```css
:root {
  --primary-color: #ff6b6b;
  --accent-color: #4ecdc4;
  --primary-background-color: #2c3e50;
  --card-background-color: #34495e;
  --primary-text-color: #ecf0f1;
}
```

## Benefits

### 🎯 **Consistent Experience**
- Interface matches your Home Assistant theme
- No jarring color differences
- Professional, integrated appearance

### 🔧 **Zero Configuration**
- Works automatically with any Home Assistant theme
- No manual CSS customization needed
- Respects your existing theme preferences

### 🚀 **Performance**
- CSS is cached for 5 minutes
- Minimal impact on Home Assistant
- Efficient theme change detection

### 🛡️ **Reliability**
- Graceful fallback when HA is unavailable
- Error handling for network issues
- Continues working even if theme service fails

## Troubleshooting

### Theme Not Loading
1. Check Home Assistant connection in status indicator
2. Verify add-on has access to Home Assistant API
3. Check logs for authentication errors

### Colors Not Updating
1. Try refreshing the page
2. Check if theme actually changed in Home Assistant
3. Use `/api/ha_theme/refresh` endpoint to force update

### Connection Issues
1. Verify Home Assistant is running
2. Check network connectivity
3. Ensure proper permissions for add-on

## Technical Details

### Architecture
```
[Home Assistant] → [Theme API] → [Add-on Web Interface]
     ↓                ↓                    ↓
[Theme Config] → [CSS Variables] → [Dynamic Styling]
```

### Update Cycle
1. Every 30 seconds: Check current theme
2. If changed: Download new CSS variables
3. Apply: Update stylesheet link
4. Refresh: Visual elements update automatically

### Performance Impact
- **Minimal**: Only checks theme every 30 seconds
- **Cached**: CSS is cached for 5 minutes
- **Efficient**: Only updates when theme actually changes

This integration makes your device discovery interface feel like a native part of Home Assistant!
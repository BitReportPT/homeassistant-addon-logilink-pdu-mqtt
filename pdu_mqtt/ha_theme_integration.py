#!/usr/bin/env python3
"""
Home Assistant Theme Integration
Fetches the current theme from Home Assistant and applies it to the web interface
"""

import requests
import json
import logging
import os
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class HomeAssistantThemeIntegration:
    def __init__(self):
        self.ha_url = self._get_ha_url()
        self.ha_token = self._get_ha_token()
        self.cached_theme = None
        self.default_theme_variables = self._get_default_theme_variables()
    
    def _get_ha_url(self) -> str:
        """Get Home Assistant URL from environment or default"""
        # Try different possible sources for HA URL
        ha_url = os.environ.get('HOMEASSISTANT_URL', 'http://homeassistant.local:8123')
        
        # For Home Assistant add-ons, try common internal URLs
        if 'homeassistant.local' in ha_url:
            internal_urls = [
                'http://supervisor/core',
                'http://homeassistant:8123',
                'http://127.0.0.1:8123',
                'http://localhost:8123'
            ]
            
            for url in internal_urls:
                try:
                    response = requests.get(f"{url}/api/", timeout=2)
                    if response.status_code == 200:
                        ha_url = url
                        break
                except:
                    continue
        
        return ha_url
    
    def _get_ha_token(self) -> Optional[str]:
        """Get Home Assistant long-lived access token"""
        # Check environment variables
        token = os.environ.get('SUPERVISOR_TOKEN')
        if not token:
            token = os.environ.get('HOMEASSISTANT_TOKEN')
        
        # For add-ons, try to read from supervisor
        if not token:
            try:
                with open('/data/options.json', 'r') as f:
                    options = json.load(f)
                    token = options.get('ha_token')
            except:
                pass
        
        return token
    
    def _get_default_theme_variables(self) -> Dict[str, str]:
        """Default Home Assistant theme variables"""
        return {
            # Primary colors
            '--primary-color': '#03a9f4',
            '--accent-color': '#ff9800',
            '--primary-background-color': '#fafafa',
            '--secondary-background-color': '#e0e0e0',
            '--card-background-color': '#ffffff',
            
            # Text colors
            '--primary-text-color': '#212121',
            '--secondary-text-color': '#727272',
            '--text-primary-color': '#ffffff',
            '--disabled-text-color': '#bdbdbd',
            
            # Interface colors
            '--divider-color': '#e0e0e0',
            '--error-color': '#f44336',
            '--success-color': '#4caf50',
            '--warning-color': '#ff9800',
            
            # Sidebar
            '--sidebar-background-color': '#ffffff',
            '--sidebar-text-color': '#212121',
            '--sidebar-icon-color': '#727272',
            '--sidebar-selected-icon-color': '#03a9f4',
            
            # Header
            '--app-header-background-color': '#03a9f4',
            '--app-header-text-color': '#ffffff',
            
            # Cards
            '--ha-card-border-radius': '8px',
            '--ha-card-box-shadow': '0 2px 4px rgba(0,0,0,0.1)',
            
            # Buttons
            '--mdc-theme-primary': '#03a9f4',
            '--mdc-theme-on-primary': '#ffffff',
            '--mdc-theme-secondary': '#ff9800',
            '--mdc-theme-on-secondary': '#ffffff',
            
            # States
            '--state-active-color': '#4caf50',
            '--state-inactive-color': '#9e9e9e',
            '--state-unavailable-color': '#f44336',
            
            # Fonts
            '--paper-font-headline_-_font-family': 'Roboto, sans-serif',
            '--paper-font-headline_-_font-size': '24px',
            '--paper-font-headline_-_font-weight': '400',
            '--paper-font-subhead_-_font-family': 'Roboto, sans-serif',
            '--paper-font-subhead_-_font-size': '16px',
            '--paper-font-subhead_-_font-weight': '400',
            
            # Special device colors
            '--device-shelly-color': '#4caf50',
            '--device-pdu-color': '#2196f3',
            '--device-unknown-color': '#9e9e9e',
        }
    
    def get_current_theme(self) -> Optional[Dict[str, Any]]:
        """Get the current theme from Home Assistant"""
        if not self.ha_url or not self.ha_token:
            logger.warning("Home Assistant URL or token not available")
            return None
        
        try:
            # Get current config including frontend settings
            headers = {
                'Authorization': f'Bearer {self.ha_token}',
                'Content-Type': 'application/json'
            }
            
            # Try to get frontend config
            response = requests.get(
                f"{self.ha_url}/api/config",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                config = response.json()
                logger.info(f"Retrieved HA config: {config.get('version', 'unknown')}")
                
                # Try to get current theme via states
                states_response = requests.get(
                    f"{self.ha_url}/api/states",
                    headers=headers,
                    timeout=5
                )
                
                if states_response.status_code == 200:
                    states = states_response.json()
                    
                    # Look for frontend entity with theme info
                    for state in states:
                        if state.get('entity_id') == 'frontend':
                            attributes = state.get('attributes', {})
                            theme = attributes.get('theme', 'default')
                            logger.info(f"Current theme: {theme}")
                            return {'theme': theme, 'config': config}
                
                return {'theme': 'default', 'config': config}
            
        except Exception as e:
            logger.error(f"Error getting HA theme: {e}")
        
        return None
    
    def get_theme_variables(self, theme_name: str = None) -> Dict[str, str]:
        """Get theme variables from Home Assistant"""
        if not theme_name:
            theme_info = self.get_current_theme()
            if theme_info:
                theme_name = theme_info.get('theme', 'default')
            else:
                theme_name = 'default'
        
        # If we can't get theme from HA, use defaults
        if not self.ha_url or not self.ha_token:
            return self.default_theme_variables
        
        try:
            headers = {
                'Authorization': f'Bearer {self.ha_token}',
                'Content-Type': 'application/json'
            }
            
            # Try to get themes configuration
            response = requests.post(
                f"{self.ha_url}/api/services/frontend/get_themes",
                headers=headers,
                json={},
                timeout=5
            )
            
            if response.status_code == 200:
                themes_data = response.json()
                logger.info(f"Retrieved themes data: {list(themes_data.keys())}")
                
                # Get theme variables
                theme_vars = self.default_theme_variables.copy()
                
                if theme_name != 'default' and theme_name in themes_data:
                    theme_config = themes_data[theme_name]
                    
                    # Update with theme-specific variables
                    for key, value in theme_config.items():
                        if key.startswith('--') or key in ['primary-color', 'accent-color']:
                            theme_vars[f'--{key}' if not key.startswith('--') else key] = value
                
                return theme_vars
                
        except Exception as e:
            logger.error(f"Error getting theme variables: {e}")
        
        return self.default_theme_variables
    
    def detect_dark_mode(self) -> bool:
        """Detect if the current theme is dark mode"""
        theme_info = self.get_current_theme()
        if theme_info:
            theme_name = theme_info.get('theme', 'default')
            return 'dark' in theme_name.lower() or 'night' in theme_name.lower()
        return False
    
    def generate_css_variables(self, theme_name: str = None) -> str:
        """Generate CSS variables string for the current theme"""
        variables = self.get_theme_variables(theme_name)
        
        css_vars = []
        for key, value in variables.items():
            # Ensure key starts with --
            if not key.startswith('--'):
                key = f'--{key}'
            
            # Clean up the value
            if isinstance(value, str):
                value = value.strip()
                if not value.startswith('#') and not value.startswith('rgb') and not value.startswith('var('):
                    # Try to convert to hex if it's a named color
                    if value in ['red', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink', 'cyan']:
                        color_map = {
                            'red': '#f44336',
                            'green': '#4caf50',
                            'blue': '#2196f3',
                            'yellow': '#ffeb3b',
                            'orange': '#ff9800',
                            'purple': '#9c27b0',
                            'pink': '#e91e63',
                            'cyan': '#00bcd4'
                        }
                        value = color_map.get(value, value)
            
            css_vars.append(f'  {key}: {value};')
        
        return ':root {\n' + '\n'.join(css_vars) + '\n}'
    
    def get_theme_info(self) -> Dict[str, Any]:
        """Get comprehensive theme information"""
        theme_info = self.get_current_theme()
        
        if not theme_info:
            return {
                'theme_name': 'default',
                'is_dark': False,
                'variables': self.default_theme_variables,
                'css': self.generate_css_variables(),
                'ha_available': False
            }
        
        theme_name = theme_info.get('theme', 'default')
        variables = self.get_theme_variables(theme_name)
        
        return {
            'theme_name': theme_name,
            'is_dark': self.detect_dark_mode(),
            'variables': variables,
            'css': self.generate_css_variables(theme_name),
            'ha_available': True,
            'ha_version': theme_info.get('config', {}).get('version', 'unknown')
        }

# Global instance
ha_theme_integration = HomeAssistantThemeIntegration()
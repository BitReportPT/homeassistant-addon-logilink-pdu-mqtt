#!/usr/bin/env python3
"""
PDU MQTT Bridge - Main Application
Professional Home Assistant add-on for PDU control and monitoring
"""

import asyncio
import json
import logging
import os
import signal
import sys
from typing import Dict, Any

from pdu_manager import PDUManager
from mqtt_bridge import MQTTBridge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/pdu_bridge.log')
    ]
)
logger = logging.getLogger(__name__)

class PDUApplication:
    """Main application class"""
    
    def __init__(self):
        self.config = self._load_config()
        self.pdu_manager = None
        self.mqtt_bridge = None
        self.running = False
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        config = {
            "mqtt": {
                "host": os.getenv("MQTT_HOST", "localhost"),
                "port": int(os.getenv("MQTT_PORT", "1883")),
                "username": os.getenv("MQTT_USERNAME", ""),
                "password": os.getenv("MQTT_PASSWORD", ""),
                "topic_prefix": os.getenv("MQTT_TOPIC_PREFIX", "pdu"),
                "discovery_prefix": os.getenv("MQTT_DISCOVERY_PREFIX", "homeassistant"),
                "retain": os.getenv("MQTT_RETAIN", "true").lower() == "true"
            },
            "pdus": json.loads(os.getenv("PDUS", "[]")),
            "discovery": {
                "enabled": os.getenv("DISCOVERY_ENABLED", "false").lower() == "true",
                "network": os.getenv("DISCOVERY_NETWORK", "192.168.1"),
                "scan_interval": int(os.getenv("DISCOVERY_SCAN_INTERVAL", "300")),
                "credentials": json.loads(os.getenv("DISCOVERY_CREDENTIALS", '[]'))
            },
            "advanced": {
                "log_level": os.getenv("LOG_LEVEL", "INFO"),
                "health_check": os.getenv("HEALTH_CHECK", "true").lower() == "true",
                "parallel_requests": int(os.getenv("PARALLEL_REQUESTS", "5")),
                "timeout": int(os.getenv("TIMEOUT", "10")),
                "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", "3"))
            }
        }
        
        # Set log level
        logging.getLogger().setLevel(getattr(logging, config["advanced"]["log_level"]))
        
        logger.info("Configuration loaded")
        logger.debug(f"Config: {json.dumps(config, indent=2)}")
        
        return config
    
    async def initialize(self):
        """Initialize the application"""
        logger.info("Initializing PDU MQTT Bridge...")
        
        try:
            # Initialize PDU manager
            self.pdu_manager = PDUManager(self.config)
            await self.pdu_manager.initialize_pdus()
            
            if not self.pdu_manager.pdus:
                logger.error("No PDUs were initialized. Exiting.")
                return False
            
            # Initialize MQTT bridge
            self.mqtt_bridge = MQTTBridge(self.config, self.pdu_manager)
            await self.mqtt_bridge.initialize()
            
            logger.info(f"Initialized {len(self.pdu_manager.pdus)} PDU(s)")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    async def start(self):
        """Start the application"""
        if not await self.initialize():
            return
        
        self.running = True
        logger.info("Starting PDU MQTT Bridge...")
        
        # Set up signal handlers
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._signal_handler)
        
        try:
            # Start monitoring and publishing tasks
            tasks = [
                asyncio.create_task(self.pdu_manager.start_monitoring()),
                asyncio.create_task(self.mqtt_bridge.start_publishing())
            ]
            
            # Wait for tasks to complete
            await asyncio.gather(*tasks)
            
        except asyncio.CancelledError:
            logger.info("Application cancelled")
        except Exception as e:
            logger.error(f"Application error: {e}")
        finally:
            await self.cleanup()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.pdu_manager.stop_monitoring()
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up...")
        
        if self.pdu_manager:
            await self.pdu_manager.cleanup()
        
        if self.mqtt_bridge:
            self.mqtt_bridge.disconnect()
        
        logger.info("Cleanup completed")

async def main():
    """Main entry point"""
    app = PDUApplication()
    await app.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)
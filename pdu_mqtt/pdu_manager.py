#!/usr/bin/env python3
"""
Professional PDU Manager for Home Assistant
Supports multiple PDU models with unified interface
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import aiohttp
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

@dataclass
class PDUStatus:
    """PDU status data structure"""
    outlets: List[str]
    temperature: Optional[float]
    humidity: Optional[float]
    current: Optional[float]
    voltage: Optional[float]
    power: Optional[float]
    status: str
    last_update: float
    error_count: int = 0

@dataclass
class PDUConfig:
    """PDU configuration"""
    name: str
    host: str
    username: str
    password: str
    model: str
    scan_interval: int
    timeout: int
    retry_attempts: int

class PDUDriver(ABC):
    """Abstract base class for PDU drivers"""
    
    @abstractmethod
    async def get_status(self) -> Optional[PDUStatus]:
        """Get PDU status"""
        pass
    
    @abstractmethod
    async def set_outlet(self, outlet: int, state: bool) -> bool:
        """Set outlet state"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test PDU connection"""
        pass

class LogiLinkDriver(PDUDriver):
    """LogiLink PDU driver"""
    
    def __init__(self, config: PDUConfig):
        self.config = config
        self.session = None
        self.auth = aiohttp.BasicAuth(config.username, config.password)
        
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                auth=self.auth
            )
        return self.session
    
    async def test_connection(self) -> bool:
        try:
            session = await self._get_session()
            async with session.get(f"http://{self.config.host}/status.xml") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Connection test failed for {self.config.name}: {e}")
            return False
    
    async def get_status(self) -> Optional[PDUStatus]:
        try:
            session = await self._get_session()
            async with session.get(f"http://{self.config.host}/status.xml") as response:
                if response.status != 200:
                    return None
                
                text = await response.text()
                if "<response>" not in text:
                    return None
                
                root = ET.fromstring(text)
                
                # Parse outlets
                outlets = []
                for i in range(8):
                    outlet_val = root.findtext(f"outletStat{i}")
                    outlets.append(outlet_val.lower() if outlet_val else "off")
                
                # Parse sensors
                temp = root.findtext("tempBan")
                humidity = root.findtext("humBan")
                current = root.findtext("curBan")
                
                return PDUStatus(
                    outlets=outlets,
                    temperature=float(temp) if temp else None,
                    humidity=float(humidity) if humidity else None,
                    current=float(current) if current else None,
                    voltage=None,
                    power=None,
                    status="online",
                    last_update=time.time()
                )
                
        except Exception as e:
            logger.error(f"Failed to get status for {self.config.name}: {e}")
            return None
    
    async def set_outlet(self, outlet: int, state: bool) -> bool:
        if outlet < 1 or outlet > 8:
            return False
            
        try:
            session = await self._get_session()
            outlet_key = f"outlet{outlet - 1}"
            op = "0" if state else "1"
            
            params = {outlet_key: "1", "op": op}
            async with session.get(f"http://{self.config.host}/control_outlet.htm", params=params) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Failed to set outlet {outlet} for {self.config.name}: {e}")
            return False

class IntellinetDriver(LogiLinkDriver):
    """Intellinet PDU driver (extends LogiLink for compatibility)"""
    pass

class PDUManager:
    """Main PDU manager class"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pdus: Dict[str, PDUDriver] = {}
        self.status_cache: Dict[str, PDUStatus] = {}
        self.running = False
        
    def _create_driver(self, pdu_config: Dict[str, Any]) -> PDUDriver:
        """Create appropriate driver for PDU model"""
        config = PDUConfig(
            name=pdu_config["name"],
            host=pdu_config["host"],
            username=pdu_config["username"],
            password=pdu_config["password"],
            model=pdu_config.get("model", "auto"),
            scan_interval=pdu_config.get("scan_interval", 30),
            timeout=pdu_config.get("timeout", 10),
            retry_attempts=pdu_config.get("retry_attempts", 3)
        )
        
        model = config.model.lower()
        if model in ["logilink", "auto"]:
            return LogiLinkDriver(config)
        elif model == "intellinet":
            return IntellinetDriver(config)
        else:
            # Auto-detect based on response
            return LogiLinkDriver(config)
    
    async def initialize_pdus(self):
        """Initialize all configured PDUs"""
        for pdu_config in self.config.get("pdus", []):
            try:
                driver = self._create_driver(pdu_config)
                if await driver.test_connection():
                    self.pdus[pdu_config["name"]] = driver
                    logger.info(f"Initialized PDU: {pdu_config['name']}")
                else:
                    logger.error(f"Failed to connect to PDU: {pdu_config['name']}")
            except Exception as e:
                logger.error(f"Failed to initialize PDU {pdu_config['name']}: {e}")
    
    async def get_all_status(self) -> Dict[str, PDUStatus]:
        """Get status for all PDUs"""
        tasks = []
        for name, driver in self.pdus.items():
            tasks.append(self._get_pdu_status(name, driver))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for name, result in zip(self.pdus.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Error getting status for {name}: {result}")
                # Use cached status if available
                if name in self.status_cache:
                    self.status_cache[name].error_count += 1
            else:
                self.status_cache[name] = result
        
        return self.status_cache
    
    async def _get_pdu_status(self, name: str, driver: PDUDriver) -> PDUStatus:
        """Get status for a single PDU"""
        status = await driver.get_status()
        if status is None:
            # Return cached status with error
            cached = self.status_cache.get(name)
            if cached:
                cached.error_count += 1
                cached.status = "error"
                return cached
            else:
                return PDUStatus(
                    outlets=["off"] * 8,
                    temperature=None,
                    humidity=None,
                    current=None,
                    voltage=None,
                    power=None,
                    status="error",
                    last_update=time.time(),
                    error_count=1
                )
        return status
    
    async def set_outlet(self, pdu_name: str, outlet: int, state: bool) -> bool:
        """Set outlet state for specific PDU"""
        if pdu_name not in self.pdus:
            return False
        
        driver = self.pdus[pdu_name]
        success = await driver.set_outlet(outlet, state)
        
        if success:
            # Update cache immediately
            await self._get_pdu_status(pdu_name, driver)
        
        return success
    
    async def start_monitoring(self):
        """Start monitoring loop"""
        self.running = True
        logger.info("Starting PDU monitoring")
        
        while self.running:
            try:
                await self.get_all_status()
                await asyncio.sleep(30)  # Default scan interval
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(10)
    
    def stop_monitoring(self):
        """Stop monitoring loop"""
        self.running = False
        logger.info("Stopping PDU monitoring")
    
    async def cleanup(self):
        """Cleanup resources"""
        for driver in self.pdus.values():
            if hasattr(driver, 'session') and driver.session:
                await driver.session.close() 
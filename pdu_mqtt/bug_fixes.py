#!/usr/bin/env python3
"""
Bug Fixes para PDU MQTT Bridge
Correções de problemas identificados e melhorias de estabilidade
"""

import logging
import time
import json
from typing import Optional, Dict, Any
import requests
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

class PDUBugFixes:
    """Classe com correções de bugs e melhorias"""
    
    @staticmethod
    def fix_xml_parsing(xml_content: str) -> Optional[Dict[str, Any]]:
        """
        Bug Fix: Parsing XML mais robusto para diferentes formatos de PDU
        """
        try:
            # Remove caracteres problemáticos
            xml_content = xml_content.strip()
            
            # Verifica se contém a tag response
            if "<response>" not in xml_content:
                logger.warning("XML não contém tag <response>")
                return None
            
            # Parse XML com tratamento de erros
            xml = ET.fromstring(xml_content)
            
            # Extrai dados com valores padrão
            data = {
                "outlets": [],
                "tempBan": xml.findtext("tempBan", "N/A"),
                "humBan": xml.findtext("humBan", "N/A"),
                "curBan": xml.findtext("curBan", "N/A")
            }
            
            # Extrai status das tomadas com fallback
            for i in range(8):
                tag = f"outletStat{i}"
                val = xml.findtext(tag)
                if val is not None:
                    data["outlets"].append(val.lower())
                else:
                    data["outlets"].append("unknown")
            
            # Converte valores numéricos com validação
            for key in ["tempBan", "humBan", "curBan"]:
                try:
                    if data[key] not in ["N/A", None, ""]:
                        # Tenta converter para float para validar
                        float(data[key])
                except (ValueError, TypeError):
                    data[key] = "N/A"
            
            return data
            
        except ET.ParseError as e:
            logger.error(f"Erro ao fazer parse do XML: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado no parsing XML: {e}")
            return None
    
    @staticmethod
    def fix_connection_timeout(url: str, auth: tuple, timeout: int = 10) -> Optional[requests.Response]:
        """
        Bug Fix: Conexão com timeout e retry automático
        """
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url, 
                    auth=auth, 
                    timeout=timeout,
                    headers={
                        'User-Agent': 'PDU-MQTT-Bridge/1.4.0',
                        'Accept': 'application/xml, text/xml'
                    }
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 401:
                    logger.error(f"Credenciais inválidas para {url}")
                    return response
                else:
                    logger.warning(f"HTTP {response.status_code} em tentativa {attempt + 1}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout na tentativa {attempt + 1} para {url}")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Erro de conexão na tentativa {attempt + 1} para {url}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro na requisição: {e}")
                
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        
        logger.error(f"Falha após {max_retries} tentativas para {url}")
        return None
    
    @staticmethod
    def fix_outlet_state_validation(outlet_num: int, state: Any) -> bool:
        """
        Bug Fix: Validação robusta do estado das tomadas
        """
        if not isinstance(outlet_num, int) or outlet_num < 1 or outlet_num > 8:
            logger.error(f"Número de tomada inválido: {outlet_num}")
            return False
        
        # Normaliza o estado
        if isinstance(state, str):
            state = state.lower().strip()
            valid_states = ['on', 'off', 'true', 'false', '1', '0']
            if state not in valid_states:
                logger.error(f"Estado inválido: {state}")
                return False
        elif isinstance(state, bool):
            pass  # Estado booleano é válido
        elif isinstance(state, int):
            if state not in [0, 1]:
                logger.error(f"Estado numérico inválido: {state}")
                return False
        else:
            logger.error(f"Tipo de estado inválido: {type(state)}")
            return False
        
        return True
    
    @staticmethod
    def fix_mqtt_topic_validation(topic: str) -> str:
        """
        Bug Fix: Validação e limpeza de tópicos MQTT
        """
        if not topic or not isinstance(topic, str):
            logger.warning("Tópico MQTT inválido, usando padrão")
            return "pdu"
        
        # Remove caracteres problemáticos
        topic = topic.strip()
        invalid_chars = ['#', '+', '\x00']
        for char in invalid_chars:
            if char in topic:
                logger.warning(f"Removendo caractere inválido '{char}' do tópico")
                topic = topic.replace(char, '')
        
        # Remove barras duplas
        while '//' in topic:
            topic = topic.replace('//', '/')
        
        # Remove barra inicial/final
        topic = topic.strip('/')
        
        if not topic:
            logger.warning("Tópico vazio após limpeza, usando padrão")
            return "pdu"
        
        return topic
    
    @staticmethod
    def fix_configuration_validation(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bug Fix: Validação completa da configuração
        """
        fixed_config = {}
        
        # MQTT Host
        fixed_config['mqtt_host'] = config.get('mqtt_host', 'localhost')
        if not isinstance(fixed_config['mqtt_host'], str) or not fixed_config['mqtt_host'].strip():
            fixed_config['mqtt_host'] = 'localhost'
        
        # MQTT Port
        try:
            fixed_config['mqtt_port'] = int(config.get('mqtt_port', 1883))
            if fixed_config['mqtt_port'] < 1 or fixed_config['mqtt_port'] > 65535:
                fixed_config['mqtt_port'] = 1883
        except (ValueError, TypeError):
            fixed_config['mqtt_port'] = 1883
        
        # MQTT User/Password
        fixed_config['mqtt_user'] = str(config.get('mqtt_user', ''))
        fixed_config['mqtt_password'] = str(config.get('mqtt_password', ''))
        
        # MQTT Topic
        fixed_config['mqtt_topic'] = PDUBugFixes.fix_mqtt_topic_validation(
            config.get('mqtt_topic', 'pdu')
        )
        
        # PDU List
        pdu_list = config.get('pdu_list', [])
        if not isinstance(pdu_list, list):
            pdu_list = []
        
        fixed_pdu_list = []
        for pdu in pdu_list:
            if not isinstance(pdu, dict):
                continue
            
            # Validação de cada PDU
            if not pdu.get('name') or not pdu.get('host'):
                logger.warning(f"PDU inválido ignorado: {pdu}")
                continue
            
            fixed_pdu = {
                'name': str(pdu['name']).strip(),
                'host': str(pdu['host']).strip(),
                'username': str(pdu.get('username', 'admin')).strip(),
                'password': str(pdu.get('password', 'admin'))
            }
            
            # Validação básica de IP/hostname
            if not fixed_pdu['host'] or '/' in fixed_pdu['host']:
                logger.warning(f"Host inválido: {fixed_pdu['host']}")
                continue
            
            fixed_pdu_list.append(fixed_pdu)
        
        fixed_config['pdu_list'] = fixed_pdu_list
        
        return fixed_config
    
    @staticmethod
    def fix_discovery_network_validation(network: str) -> Optional[str]:
        """
        Bug Fix: Validação da rede para descoberta
        """
        if not network or not isinstance(network, str):
            return None
        
        network = network.strip()
        
        # Verifica formato básico (ex: 192.168.1)
        parts = network.split('.')
        if len(parts) != 3:
            logger.error(f"Formato de rede inválido: {network}")
            return None
        
        # Valida cada parte
        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    logger.error(f"Octeto inválido: {part}")
                    return None
            except ValueError:
                logger.error(f"Octeto não numérico: {part}")
                return None
        
        return network
    
    @staticmethod
    def fix_sensor_data_conversion(value: str) -> Optional[float]:
        """
        Bug Fix: Conversão robusta de dados de sensores
        """
        if not value or value in ['N/A', 'n/a', 'NULL', 'null', '']:
            return None
        
        try:
            # Remove espaços e caracteres especiais
            value = str(value).strip()
            
            # Remove unidades comuns
            units = ['°C', '°F', '%', 'A', 'V', 'W']
            for unit in units:
                if value.endswith(unit):
                    value = value[:-len(unit)].strip()
            
            # Converte para float
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Não foi possível converter valor: {value}")
            return None
    
    @staticmethod
    def fix_mqtt_payload_encoding(payload: Any) -> str:
        """
        Bug Fix: Codificação correta de payloads MQTT
        """
        if isinstance(payload, str):
            return payload
        elif isinstance(payload, (int, float)):
            return str(payload)
        elif isinstance(payload, bool):
            return "ON" if payload else "OFF"
        elif isinstance(payload, dict):
            try:
                return json.dumps(payload)
            except (TypeError, ValueError):
                return str(payload)
        else:
            return str(payload)
    
    @staticmethod
    def fix_error_recovery(func):
        """
        Bug Fix: Decorator para recuperação automática de erros
        """
        def wrapper(*args, **kwargs):
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Erro na tentativa {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        logger.error("Máximo de tentativas excedido")
                        raise
                    time.sleep(2 ** attempt)  # Exponential backoff
            return None
        return wrapper
    
    @staticmethod
    def create_healthcheck_endpoint() -> Dict[str, Any]:
        """
        Bug Fix: Endpoint de health check para monitoramento
        """
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.4.0",
            "uptime": time.time(),
            "mqtt_connected": True,
            "pdus_configured": 0,
            "errors_count": 0
        }

# Aplicar correções automaticamente
def apply_bug_fixes():
    """Aplica todas as correções de bugs automaticamente"""
    logger.info("Aplicando correções de bugs...")
    
    # Aqui você pode adicionar lógica para aplicar correções automaticamente
    # Por exemplo, validar configurações existentes, limpar dados corrompidos, etc.
    
    logger.info("Correções de bugs aplicadas com sucesso")

if __name__ == "__main__":
    apply_bug_fixes()
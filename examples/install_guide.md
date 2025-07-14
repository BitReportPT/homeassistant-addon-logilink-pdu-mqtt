# 🚀 Guia Completo de Instalação - PDU MQTT Bridge

## 📋 Índice
1. [Instalação do Add-on](#1-instalação-do-add-on)
2. [Configuração MQTT](#2-configuração-mqtt)
3. [Configuração das PDUs](#3-configuração-das-pdus)
4. [Configuração Home Assistant](#4-configuração-home-assistant)
5. [Dashboards Lovelace](#5-dashboards-lovelace)
6. [Automações](#6-automações)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Instalação do Add-on

### 1.1 Adicionar Repositório
1. Vai a **Settings** → **Add-ons** → **Add-on Store**
2. Clica nos **3 pontos** (⋮) no canto superior direito
3. Seleciona **Repositories**
4. Adiciona: `https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt`

### 1.2 Instalar Add-on
1. Procura por **"LogiLink & Intellinet PDU MQTT Bridge"**
2. Clica **Install**
3. Aguarda a instalação completar

---

## 2. Configuração MQTT

### 2.1 Verificar Broker MQTT
Certifica-te que tens um broker MQTT configurado:
- **Mosquitto Add-on** (recomendado)
- **MQTT Broker** no Home Assistant
- **Broker externo** (se aplicável)

### 2.2 Configurar Add-on
1. Vai a **Settings** → **Add-ons** → **LogiLink & Intellinet PDU MQTT Bridge**
2. Clica **Configuration**
3. Configura:

```yaml
mqtt_host: "localhost"  # ou IP do teu broker
mqtt_port: 1883
mqtt_user: "ha"         # teu user MQTT
mqtt_password: "pass"   # tua password MQTT
mqtt_topic: "pdu"
auto_discovery: true    # para descobrir PDUs automaticamente
discovery_network: "192.168.1"  # tua rede
pdu_list: []           # vazio se usar auto-discovery
```

---

## 3. Configuração das PDUs

### 3.1 Auto-Discovery (Recomendado)
1. Ativa `auto_discovery: true`
2. Define `discovery_network` para a tua rede
3. Inicia o add-on
4. Verifica os logs para ver PDUs descobertas

### 3.2 Configuração Manual
Se preferires configurar manualmente:

```yaml
auto_discovery: false
pdu_list:
  - name: "rack_01"
    host: "192.168.1.112"
    username: "admin"
    password: "admin"
  - name: "rack_02"
    host: "192.168.1.113"
    username: "admin"
    password: "admin"
```

---

## 4. Configuração Home Assistant

### 4.1 Adicionar ao configuration.yaml
Adiciona isto ao teu `configuration.yaml`:

```yaml
# MQTT Configuration
mqtt:
  broker: localhost
  port: 1883
  username: ha
  password: pass
  discovery: true
  discovery_prefix: homeassistant

# PDU Switches (exemplo para rack_01)
mqtt:
  switch:
    - name: "Rack 01 - Tomada 1"
      state_topic: "pdu/rack_01/outlet1"
      command_topic: "pdu/rack_01/outlet1/set"
      payload_on: "on"
      payload_off: "off"
      retain: true
      icon: mdi:power-plug

# PDU Sensors
mqtt:
  sensor:
    - name: "Rack 01 - Temperatura"
      state_topic: "pdu/rack_01/temperature"
      unit_of_measurement: "°C"
      device_class: temperature
```

### 4.2 Reiniciar Home Assistant
1. Vai a **Settings** → **System**
2. Clica **Restart**

---

## 5. Dashboards Lovelace

### 5.1 Dashboard Básico
1. Vai a **Settings** → **Dashboards**
2. Clica **+ Add Dashboard**
3. Nome: "PDU Control"
4. Clica **Create**

### 5.2 Adicionar Cards
Adiciona estes cards ao teu dashboard:

#### Card de Controlo de Tomadas
```yaml
type: entities
title: "Rack 01 - Controlo de Tomadas"
entities:
  - entity: switch.rack_01_tomada_1
    name: "Servidor 1"
  - entity: switch.rack_01_tomada_2
    name: "Servidor 2"
  - entity: switch.rack_01_tomada_3
    name: "Switch"
  - entity: switch.rack_01_tomada_4
    name: "Router"
```

#### Card de Sensores
```yaml
type: entities
title: "Rack 01 - Monitorização"
entities:
  - entity: sensor.rack_01_temperatura
    name: "Temperatura"
  - entity: sensor.rack_01_humidade
    name: "Humidade"
  - entity: sensor.rack_01_corrente
    name: "Corrente"
```

### 5.3 Dashboard Avançado
Para um dashboard mais avançado, instala estas custom cards:

1. **HACS** → **Frontend** → **Custom Cards**
2. Instala:
   - **Button Card**
   - **Mini Graph Card**
   - **Stack In Card**
   - **ApexCharts Card**

3. Usa o ficheiro `advanced_dashboard.yaml` como referência

---

## 6. Automações

### 6.1 Automação de Temperatura
```yaml
automation:
  - alias: "Alerta Temperatura Alta"
    trigger:
      platform: numeric_state
      entity_id: sensor.rack_01_temperatura
      above: 35
    action:
      - service: notify.mobile_app
        data:
          title: "Alerta PDU"
          message: "Temperatura alta: {{ states('sensor.rack_01_temperatura') }}°C"
      - service: switch.turn_off
        target:
          entity_id: 
            - switch.rack_01_tomada_1
            - switch.rack_01_tomada_2
```

### 6.2 Automação de Status
```yaml
automation:
  - alias: "PDU Offline"
    trigger:
      platform: state
      entity_id: binary_sensor.rack_01_status
      to: "off"
    action:
      - service: notify.mobile_app
        data:
          title: "Alerta PDU"
          message: "PDU Rack 01 ficou offline!"
```

---

## 7. Troubleshooting

### 7.1 Verificar Logs
1. Vai a **Settings** → **Add-ons** → **LogiLink & Intellinet PDU MQTT Bridge**
2. Clica **Logs**
3. Procura por erros

### 7.2 Testar Conectividade
```bash
# Testar PDU
curl -u admin:admin http://192.168.1.112/status.xml

# Testar MQTT
mosquitto_pub -h localhost -t "pdu/test" -m "test"
```

### 7.3 Problemas Comuns

#### Add-on não inicia
- Verifica configuração MQTT
- Verifica se PDUs estão acessíveis
- Verifica logs

#### Não aparecem entidades
- Verifica tópicos MQTT
- Reinicia Home Assistant
- Verifica configuração MQTT no HA

#### PDUs não descobertas
- Verifica rede
- Verifica credenciais
- Usa configuração manual

---

## 🎯 Próximos Passos

1. **Testa o add-on** com uma PDU
2. **Configura o dashboard** básico
3. **Adiciona automações** conforme necessário
4. **Instala custom cards** para dashboard avançado
5. **Monitoriza logs** para otimizações

---

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt/issues)
- **Documentação**: [README.md](../README.md)
- **Exemplos**: [Pasta examples](../examples/) 
# Guia de Verificação - LogiLink PDU MQTT Bridge

## 🔍 Verificar se está tudo a funcionar

### 1. Verificar se o Add-on está a correr

No Home Assistant:
1. Ir a **Settings** → **Add-ons**
2. Clicar em **LogiLink PDU MQTT Bridge**
3. Verificar se o status é **Running**
4. Ver os logs - devem mostrar:
   ```
   Starting PDU MQTT Bridge v1.1.5
   Connected to MQTT broker
   Subscribed to pdu/rack_01/outlet1/set
   ...
   Status published for PDU rack_01 - 8 outlets
   ```

### 2. Verificar entidades no Home Assistant

Ir a **Developer Tools** → **States** e procurar por:
- `switch.rack_01_outlet1` até `switch.rack_01_outlet8`
- `sensor.rack_01_temperature`
- `sensor.rack_01_humidity`
- `sensor.rack_01_current`

### 3. Teste via Dashboard

1. Adicionar o dashboard completo (copiar de `examples/complete_dashboard.yaml`)
2. Só testar outlets 1 e 8!
3. Clicar nos botões deve ligar/desligar as tomadas

### 4. Teste via MQTT (linha de comando)

```bash
# Verificar estado atual
mosquitto_sub -h 192.168.1.241 -u mqttuser -P mqttpass -t "pdu/rack_01/outlet1/state" -C 1

# Desligar outlet 1
mosquitto_pub -h 192.168.1.241 -u mqttuser -P mqttpass -t "pdu/rack_01/outlet1/set" -m "OFF"

# Ligar outlet 1
mosquitto_pub -h 192.168.1.241 -u mqttuser -P mqttpass -t "pdu/rack_01/outlet1/set" -m "ON"
```

### 5. Teste via MQTT Explorer

1. Instalar MQTT Explorer
2. Conectar a 192.168.1.241:1883 com mqttuser/mqttpass
3. Navegar até `pdu/rack_01/`
4. Ver todos os tópicos disponíveis
5. Publicar "ON" ou "OFF" em `pdu/rack_01/outlet1/set`

### 6. Verificar funcionalidades avançadas

```bash
# Ver configuração de rede atual
mosquitto_sub -h 192.168.1.241 -u mqttuser -P mqttpass -t "pdu/rack_01/network/config" -C 1

# Ver limites de temperatura
mosquitto_sub -h 192.168.1.241 -u mqttuser -P mqttpass -t "pdu/rack_01/threshold/temperature" -C 1

# Configurar nome do outlet 1
mosquitto_pub -h 192.168.1.241 -u mqttuser -P mqttpass \
  -t "pdu/rack_01/outlet/1/config/set" \
  -m '{"name": "Servidor Principal", "delay_on": "10", "delay_off": "5"}'
```

## ❌ Problemas Comuns

### Add-on não aparece no Home Assistant
1. Verificar estrutura: ficheiros devem estar em `pdu_mqtt/`
2. Incrementar versão em todos os ficheiros
3. Remover e adicionar repositório novamente

### MQTT não conecta
1. Verificar credenciais MQTT
2. Verificar se o broker está acessível
3. Ver logs do add-on

### Outlets não respondem
1. Verificar se o PDU está acessível via HTTP (192.168.1.215)
2. Verificar credenciais do PDU (admin/admin)
3. Ver logs para erros HTTP

### Entidades não aparecem no HA
1. Verificar se MQTT Discovery está ativo
2. Reiniciar Home Assistant
3. Verificar em MQTT Explorer se os tópicos discovery foram publicados

## ✅ Checklist de Funcionalidades

- [ ] Ligar/desligar outlets 1 e 8
- [ ] Ver temperatura, humidade e corrente
- [ ] Dashboard mostra estados corretos
- [ ] Comandos MQTT funcionam
- [ ] Configurar nome de outlet funciona
- [ ] Definir limites de temperatura funciona
- [ ] Logs mostram atualizações a cada 30 segundos

## 🚀 Próximos Passos

Se tudo estiver a funcionar:
1. Configurar automações no Home Assistant
2. Adicionar alertas de temperatura
3. Criar scripts para sequências de reinicialização
4. Integrar com outros sistemas via MQTT 
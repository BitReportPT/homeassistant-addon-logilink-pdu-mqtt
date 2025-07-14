# LogiLink PDU MQTT Bridge

Home Assistant add-on para monitorizar e controlar PDU LogiLink PDU8P01 via MQTT.

## Funcionalidades

- **Monitorização**: Estado das tomadas 1 e 8 em tempo real
- **Controlo**: Ligar/desligar tomadas via MQTT
- **Power Monitoring**: Monitorização de consumo de energia
- **Home Assistant Integration**: Discovery automático de entidades

## Instalação

1. Adicionar este repositório ao Home Assistant:
   ```
   https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt
   ```

2. Instalar o add-on "LogiLink PDU MQTT Bridge"

3. Configurar:
   - **MQTT Host**: IP do teu broker MQTT (ex: `localhost`)
   - **MQTT Port**: Porta MQTT (ex: `1883`)
   - **MQTT User**: Usuário MQTT (opcional)
   - **MQTT Password**: Password MQTT (opcional)
   - **PDU List**: Configuração da PDU
     - **Name**: Nome da PDU (ex: `rack_01`)
     - **Host**: IP da PDU (ex: `192.168.1.215`)
     - **Username**: Usuário da PDU (ex: `admin`)
     - **Password**: Password da PDU (ex: `admin`)

4. Iniciar o add-on

## Tópicos MQTT

### Estado
- `pdu/outlet_1/state` - Estado da tomada 1 (ON/OFF)
- `pdu/outlet_8/state` - Estado da tomada 8 (ON/OFF)
- `pdu/outlet_1/power` - Consumo de energia da tomada 1 (W)
- `pdu/outlet_8/power` - Consumo de energia da tomada 8 (W)

### Controlo
- `pdu/outlet_1/set` - Comando para tomada 1 (ON/OFF)
- `pdu/outlet_8/set` - Comando para tomada 8 (ON/OFF)

## Home Assistant

O add-on publica automaticamente mensagens de discovery para o Home Assistant. As entidades aparecerão automaticamente na interface:

- **Switches**: `PDU Outlet 1` e `PDU Outlet 8`
- **Sensors**: `PDU Outlet 1 Power` e `PDU Outlet 8 Power`

## Configuração MQTT

Certifica-te de que o broker MQTT está configurado no Home Assistant:

```yaml
# configuration.yaml
mqtt:
  broker: localhost
  port: 1883
  # username: mqttuser  # se necessário
  # password: mqttpass  # se necessário
```

## Troubleshooting

### Add-on não aparece
- Verifica se o repositório foi adicionado corretamente
- Refresca a lista de add-ons
- Reinicia o Home Assistant

### Erro de conexão MQTT
- Verifica se o broker MQTT está a funcionar
- Confirma as credenciais MQTT
- Verifica se a porta está correta

### "No PDUs configured"
- Verifica a configuração da PDU no add-on
- Confirma se o IP da PDU está correto
- Testa a conectividade com a PDU

### Logs
Verifica os logs do add-on para mais detalhes sobre erros.

## Suporte

Para suporte, abrir uma issue no GitHub ou contactar BitReport.pt.

## Licença

MIT License
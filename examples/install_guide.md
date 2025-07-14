# Guia de Instalação - LogiLink PDU MQTT Bridge

## Pré-requisitos

- Home Assistant (versão 2024+)
- Broker MQTT configurado (Mosquitto add-on recomendado)
- PDU LogiLink PDU8P01 acessível via rede

## Passo 1: Configurar MQTT

1. Instalar o add-on "Mosquitto broker" no Home Assistant
2. Configurar credenciais MQTT se necessário
3. Anotar o IP e porta do broker MQTT

## Passo 2: Adicionar o Repositório

1. Ir para **Settings → Add-ons → Add-on Store**
2. Clicar nos 3 pontos no canto superior direito
3. Selecionar **Repositories**
4. Adicionar: `https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt`
5. Clicar **Add**

## Passo 3: Instalar o Add-on

1. Procurar por **"LogiLink PDU MQTT Bridge"** na lista
2. Clicar **Install**
3. Aguardar a instalação completar

## Passo 4: Configurar o Add-on

1. Clicar **Start** para iniciar o add-on
2. Ir para **Configuration** tab
3. Configurar:

```yaml
mqtt_host: localhost
mqtt_port: 1883
mqtt_user: ""  # deixar vazio se não usar autenticação
mqtt_password: ""  # deixar vazio se não usar autenticação
pdu_list:
  - name: "rack_01"
    host: "192.168.1.215"  # IP da tua PDU
    username: "admin"
    password: "admin"
```

4. Clicar **Save**
5. Reiniciar o add-on

## Passo 5: Verificar Funcionamento

1. Verificar os logs do add-on
2. Procurar por mensagens como:
   - "Connected to MQTT broker"
   - "Connected to PDU at 192.168.1.215"
   - "Status published"

## Passo 6: Configurar Home Assistant

O add-on publica automaticamente as entidades via MQTT Discovery. As entidades devem aparecer automaticamente:

- **Switches**: `PDU Outlet 1` e `PDU Outlet 8`
- **Sensors**: `PDU Outlet 1 Power` e `PDU Outlet 8 Power`

## Troubleshooting

### Add-on não aparece
- Verificar se o repositório foi adicionado corretamente
- Refrescar a lista de add-ons
- Reiniciar o Home Assistant

### Erro de conexão MQTT
- Verificar se o Mosquitto broker está a funcionar
- Confirmar credenciais MQTT
- Verificar se a porta está correta

### "No PDUs configured"
- Verificar configuração da PDU
- Confirmar IP da PDU
- Testar conectividade com a PDU

### Logs
Verificar logs do add-on para mais detalhes sobre erros. 
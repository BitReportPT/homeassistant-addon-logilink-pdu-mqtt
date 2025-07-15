# 🔍 PDU MQTT Bridge - Descoberta Visual

## Funcionalidades Novas - Versão 1.4.0

### ✨ Interface Visual de Descoberta
O addon agora inclui uma **interface web moderna** para descobrir e configurar PDUs automaticamente, eliminando a necessidade de editar configurações YAML manualmente.

### 🔧 Correções de Bugs Implementadas
- **Parsing XML mais robusto** para diferentes formatos de PDU
- **Conexão com retry automático** e timeout melhorado
- **Validação de estado das tomadas** mais rigorosa
- **Validação de tópicos MQTT** e limpeza automática
- **Validação completa da configuração** com valores padrão
- **Conversão robusta de dados de sensores**
- **Codificação correta de payloads MQTT**
- **Recuperação automática de erros** com exponential backoff

## 🚀 Como Usar a Interface Visual

### 1. Acesso à Interface
Após instalar o addon, aceda à interface web em:
```
http://[IP_DO_HOME_ASSISTANT]:8099
```

### 2. Descoberta de PDUs
1. **Configure a rede** - Defina a gama de IPs para procurar (ex: 192.168.1)
2. **Defina o range** - Configure IP inicial e final (ex: 1 a 254)
3. **Clique em "Procurar PDUs"** - A interface irá procurar automaticamente
4. **Visualize o progresso** - Barra de progresso em tempo real

### 3. Configuração dos PDUs
1. **Teste credenciais** - Clique em "Testar" para cada PDU encontrado
2. **Insira credenciais** - Username e password (padrão: admin/admin)
3. **Visualize informações** - Status das tomadas, temperatura, etc.
4. **Adicione à configuração** - Clique em "Adicionar"

### 4. Guardar Configuração
1. **Verifique PDUs configurados** - Lista na parte inferior
2. **Clique em "Guardar Configuração"** - Salva automaticamente
3. **Reinicie o addon** - Para aplicar as novas configurações

## 🎯 Funcionalidades da Interface

### Descoberta Automática
- **Scan de rede completo** com progresso em tempo real
- **Detecção de diferentes tipos de PDU** (LogiLink, Intellinet, etc.)
- **Teste de endpoints múltiplos** para maior compatibilidade
- **Verificação de autenticação** necessária

### Teste de Credenciais
- **Teste em tempo real** de username/password
- **Validação de conectividade** antes de adicionar
- **Informações detalhadas** sobre o dispositivo
- **Status das tomadas** visualizado graficamente

### Configuração Visual
- **Interface amigável** sem necessidade de editar YAML
- **Validação automática** de configurações
- **Preview das configurações** antes de salvar
- **Gestão de múltiplos PDUs** numa só interface

## 📊 Dashboard Visual Melhorado

### Novas Visualizações
- **Gráficos de temperatura** com alertas visuais
- **Indicadores de corrente** em tempo real
- **Status das tomadas** com cores indicativas
- **Controlo por grupos** de equipamentos

### Alertas Inteligentes
- **Alertas de temperatura** configuráveis
- **Monitoramento de corrente** com limiares
- **Notificações visuais** no dashboard
- **Histórico de alertas** para análise

### Controlo Avançado
- **Botões de ação rápida** para cenários comuns
- **Controlo por grupos** (servidores, rede, etc.)
- **Programações automáticas** com interface visual
- **Modo emergência** para desligar tudo

## 🔧 Configuração Avançada

### Opções do Addon
```yaml
# Configurações da descoberta visual
auto_discovery: true
discovery_network: "192.168.1"
discovery_range_start: 1
discovery_range_end: 254

# Interface web
webui: http://[HOST]:[PORT:8099]
```

### Configuração Home Assistant
Adicione ao `configuration.yaml`:

```yaml
# Sensores adicionais
sensor:
  - platform: template
    sensors:
      pdu_mqtt_addon_status:
        friendly_name: "PDU MQTT Addon Status"
        value_template: "{{ states('sensor.supervisor_addons') | selectattr('slug', 'eq', 'local_pdu_mqtt') | map(attribute='state') | first | default('unknown') }}"
        
      rack_01_total_power:
        friendly_name: "Total Power"
        unit_of_measurement: "W"
        value_template: "{{ (states('sensor.rack_01_current') | float * 230) | round(2) }}"

# Alertas configuráveis
alert:
  pdu_high_temperature:
    name: "PDU High Temperature"
    entity_id: sensor.rack_01_temperature
    state: "on"
    repeat: 5
    can_acknowledge: true
    message: "PDU temperature is above threshold"

# Scripts para controlo por grupos
script:
  pdu_turn_on_servers:
    alias: "Turn On Servers"
    sequence:
      - service: switch.turn_on
        target:
          entity_id:
            - switch.rack_01_outlet1
            - switch.rack_01_outlet2
```

## 🐛 Problemas Resolvidos

### Bug Fixes Implementados
1. **Parsing XML inconsistente** - Agora suporta diferentes formatos
2. **Timeouts de conexão** - Retry automático com backoff
3. **Estados de tomadas inválidos** - Validação rigorosa
4. **Tópicos MQTT problemáticos** - Limpeza automática
5. **Configurações inválidas** - Validação completa
6. **Dados de sensores corrompidos** - Conversão robusta
7. **Payloads MQTT mal formados** - Codificação correta
8. **Falhas de recuperação** - Sistema de retry inteligente

### Melhorias de Estabilidade
- **Conexões mais estáveis** com retry automático
- **Validação de dados** em todos os pontos
- **Recuperação automática** de erros temporários
- **Logging melhorado** para debugging
- **Health checks** para monitoramento

## 🚀 Instalação e Atualização

### Instalação Nova
1. Adicione este repositório ao HACS
2. Instale o addon "PDU MQTT Bridge"
3. Configure as opções básicas
4. Aceda à interface web para descoberta
5. Configure os PDUs encontrados
6. Adicione o dashboard visual

### Atualização da Versão Anterior
1. Faça backup da configuração atual
2. Atualize o addon através do HACS
3. Reinicie o addon
4. Aceda à interface web para reconfigurar
5. Teste as funcionalidades

## 📋 Requisitos

### Dependências
- Home Assistant 2024.1+
- MQTT Broker configurado
- PDUs compatíveis na rede
- Acesso à rede onde estão os PDUs

### PDUs Suportados
- LogiLink PDU8P01
- Intellinet 163682
- Qualquer PDU com interface HTTP/XML similar

## 🛠️ Troubleshooting

### Problemas Comuns

#### Interface Web Não Carrega
```bash
# Verifique se o addon está running
# Aceda aos logs do addon
# Confirme que a porta 8099 está acessível
```

#### PDUs Não Descobertos
```bash
# Verifique conectividade de rede
# Confirme que os PDUs estão na rede especificada
# Teste conectividade manual: curl -u admin:admin http://IP/status.xml
```

#### Configuração Não Salva
```bash
# Verifique permissões de escrita
# Confirme que o addon tem acesso a /data/
# Reinicie o addon após mudanças
```

### Logs de Debug
Para ativar logs detalhados:
```yaml
log_level: DEBUG
```

## 📈 Monitoramento

### Métricas Disponíveis
- **Status de conectividade** de cada PDU
- **Temperatura e humidade** em tempo real
- **Consumo de corrente** por PDU
- **Estado das tomadas** individual
- **Uptime do addon** e estatísticas

### Dashboard de Monitoramento
Use o dashboard `examples/visual_dashboard.yaml` para uma interface completa de monitoramento.

## 🔄 Atualizações Futuras

### Funcionalidades Planejadas
- **Descoberta automática periódica** de novos PDUs
- **Integração com sistemas de monitoring** (Grafana, etc.)
- **Controlo por voz** via assistentes
- **Agendamento avançado** de tarefas
- **Relatórios de consumo** energético

### Feedback
Para reportar bugs ou sugerir melhorias:
- [GitHub Issues](https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt/issues)
- [Discussões](https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt/discussions)

---

## 📞 Suporte

Para suporte técnico:
- **Email**: support@bitreport.pt
- **GitHub**: [BitReportPT](https://github.com/BitReportPT)
- **Documentação**: [Wiki do Projeto](https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt/wiki)

**Versão**: 1.4.0  
**Mantido por**: BitReport.pt  
**Licença**: MIT
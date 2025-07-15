# Changelog - Versão 1.4.0

## 🚀 Novas Funcionalidades

### ✨ Interface Visual de Descoberta
- **Interface web moderna** para descobrir PDUs automaticamente
- **Scan de rede visual** com progresso em tempo real  
- **Teste de credenciais** integrado na interface
- **Configuração visual** sem necessidade de editar YAML
- **Gestão de múltiplos PDUs** numa única interface
- **Visualização do estado das tomadas** em tempo real

### 🔧 Correções de Bugs Críticas

#### 1. Parsing XML Melhorado
- **Problema**: XML parsing inconsistente com diferentes formatos de PDU
- **Solução**: Sistema robusto que suporta variações de formato
- **Benefício**: Compatibilidade com mais modelos de PDU

#### 2. Conexão com Retry Automático
- **Problema**: Timeouts frequentes e falhas de conexão
- **Solução**: Sistema de retry com exponential backoff
- **Benefício**: Conexões mais estáveis e confiáveis

#### 3. Validação de Estados das Tomadas
- **Problema**: Estados inválidos causavam erros no MQTT
- **Solução**: Validação rigorosa com normalização automática
- **Benefício**: Controlo mais preciso das tomadas

#### 4. Limpeza de Tópicos MQTT
- **Problema**: Tópicos mal formados causavam problemas
- **Solução**: Validação e limpeza automática de tópicos
- **Benefício**: Comunicação MQTT mais estável

#### 5. Validação de Configuração
- **Problema**: Configurações inválidas causavam crashes
- **Solução**: Validação completa com valores padrão
- **Benefício**: Startup mais robusto do addon

#### 6. Conversão de Dados de Sensores
- **Problema**: Dados corrompidos de temperatura/humidade
- **Solução**: Conversão robusta com tratamento de erros
- **Benefício**: Dados mais confiáveis no dashboard

#### 7. Codificação de Payloads MQTT
- **Problema**: Payloads mal formados
- **Solução**: Codificação correta para todos os tipos de dados
- **Benefício**: Comunicação MQTT sem erros

#### 8. Recuperação Automática de Erros
- **Problema**: Falhas permanentes após erros temporários
- **Solução**: Sistema de recuperação com retry inteligente
- **Benefício**: Maior disponibilidade do serviço

## 🎯 Melhorias de Interface

### Dashboard Visual Avançado
- **Gráficos de temperatura** com alertas visuais
- **Indicadores de corrente** em tempo real
- **Status das tomadas** com cores indicativas
- **Controlo por grupos** de equipamentos
- **Alertas inteligentes** configuráveis
- **Histórico de alertas** para análise

### Controlo Avançado
- **Botões de ação rápida** para cenários comuns
- **Controlo por grupos** (servidores, rede, etc.)
- **Programações automáticas** com interface visual
- **Modo emergência** para desligar tudo
- **Scripts personalizados** para automação

## 🔧 Configuração Simplificada

### Opções Novas do Addon
```yaml
# Descoberta visual ativada por padrão
auto_discovery: true
discovery_network: "192.168.1"
discovery_range_start: 1
discovery_range_end: 254

# Interface web integrada
webui: http://[HOST]:[PORT:8099]
ports:
  8099/tcp: 8099
```

### Dependências Atualizadas
- `flask==2.3.3` - Para interface web
- `werkzeug==2.3.7` - Backend web robusto
- Mantidas dependências existentes

## 📊 Monitoramento Melhorado

### Métricas Novas
- **Status de conectividade** de cada PDU
- **Uptime do addon** e estatísticas
- **Contador de erros** para debugging
- **Health checks** automáticos

### Logging Avançado
- **Logs estruturados** para melhor debugging
- **Níveis de log** configuráveis
- **Rotação automática** de logs
- **Métricas de performance**

## 🚀 Instalação e Migração

### Para Novos Usuários
1. Instale o addon via HACS
2. Configure MQTT básico
3. Aceda à interface web: `http://[IP]:8099`
4. Use a descoberta visual para configurar PDUs
5. Adicione o dashboard visual

### Para Usuários Existentes
1. Faça backup da configuração atual
2. Atualize o addon
3. Reinicie o addon
4. Aceda à interface web para reconfigurar
5. Teste as novas funcionalidades

## 🐛 Problemas Conhecidos Resolvidos

### ✅ Resolvidos nesta versão
- XML parsing falhava com alguns PDUs
- Timeouts constantes em redes lentas
- Estados de tomadas inconsistentes
- Tópicos MQTT mal formados
- Configurações inválidas causavam crashes
- Dados de sensores corrompidos
- Payloads MQTT incorretos
- Falhas de recuperação após erros

### ⚠️ Limitações Conhecidas
- Interface web requer porta 8099 disponível
- Descoberta pode ser lenta em redes grandes
- Alguns PDUs podem precisar configuração manual
- Requer reinício do addon após mudanças

## 📋 Testes Realizados

### Compatibilidade
- ✅ LogiLink PDU8P01
- ✅ Intellinet 163682
- ✅ Home Assistant 2024.1+
- ✅ MQTT Brokers: Mosquitto, HiveMQ
- ✅ Redes: IPv4 subnets padrão

### Testes de Stress
- ✅ Descoberta em redes /24 completas
- ✅ Múltiplos PDUs simultâneos
- ✅ Reconexão após falhas de rede
- ✅ Uso contínuo por 48+ horas

### Testes de Segurança
- ✅ Validação de inputs
- ✅ Sanitização de dados
- ✅ Proteção contra injection
- ✅ Timeouts apropriados

## 🔄 Próximos Passos

### Funcionalidades Planejadas v1.5.0
- **Descoberta automática periódica** de novos PDUs
- **Integração com Grafana** para métricas
- **Controlo por voz** via assistentes
- **Agendamento avançado** de tarefas
- **Relatórios de consumo** energético

### Melhorias Técnicas
- **API REST** para integração externa
- **WebSocket** para updates em tempo real
- **Backup/restore** de configurações
- **Cluster support** para alta disponibilidade

## 📞 Suporte e Feedback

### Reportar Problemas
- [GitHub Issues](https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt/issues)
- [Discussões](https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt/discussions)

### Contribuições
- Fork do projeto no GitHub
- Submeta Pull Requests
- Reporte bugs e sugestões
- Contribua com documentação

---

**Data de Lançamento**: 2024-01-15  
**Versão**: 1.4.0  
**Mantido por**: BitReport.pt  
**Licença**: MIT

### Agradecimentos
Obrigado à comunidade Home Assistant pelo feedback e sugestões que tornaram esta versão possível!
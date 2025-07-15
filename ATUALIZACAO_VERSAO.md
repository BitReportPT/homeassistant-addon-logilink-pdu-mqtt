# 🔄 Actualização da Versão para 1.4.0

## 📋 Problema Reportado
O Home Assistant ainda mostra "Versão actual: 1.3.4" em vez de "1.4.0".

## ✅ Ficheiros Actualizados

### 1. Ficheiros de Versão Principais
- ✅ `version.json` → `"version": "1.4.0"`
- ✅ `pdu_mqtt/config.yaml` → `version: "1.4.0"`
- ✅ `pdu_mqtt/version.txt` → `1.4.0` (novo)
- ✅ `pdu_mqtt/run.py` → `"Starting PDU MQTT Bridge v1.4.0"`

### 2. Ficheiros de Documentação
- ✅ `README.md` → Adicionado changelog v1.4.0
- ✅ `pdu_mqtt/CHANGELOG.md` → Adicionada entrada [1.4.0]
- ✅ `pdu_mqtt/bug_fixes.py` → User-Agent atualizado

## 🔧 Passos para Resolução

### 1. **Reiniciar o Add-on**
```bash
# No Home Assistant:
# 1. Ir a Settings → Add-ons
# 2. Encontrar "LogiLink & Intellinet PDU MQTT Bridge"
# 3. Clicar em "Restart"
```

### 2. **Limpar Cache do Home Assistant**
```bash
# No Home Assistant:
# 1. Ir a Settings → System → Storage
# 2. Clicar em "Clear Cache"
# 3. Reiniciar o Home Assistant
```

### 3. **Reinstalar o Add-on (se necessário)**
```bash
# No Home Assistant:
# 1. Ir a Settings → Add-ons
# 2. Encontrar o add-on
# 3. Clicar em "Uninstall"
# 4. Ir a Add-on Store → Repositories
# 5. Atualizar o repositório
# 6. Reinstalar o add-on
```

### 4. **Verificar Repositório HACS**
```bash
# No HACS:
# 1. Ir a HACS → Integrations
# 2. Encontrar o repositório
# 3. Clicar nos três pontos (...)
# 4. Selecionar "Redownload"
# 5. Aguardar sincronização
```

### 5. **Atualizar Repositório Git**
```bash
# Se estiver a usar repositório próprio:
git add .
git commit -m "Update to version 1.4.0"
git push origin main
```

## 🔍 Verificação da Versão

### Locais onde a versão deve aparecer como 1.4.0:
1. **Interface do Add-on**: Settings → Add-ons → PDU MQTT Bridge
2. **Logs do Add-on**: "Starting PDU MQTT Bridge v1.4.0"
3. **Registo de Alterações**: Link no add-on deve mostrar versão 1.4.0
4. **Interface Web**: http://[IP]:8099 (footer da página)

### Comandos para Verificar:
```bash
# Verificar versão nos ficheiros
cat version.json
cat pdu_mqtt/config.yaml | grep version
cat pdu_mqtt/version.txt

# Verificar logs do add-on
# No Home Assistant: Settings → Add-ons → PDU MQTT Bridge → Logs
```

## 🐛 Possíveis Causas do Problema

### 1. **Cache do Home Assistant**
- O Home Assistant pode ter a versão anterior em cache
- **Solução**: Reiniciar o add-on e limpar cache

### 2. **Repositório Não Actualizado**
- Se estiver a usar repositório próprio, pode não estar actualizado
- **Solução**: Fazer push das alterações para o repositório

### 3. **HACS Cache**
- O HACS pode ter cache da versão anterior
- **Solução**: Redownload do repositório no HACS

### 4. **Sincronização Pendente**
- Pode haver delay na sincronização
- **Solução**: Aguardar alguns minutos e verificar novamente

## 📊 Verificação Final

### Checklist:
- [ ] Versão no `config.yaml` = 1.4.0
- [ ] Versão no `version.json` = 1.4.0
- [ ] Add-on reiniciado
- [ ] Cache limpo
- [ ] Repositório actualizado
- [ ] Interface web acessível em porta 8099
- [ ] Logs mostram "v1.4.0"

### Se Ainda Mostrar 1.3.4:
1. **Verificar se o repositório correcto está a ser usado**
2. **Reinstalar completamente o add-on**
3. **Verificar se há conflitos de repositório**
4. **Contactar suporte se problema persistir**

## 🔧 Informações Técnicas

### Estrutura de Versão:
```
version.json                    # Versão principal
pdu_mqtt/config.yaml           # Versão do add-on
pdu_mqtt/version.txt           # Versão adicional
pdu_mqtt/run.py                # Versão no código
```

### Logs Esperados:
```
Starting PDU MQTT Bridge v1.4.0
PDU Discovery Web Interface
Web interface available at: http://localhost:8099
```

### URLs Importantes:
- **Interface Web**: http://[IP_HOME_ASSISTANT]:8099
- **Logs**: Settings → Add-ons → PDU MQTT Bridge → Logs
- **Configuração**: Settings → Add-ons → PDU MQTT Bridge → Configuration

## 📞 Suporte

Se o problema persistir após seguir estes passos:

1. **Verificar logs** do add-on para erros
2. **Reportar problema** com detalhes específicos
3. **Incluir informações** sobre versão do Home Assistant
4. **Mencionar passos já tentados**

---

**Versão Esperada**: 1.4.0  
**Data de Actualização**: 2024-01-15  
**Status**: ✅ Ficheiros actualizados, aguardar sincronização
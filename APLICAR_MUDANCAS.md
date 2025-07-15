# 🔄 Como Aplicar as Mudanças no Repositório GitHub

## 📋 Situação Atual
O repositório oficial `https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt` ainda tem a versão 1.3.4. As melhorias desenvolvidas (versão 1.4.0) precisam ser aplicadas.

## 🎯 Soluções Práticas

### **Opção 1: Repositório Próprio (Mais Rápido)**

#### 1. Criar Novo Repositório
```bash
# No GitHub:
# 1. Ir para https://github.com/new
# 2. Nome: homeassistant-addon-pdu-mqtt-visual
# 3. Descrição: PDU MQTT Bridge with Visual Discovery
# 4. Público
# 5. Criar repositório
```

#### 2. Copiar Ficheiros Principais
Copiar estes ficheiros para o novo repositório:

```
📁 Ficheiros a copiar:
├── repository.yaml
├── README.md (atualizado)
├── version.json
├── pdu_mqtt/
│   ├── config.yaml (versão 1.4.0)
│   ├── run.py (com web_interface)
│   ├── web_interface.py (NOVO)
│   ├── bug_fixes.py (NOVO)
│   ├── requirements.txt (atualizado)
│   ├── templates/
│   │   └── index.html (NOVO)
│   ├── CHANGELOG.md (atualizado)
│   └── (outros ficheiros existentes)
├── examples/
│   └── visual_dashboard.yaml (NOVO)
└── documentação (NOVOS)
```

#### 3. Adicionar ao Home Assistant
```yaml
# Settings → Add-ons → Add-on Store → ... → Repositories
# Adicionar URL:
https://github.com/[SEU_USERNAME]/homeassistant-addon-pdu-mqtt-visual
```

### **Opção 2: Fork do Repositório Original**

#### 1. Fazer Fork
```bash
# Ir para: https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt
# Clicar em "Fork"
# Criar fork na sua conta
```

#### 2. Aplicar Mudanças
Após fazer fork, aplicar estas mudanças:

##### a) Atualizar `version.json`:
```json
{
  "version": "1.4.0"
}
```

##### b) Atualizar `pdu_mqtt/config.yaml`:
```yaml
name: LogiLink & Intellinet PDU MQTT Bridge
version: "1.4.0"
slug: pdu_mqtt
description: "MQTT bridge for PDUs with automatic visual discovery"
# ... resto da configuração
webui: http://[HOST]:[PORT:8099]
ports:
  8099/tcp: 8099
```

##### c) Adicionar novos ficheiros:
- `pdu_mqtt/web_interface.py`
- `pdu_mqtt/bug_fixes.py`
- `pdu_mqtt/templates/index.html`
- `examples/visual_dashboard.yaml`

##### d) Atualizar `pdu_mqtt/run.py`:
```python
# Adicionar import
import threading

# Adicionar função web interface
def start_web_interface():
    try:
        from web_interface import run_web_interface
        run_web_interface()
    except Exception as e:
        logger.error(f"Failed to start web interface: {e}")

# No main(), adicionar:
web_thread = threading.Thread(target=start_web_interface, daemon=True)
web_thread.start()
```

##### e) Atualizar `pdu_mqtt/requirements.txt`:
```txt
paho-mqtt==1.6.1
aiohttp==3.9.1
asyncio-mqtt==0.16.1
requests==2.31.0
flask==2.3.3
werkzeug==2.3.7
```

#### 3. Usar o Fork
```yaml
# Settings → Add-ons → Add-on Store → ... → Repositories
# Adicionar URL:
https://github.com/[SEU_USERNAME]/homeassistant-addon-logilink-pdu-mqtt
```

### **Opção 3: Aplicação Manual (Avançado)**

#### 1. Clonar o Repositório Original
```bash
git clone https://github.com/BitReportPT/homeassistant-addon-logilink-pdu-mqtt
cd homeassistant-addon-logilink-pdu-mqtt
```

#### 2. Aplicar Mudanças Manualmente
```bash
# Atualizar version.json
echo '{"version": "1.4.0"}' > version.json

# Atualizar config.yaml
sed -i 's/version: "1.3.4"/version: "1.4.0"/' pdu_mqtt/config.yaml

# Adicionar novos ficheiros (copiar da workspace)
# ... (processo manual)
```

#### 3. Hospedar Localmente ou Fazer Push
```bash
# Fazer push para o seu próprio repositório
git remote set-url origin https://github.com/[SEU_USERNAME]/[NOVO_REPO]
git add .
git commit -m "Update to version 1.4.0 with visual interface"
git push origin main
```

## 📦 Ficheiros Essenciais para Copiar

### **Ficheiros Obrigatórios**:
1. `version.json` - Versão 1.4.0
2. `pdu_mqtt/config.yaml` - Configuração atualizada
3. `pdu_mqtt/web_interface.py` - Interface web
4. `pdu_mqtt/templates/index.html` - Template HTML
5. `pdu_mqtt/run.py` - Código principal atualizado
6. `pdu_mqtt/requirements.txt` - Dependências atualizadas

### **Ficheiros Opcionais**:
1. `pdu_mqtt/bug_fixes.py` - Correções de bugs
2. `examples/visual_dashboard.yaml` - Dashboard visual
3. `README_VISUAL_DISCOVERY.md` - Documentação
4. `CHANGELOG_V1.4.0.md` - Changelog detalhado

## 🔍 Verificação Final

Após aplicar as mudanças:

1. **Verificar versão**:
   ```bash
   cat version.json
   cat pdu_mqtt/config.yaml | grep version
   ```

2. **Testar instalação**:
   ```yaml
   # Home Assistant deve mostrar: "Versão atual: 1.4.0"
   ```

3. **Testar interface web**:
   ```
   # Acessar: http://[IP]:8099
   ```

## 📞 Contactar Mantedores (Alternativa)

Se preferir que o repositório original seja atualizado:

1. **Abrir Issue** no repositório original
2. **Sugerir as melhorias** desenvolvidas
3. **Oferecer Pull Request** com as mudanças
4. **Aguardar aprovação** dos mantedores

## 🎯 Recomendação

**Para uso imediato**: Opção 1 (Repositório Próprio)
**Para contribuir**: Opção 2 (Fork + Pull Request)
**Para aprender**: Opção 3 (Aplicação Manual)

---

**Resultado**: Home Assistant mostrará "Versão atual: 1.4.0" com interface visual disponível na porta 8099.
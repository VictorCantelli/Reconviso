# 🚀 Setup Rápido - 5 Minutos

## Passo 1: Preparar Repositório (2 min)

### 1.1 Criar estrutura de diretórios

```bash
mkdir -p .github/workflows scripts nuclei-templates/{custom-exposure,custom-panels} wordlists
```

### 1.2 Criar arquivos necessários

```bash
# Workflow principal
touch .github/workflows/osint-recon.yml

# Scripts Python
touch scripts/conviso_integration.py
touch scripts/normalize_findings.py

# Templates custom Nuclei
touch nuclei-templates/custom-exposure/sensitive-files.yaml

# Wordlists básicas
touch wordlists/common-paths.txt
```

### 1.3 Copiar conteúdo dos artifacts

Copie o conteúdo dos seguintes artifacts criados anteriormente:

1. **`.github/workflows/osint-recon.yml`** ← `osint_recon_workflow`
2. **`scripts/conviso_integration.py`** ← `conviso_integration_script`
3. **`nuclei-templates/custom-exposure/sensitive-files.yaml`** ← `custom_nuclei_template`

## Passo 2: Configurar Secrets (1 min)

### Via GitHub UI

1. Acesse: **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Adicione:

```
Nome: CONVISO_API_KEY
Valor: [sua-api-key-do-conviso]
```

4. (Opcional) Adicione:

```
Nome: SLACK_WEBHOOK_URL
Valor: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Via GitHub CLI

```bash
# Instalar GitHub CLI se necessário
# macOS: brew install gh
# Linux: snap install gh
# Windows: choco install gh

# Autenticar
gh auth login

# Adicionar secrets
gh secret set CONVISO_API_KEY
# Cole sua API key quando solicitado

gh secret set SLACK_WEBHOOK_URL
# Cole sua webhook URL quando solicitado
```

## Passo 3: Obter API Key do Conviso (1 min)

### Método 1: Via UI do Conviso

1. Acesse: https://app.convisoappsec.com
2. Login → **Settings** → **API Keys**
3. Click **"Generate New API Key"**
4. Copie e salve em local seguro
5. Cole no GitHub Secret

### Método 2: Via GraphQL (teste)

```bash
# Testar se sua API key funciona
curl -X POST https://api.convisoappsec.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{"query":"query{viewer{email name}}"}'

# Resposta esperada:
# {"data":{"viewer":{"email":"seu@email.com","name":"Seu Nome"}}}
```

## Passo 4: Configurar Python Requirements (30 seg)

Crie `requirements.txt`:

```txt
requests>=2.31.0
python-dotenv>=1.0.0
```

Commit:

```bash
git add requirements.txt
git commit -m "Add Python dependencies"
```

## Passo 5: Primeiro Teste (30 seg)

### Executar workflow manualmente

1. Acesse **Actions** no GitHub
2. Selecione **"🔍 Advanced OSINT Recon Pipeline"**
3. Click **"Run workflow"**
4. Preencha:
   - **Target URL**: `https://example.com` (para teste)
   - **Scope**: `passive-only` (início conservador)
   - **Notify Slack**: `false`
5. Click **"Run workflow"**

### Via GitHub CLI

```bash
gh workflow run osint-recon.yml \
  -f target=https://example.com \
  -f scope=passive-only \
  -f notify_slack=false
```

## ✅ Verificação de Setup

### Checklist

- [ ] Estrutura de diretórios criada
- [ ] Workflow YAML no lugar correto
- [ ] Script Python de integração adicionado
- [ ] Secret `CONVISO_API_KEY` configurado
- [ ] (Opcional) Secret `SLACK_WEBHOOK_URL` configurado
- [ ] Primeiro workflow executado com sucesso

### Verificar resultado

Após execução do workflow:

1. **Actions** → Selecione o run
2. Verifique os jobs:
   - ✅ `passive-recon` → deve completar
   - ✅ `osint-dorks` → deve completar
   - ✅ `process-findings` → deve completar
   - ✅ `conviso-integration` → deve completar

3. **Artifacts** → Baixe e verifique:
   - `passive-recon-results/` → deve conter JSONs
   - `normalized-findings.json` → deve ter findings
   - `RECON_REPORT.md` → relatório em markdown

## 🎯 Próximos Passos

### Nível 1: Básico (você já está aqui!)
- [x] Setup inicial
- [x] Primeiro scan passivo
- [ ] Revisar findings no Conviso

### Nível 2: Intermediário
- [ ] Ativar `passive-active-light` scope
- [ ] Configurar notificações Slack
- [ ] Criar wordlists customizadas
- [ ] Adicionar nuclei templates próprios

### Nível 3: Avançado
- [ ] Usar `full-recon` scope
- [ ] Integrar com CI/CD do projeto
- [ ] Schedule automático (cron)
- [ ] Correlação de findings históricos
- [ ] Dashboard customizado

## 📊 Exemplos de Comandos Úteis

### Executar scan completo

```bash
gh workflow run osint-recon.yml \
  -f target=https://seu-site.com \
  -f scope=full-recon \
  -f notify_slack=true
```

### Agendar scan semanal

Adicione ao workflow YAML:

```yaml
on:
  schedule:
    - cron: '0 2 * * 1'  # Toda segunda-feira às 2h AM UTC
  workflow_dispatch:
    # ... resto do código
```

### Monitorar execução

```bash
# Listar últimos runs
gh run list --workflow=osint-recon.yml --limit 5

# Ver logs de um run específico
gh run view RUN_ID --log

# Baixar artifacts
gh run download RUN_ID
```

## 🐛 Troubleshooting Rápido

### Erro: "CONVISO_API_KEY not found"

**Solução**: Verifique se o secret está configurado:

```bash
gh secret list | grep CONVISO
```

Se não aparecer, adicione:

```bash
gh secret set CONVISO_API_KEY
```

### Erro: "Go installation failed"

**Solução**: Workflow já inclui instalação do Go. Se persistir, verifique:

```yaml
- name: Setup Go
  uses: actions/setup-go@v5
  with:
    go-version: '1.21'  # Versão mínima
```

### Workflow demora muito

**Solução**: Use scope mais leve:

- `passive-only` → ~5-10 min
- `passive-active-light` → ~15-25 min
- `full-recon` → ~30-60 min

### Findings não aparecem no Conviso

**Debug**:

1. Verificar logs do job `conviso-integration`
2. Testar API key manualmente (comando acima)
3. Verificar se projeto foi criado no Conviso UI

## 📚 Recursos Úteis

### Documentação

- [Conviso API](https://docs.convisoappsec.com/api/api-overview)
- [Nuclei Templates](https://github.com/projectdiscovery/nuclei-templates)
- [GitHub Actions](https://docs.github.com/en/actions)

### Ferramentas

- [ProjectDiscovery Tools](https://github.com/projectdiscovery)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)

### Comunidade

- [Discord - ProjectDiscovery](https://discord.gg/projectdiscovery)
- [Conviso Platform Support](https://support.convisoappsec.com)

---

## 🎉 Pronto!

Seu pipeline OSINT está configurado e rodando. Agora é só:

1. ✅ Executar scans regulares
2. ✅ Revisar findings no Conviso
3. ✅ Ajustar templates conforme necessário
4. ✅ Compartilhar resultados com o time

**Happy Hunting! 🔍**
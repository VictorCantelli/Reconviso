# 🔍 OSINT Recon Automation Pipeline

Pipeline automatizado de reconhecimento OSINT usando GitHub Actions, integrado com Conviso Platform.

## 📋 Índice

- [Características](#características)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Arquitetura](#arquitetura)
- [Integração Conviso](#integração-conviso)
- [Troubleshooting](#troubleshooting)

## ✨ Características

### 🎯 Recon Passivo
- ✅ Technology stack detection (httpx, Wappalyzer)
- ✅ DNS enumeration completo
- ✅ Subdomain discovery (passive)
- ✅ SSL/TLS analysis
- ✅ Wayback Machine mining (GAU + waybackurls)
- ✅ Parameter extraction automático
- ✅ Endpoint discovery

### 🔎 OSINT & Sensitive Files
- ✅ Exposed admin panels
- ✅ Configuration files (.env, .git, backups)
- ✅ Server misconfigurations (Apache, Nginx, IIS)
- ✅ Information disclosure (phpinfo, debug, server-status)
- ✅ Google Dorks automation

### 🎯 Active Recon (Light)
- ✅ Directory fuzzing controlado
- ✅ Endpoint validation
- ✅ Form detection (POST endpoints)
- ✅ Rate limiting integrado

### 🧬 Vulnerability Scanning
- ✅ Nuclei full scan
- ✅ Template filtering por severity
- ✅ Bulk scanning otimizado

### 📊 Processing & Reporting
- ✅ Findings normalization
- ✅ Deduplicação automática
- ✅ Severity breakdown
- ✅ Markdown reports
- ✅ JSON export

### 📤 Integrations
- ✅ **Conviso Platform** (GraphQL API)
- ✅ Slack notifications
- ✅ Discord webhooks (opcional)
- ✅ GitHub Comments

## 📁 Estrutura do Projeto

```
osint-recon-automation/
├── .github/
│   └── workflows/
│       └── osint-recon.yml          # Workflow principal
│
├── scripts/
│   ├── conviso_integration.py       # Integração Conviso
│   ├── normalize_findings.py        # Normalização de dados
│   └── slack_notifier.py           # Notificações Slack
│
├── wordlists/
│   ├── common-paths.txt            # Paths comuns
│   ├── admin-panels.txt            # Admin endpoints
│   └── config-files.txt            # Arquivos de config
│
├── nuclei-templates/                # Templates custom
│   ├── exposed-configs/
│   ├── info-disclosure/
│   └── misconfigurations/
│
├── docs/
│   ├── SETUP.md                    # Guia de setup
│   ├── CONVISO_INTEGRATION.md      # Documentação Conviso
│   └── ARCHITECTURE.md             # Arquitetura detalhada
│
├── .env.example                    # Exemplo de variáveis
├── requirements.txt                # Python dependencies
└── README.md                       # Este arquivo
```

## 🔧 Pré-requisitos

### GitHub Repository Secrets

Configure os seguintes secrets em **Settings > Secrets and variables > Actions**:

```bash
CONVISO_API_KEY          # API key do Conviso Platform
SLACK_WEBHOOK_URL        # (Opcional) Webhook do Slack
DISCORD_WEBHOOK_URL      # (Opcional) Webhook do Discord
```

### Permissões Necessárias

- ✅ Read/Write access to repository
- ✅ Actions permissions enabled
- ✅ Artifacts upload enabled

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/your-org/osint-recon-automation.git
cd osint-recon-automation
```

### 2. Configure os secrets

Via GitHub UI ou GitHub CLI:

```bash
gh secret set CONVISO_API_KEY
# Cole sua API key quando solicitado

gh secret set SLACK_WEBHOOK_URL
# Cole sua webhook URL quando solicitado
```

### 3. Crie os diretórios necessários

```bash
mkdir -p passive osint active vulnerabilities
```

### 4. (Opcional) Setup local para testes

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` local (não commitar):

```bash
CONVISO_API_KEY=your_api_key_here
CONVISO_API_URL=https://api.convisoappsec.com/graphql
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Ajustar Rate Limits

Edite `.github/workflows/osint-recon.yml`:

```yaml
# Linha ~245 - Directory Fuzzing
-rate 10  # Requisições por segundo

# Linha ~290 - Nuclei Scan
-rate-limit 50  # Requisições por minuto
```

## 🎮 Uso

### Via GitHub Actions UI

1. Acesse **Actions** no repositório
2. Selecione **"🔍 Advanced OSINT Recon Pipeline"**
3. Click **"Run workflow"**
4. Preencha:
   - **Target URL**: `https://example.com`
   - **Scope**: `passive-active-light` (recomendado)
   - **Notify Slack**: `true/false`
5. Click **"Run workflow"**

### Via GitHub CLI

```bash
gh workflow run osint-recon.yml \
  -f target=https://example.com \
  -f scope=passive-active-light \
  -f notify_slack=true
```

### Via API

```bash
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/osint-recon.yml/dispatches \
  -d '{"ref":"main","inputs":{"target":"https://example.com","scope":"passive-active-light"}}'
```

## 🏗️ Arquitetura

### Pipeline Flow

```
┌─────────────────┐
│   Input URL     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Passive Recon   │◄─── httpx, subfinder, dnsx
│ • Tech Stack    │
│ • DNS Info      │
│ • Subdomains    │
│ • SSL/TLS       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Wayback Mining  │◄─── gau, waybackurls
│ • URLs          │
│ • Parameters    │
│ • Endpoints     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OSINT & Dorks   │◄─── nuclei (exposures)
│ • Config files  │
│ • Admin panels  │
│ • Misconfigs    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Active Recon    │◄─── ffuf, httpx
│ • Dir fuzzing   │
│ • Validation    │
│ • Forms         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Vuln Scanning   │◄─── nuclei (full)
│ • Templates     │
│ • Severity      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Normalization   │◄─── Python
│ • Deduplicate   │
│ • Classify      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Conviso Upload  │◄─── GraphQL
│ • Projects      │
│ • Vulns         │
│ • Summary       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Notifications   │◄─── Slack, Discord
│ • Report        │
│ • Artifacts     │
└─────────────────┘
```

### Dados Gerados

#### Artifacts

| Artifact | Conteúdo | Retenção |
|----------|----------|----------|
| `passive-recon-results` | Tech, DNS, subdomains, wayback | 30 dias |
| `osint-results` | Exposed files, panels, configs | 30 dias |
| `active-recon-results` | Fuzzing, validated endpoints | 30 dias |
| `vulnerability-results` | Nuclei scan completo | 30 dias |
| `normalized-findings` | JSON normalizado | 90 dias |
| `final-report` | Markdown report | Permanente |

## 🔗 Integração Conviso

### Fluxo de Dados

```python
# 1. Autenticação
headers = {
    "Authorization": f"Bearer {CONVISO_API_KEY}",
    "Content-Type": "application/json"
}

# 2. Criar/Buscar Projeto
project = get_or_create_project(target_url)

# 3. Enviar Findings
for finding in findings:
    create_vulnerability(
        project_id=project.id,
        title=finding.name,
        severity=finding.severity,
        description=format_description(finding)
    )

# 4. Criar Sumário
create_scan_summary(project_id, summary)
```

### Mapeamento de Severidade

| Nuclei | Conviso |
|--------|---------|
| critical | CRITICAL |
| high | HIGH |
| medium | MEDIUM |
| low | LOW |
| info | INFORMATIONAL |

### GraphQL Queries Utilizadas

#### Buscar Projeto
```graphql
query SearchProject($name: String!) {
  projects(filter: {name: {eq: $name}}) {
    collection {
      id
      name
    }
  }
}
```

#### Criar Vulnerabilidade
```graphql
mutation CreateVulnerability($input: CreateVulnerabilityInput!) {
  createVulnerability(input: $input) {
    vulnerability {
      id
      title
      severity
    }
  }
}
```

## 🐛 Troubleshooting

### Workflow falha no job "passive-recon"

**Problema**: Ferramentas Go não instaladas

**Solução**:
```yaml
# Verificar versão do Go
- name: Setup Go
  uses: actions/setup-go@v5
  with:
    go-version: '1.21'  # Mínimo requerido
```

### Findings não aparecem no Conviso

**Problema**: API key inválida ou projeto não criado

**Solução**:
1. Verificar secret `CONVISO_API_KEY`
2. Testar API key manualmente:
```bash
curl -H "Authorization: Bearer YOUR_KEY" \
  https://api.convisoappsec.com/graphql \
  -d '{"query":"query{viewer{email}}"}'
```

### Rate Limit Exceeded

**Problema**: Muitas requisições em pouco tempo

**Solução**:
```yaml
# Reduzir rate limits
-rate 5          # ffuf
-rate-limit 25   # nuclei
```

### Wayback URLs vazias

**Problema**: Domínio novo ou não indexado

**Solução**: Aguardar ou usar outras fontes:
```bash
# Adicionar CommonCrawl
commoncrawl -d example.com
```

## 📚 Recursos Adicionais

- [Nuclei Templates](https://github.com/projectdiscovery/nuclei-templates)
- [Conviso API Docs](https://docs.convisoappsec.com/api/api-overview)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [OSINT Framework](https://osintframework.com/)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📝 License

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🔒 Security

Este projeto é para uso em **ambientes autorizados apenas**. Nunca execute scans em:
- ❌ Sistemas sem autorização expressa
- ❌ Infraestrutura de terceiros
- ❌ Ambientes de produção sem approval

Para reportar vulnerabilidades no código: security@your-org.com

---

**Developed with ❤️ for AppSec teams**
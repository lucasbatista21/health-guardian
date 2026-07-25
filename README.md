# 🛡️ Application Health Guardian

> **Sistema Serverless de Observabilidade, Alertas em Tempo Real e Status Page Dinâmica.**

[![GitHub Actions Status](https://img.shields.io/badge/GitHub%20Actions-Automated-blue?logo=githubactions)](https://github.com/lucasbatista21/health-guardian/actions)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-green?logo=github)](https://lucasbatista21.github.io/health-guardian/)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://www.python.org/)

📍 **Status Page ao Vivo:** [https://lucasbatista21.github.io/health-guardian/](https://lucasbatista21.github.io/health-guardian/)

---

## 📖 Contexto e Motivação (Caso de Uso Real)

A ideia do **Application Health Guardian** surgiu a partir de uma experiência prática em suporte e infraestrutura de TI. 

Durante uma instabilidade recente nos serviços da Microsoft (que afetou ferramentas como Teams e OneDrive), o volume de chamados e cobranças por parte dos usuários foi imediato. Enquanto a investigação e o *troubleshooting* local aconteciam, a confirmação oficial por parte do provedor levou tempo para ser formalizada por e-mail — enquanto o pico de solicitações no Downdetector já indicava a queda global.

Esse cenário gerou uma reflexão: **como funciona a engenharia por trás desses sistemas de monitoramento contínuo?**

Para entender melhor essa arquitetura na prática, desenvolvi o **Application Health Guardian** — uma solução de observabilidade *lightweight*, 100% gratuita e *serverless*, projetada para monitorar a disponibilidade e a saúde de aplicações e APIs de forma autônoma.

---

## 🛠️ Funcionalidades Principais

- 🔍 **Health Check de Serviços:** Monitora endpoints HTTP/HTTPS e valida status de resposta (ex: `200 OK`, `404 Not Found`, `500 Internal Error`).
- ⏱️ **Métricas de Latência (SRE):** Mede o tempo exato de resposta em milissegundos ($ms$) para cada requisição.
- 📱 **Alertas de Incidentes no Telegram:** Dispara notificações em tempo real com formato Markdown direto no celular quando um serviço falha.
- 📊 **Status Page Estática e Dinâmica:** Gera um painel HTML limpo e responsivo atualizado automaticamente no **fuso horário de Brasília (BRT)**.
- ⚙️ **Automação Serverless via CI/CD:** Executado via **GitHub Actions** a cada 15 minutos (via *Cron Job*) e a cada *push* no repositório.

---

## 📐 Arquitetura do Sistema

                     ┌──────────────────────────────┐
                     │   Trigger: Cron (15 min)     │
                     │      ou Evento de Push       │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │   GitHub Actions Runner      │
                     │      (Ubuntu Server)         │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │  Lê 'services.json'          │
                     │  Executa 'health_check.py'   │
                     └──────────────┬───────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  │                                   │
                  ▼                                   ▼
    ┌──────────────────────────┐        ┌──────────────────────────┐
    │  Mede Latência e Status  │        │  Houve Incidente/Falha?  │
    │  Gera 'index.html'       │        └─────────────┬────────────┘
    └─────────────┬────────────┘                      │
                  │                        Sim ┌──────┴──────┐ Não
                  ▼                            ▼             ▼
    ┌──────────────────────────┐    ┌────────────────────┐ ┌────────┐
    │ Commit do 'index.html'   │    │ Dispara Alerta via │ │  Fim   │
    │ Deploy no GitHub Pages   │    │ API do Telegram    │ └────────┘
    └──────────────────────────┘    └────────────────────┘

---

## 🧠 Tecnologias e Boas Práticas Aplicadas

| Categoria | Tecnologia / Prática | Descrição |
| :--- | :--- | :--- |
| **Linguagem** | Python 3 | Desenvolvimento sem dependências externas pesadas (apenas bibliotecas nativas como `urllib`, `json`, `time` e `datetime`). |
| **CI/CD & Serverless** | GitHub Actions | Workflows agendados via `cron` para execução automatizada e sem necessidade de servidor dedicado. |
| **Hospedagem** | GitHub Pages | Publicação contínua da Status Page pública na nuvem. |
| **Notificações** | Telegram Bot API | Envio imediato de mensagens de incidentes em formato estilizado. |
| **DevSecOps** | GitHub Secrets | Armazenamento encriptado de variáveis sensíveis (`TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`). |
| **Versionamento** | Git & GitHub | Commits semânticos e utilização de `.gitignore` rigoroso contra vazamento de credenciais locais. |

---

## 📁 Estrutura do Repositório

```text
health-guardian/
├── .github/
│   └── workflows/
│       └── healthcheck.yml   # Workflow de automação CI/CD no GitHub Actions
├── health_check.py           # Script principal de monitoramento e geração do HTML
├── services.json             # Lista de serviços/APIs a serem monitorados
├── index.html                # Dashboard público gerado dinamicamente
├── README.md                 # Documentação do projeto
└── .gitignore                # Regras para ignorar arquivos locais/sensíveis
⚙️ Configuração e Execução Local
Pré-requisitos
Python 3.10+ instalado na sua máquina.

Git instalado.

1. Clonar o Repositório
Bash
git clone [https://github.com/lucasbatista21/health-guardian.git](https://github.com/lucasbatista21/health-guardian.git)
cd health-guardian
2. Configurar os Serviços Monitorados
Edite o arquivo services.json para adicionar ou remover URLs que deseja acompanhar:

JSON
[
  {
    "name": "Google (Busca)",
    "url": "[https://www.google.com](https://www.google.com)"
  },
  {
    "name": "GitHub (Status)",
    "url": "[https://github.com](https://github.com)"
  }
]
3. Configurar Variáveis de Ambiente (Opcional - para testes com o Telegram)
Se quiser receber os alertas do Telegram rodando localmente no seu terminal:

Linux / Mac (Bash):

Bash
export TELEGRAM_BOT_TOKEN="seu_bot_token"
export TELEGRAM_CHAT_ID="seu_chat_id"
Windows (PowerShell):

PowerShell
$env:TELEGRAM_BOT_TOKEN="seu_bot_token"
$env:TELEGRAM_CHAT_ID="seu_chat_id"
4. Executar o Script
Bash
python health_check.py
Após a execução, um arquivo index.html atualizado será gerado na raiz do projeto.

🛡️ Segurança (DevSecOps) e Tolerância a Falhas
Token Protection: Nenhuma credencial de API é colocada diretamente no código (hardcoded). Todas as variáveis sensíveis são injetadas no pipeline do GitHub Actions via Secrets.

Prevenção de Loops no CI: A gravação do index.html pela automação utiliza a flag [skip ci] no commit, impedindo disparos infinitos da esteira de integração contínua.

Isolamento de Erros: Exceções de conexão (ex: HTTPError, URLError ou timeouts) são tratadas individualmente sem interromper a verificação dos outros serviços mapeados.

✉️ Contato e Conexões
Desenvolvido por Lucas Batista como parte de estudos práticos em Engenharia de Software, Infraestrutura de TI e práticas de DevOps/SRE.

- **GitHub:** [lucasbatista21](https://github.com/lucasbatista21)
- **LinkedIn:** [Lucas Batista de Oliveira](https://www.linkedin.com/in/lucas-batistade-oliveira/)

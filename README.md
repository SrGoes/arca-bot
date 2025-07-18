# 🚀 ARCA Bot v1.3.7

**Bot Discord multipropósito para a organização ARCA (Star Citizen)**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.3+-blue.svg)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/Architecture-Modular-green.svg)](src/)

Bot Discord avançado desenvolvido especificamente para a organização ARCA no universo de Star Citizen. Oferece sistema completo de economia com Arca Coins, sorteios interativos, painel de carteiras em tempo real e sistema robusto de permissões.

---

## 📋 **Índice**

- [🎯 Funcionalidades](#-funcionalidades)
- [🏗️ Arquitetura](#%EF%B8%8F-arquitetura)
- [⚙️ Instalação e Configuração](#%EF%B8%8F-instalação-e-configuração)
- [🚀 Execução](#-execução)
- [📊 Comandos](#-comandos)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🧪 Testes](#-testes)
- [🐛 Troubleshooting](#-troubleshooting)
- [🤝 Contribuindo](#-contribuindo)

---

## 🎯 **Funcionalidades**

### 💰 **Sistema de Economia**
- **Arca Coins (AC)** - Moeda virtual da organização
- **Recompensas por Voz** - 20 AC/hora por tempo em canais C.O.M.M.S OPS
- **Daily Rewards** - Bônus diário de 70-100 AC
- **Comandos Administrativos** - Distribuição e remoção de moedas
- **Persistência** - Dados salvos com backup automático a cada 6 horas

### 🎲 **Sistema de Sorteios**
- **Criação Dinâmica** - Sorteios com preços configuráveis
- **Interface Interativa** - Botões para comprar tickets e sortear
- **Painel Administrativo** - Controle completo para admins
- **Sistema de Tickets** - Compra com preços progressivos (1.1x por ticket adicional)
- **Segurança** - Reembolso automático em caso de cancelamento

### 🎛️ **Painel de Carteiras**
- **Ranking Completo** - Mostra TODOS os usuários (não apenas top 10)
- **Persistência Automática** - Sobrevive a reinicializações do bot
- **Atualização em Tempo Real** - Dados sempre atualizados a cada 5 minutos
- **Interface Visual** - Embed elegante com estatísticas detalhadas
- **Recuperação Inteligente** - Sistema recupera painéis após restart

### 🔒 **Sistema de Permissões**
- **Hierarquia de Níveis** - Owner > Admin > Discord Admin > Economy Admin > User
- **Verificação Automática** - Checagem por cargos e permissões Discord
- **Controle Granular** - Diferentes níveis para diferentes comandos
- **Segurança** - Verificação dupla por cargos e permissões nativas

### ⚡ **Sistemas de Performance**
- **Cache Inteligente** - Sistema TTL com limpeza automática
- **Rate Limiting** - Proteção avançada contra spam
- **Logs Estruturados** - Sistema de logging com rotação automática  
- **Backup Automático** - Proteção de dados a cada 6 horas
- **Configuração Centralizada** - Sistema JSON + fallbacks inteligentes

### 🤖 **Sistemas Automáticos**
- **Ganho por Voz** - 20 AC por hora em canais da categoria "C.O.M.M.S OPS"
- **Log de Cargos** - Mensagens automáticas quando membros recebem novos cargos
- **Monitoramento de Status** - Detecção de entrada/saída de canais de voz
- **Painel Automático** - Atualização automática do ranking de carteiras

---

## 🏗️ **Arquitetura**

### 📊 **Padrão de Arquitetura: Modular Enterprise**

```
ARCA Bot Architecture
├── 🎯 Core Systems (src/core/)
│   ├── ⚙️ Config Management (settings.py)
│   ├── 🗄️ Cache System (cache.py) 
│   ├── 🛡️ Rate Limiting (rate_limiter.py)
│   ├── 🔒 Permissions (permissions.py)
│   └── 🎛️ Wallet Panel (wallet_panel.py)
├── 🧩 Business Logic (src/modules/)
│   ├── 💰 Economy System (economy.py)
│   └── 🎲 Lottery System (lottery.py)
├── 🎮 Command Interface (src/commands/)
│   ├── 💳 Economy Commands (economy.py)
│   ├── 🎯 Lottery Commands (lottery.py)
│   └── 🔧 Basic Commands (basic.py)
├── ⚙️ Configuration (config/)
│   ├── 📝 Settings Manager (settings.py)
│   └── 🔧 Bot Config (bot_config.json)
└── 🧪 Quality & Automation
    ├── 📊 Unit Tests (tests/)
    ├── 🔧 Build Scripts (scripts/)
    └── 🚀 CI/CD Ready
```

---

## ⚙️ **Instalação e Configuração**

### **Pré-requisitos**
- Python 3.8 ou superior
- Git (para clonar o repositório)
- Discord Bot Token

### **1. Clone o repositório**
```bash
git clone https://github.com/SrGoes/arca-bot.git
cd arca-bot
```

### **2. Instale as dependências**
```bash
pip install -r requirements.txt
```

### **3. Configure o ambiente**
1. Copie o arquivo de exemplo:
   ```bash
   copy .env.example .env    # Windows
   cp .env.example .env      # Linux/Mac
   ```
2. Edite o arquivo `.env` e adicione seu token do bot:
   ```env
   DISCORD_BOT_TOKEN=seu_token_aqui
   ```

### **4. Criação e Configuração do Bot Discord**

#### **Criando o Bot**
1. Acesse o [Discord Developer Portal](https://discord.com/developers/applications)
2. Clique em "New Application"
3. Dê um nome ao seu bot (ex: "ARCA Bot")
4. Vá para a aba "Bot"
5. Clique em "Add Bot"
6. Copie o token e cole no arquivo `.env`

#### **Intents Necessários**
Certifique-se de habilitar os seguintes intents no Developer Portal:
- ✅ **Server Members Intent** (para detectar mudanças de membros)
- ✅ **Message Content Intent** (para processar comandos)

#### **Convite do Bot**
Use este link para convidar o bot (substitua `CLIENT_ID` pelo ID da sua aplicação):
```
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=3165184&scope=bot
```

### **5. Configuração do Servidor Discord**

#### **Canais Necessários**
1. **Categoria**: `C.O.M.M.S OPS` com canais de voz para ganhar AC
2. **Canal**: `log-cargos` para logs de mudanças de cargos  
3. **Canal**: `painel-carteiras` para o painel de carteiras automático
4. **Canal**: `sorteios` para sorteios (opcional)

#### **Cargos Administrativos**
- `ECONOMIA_ADMIN` - Para comandos de economia
- `SORTEIO_ADMIN` - Para criar sorteios  
- `ADMIN` - Para comandos administrativos gerais

#### **Permissões do Bot**
- Ver canais e histórico de mensagens
- Enviar mensagens e usar embeds
- Conectar e ver canais de voz (monitoramento)
- Gerenciar mensagens (painel de carteiras)

---

## 🚀 **Execução**

### **Execução Simples**
```bash
python run.py
```

### **Com Ambiente Virtual (Recomendado)**
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)  
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar bot
python run.py
```

### **Usando Scripts de Automação**
```bash
# Windows
scripts\setup.bat

# Linux/Mac
chmod +x scripts/setup.sh
./scripts/setup.sh
```

---

## 📊 **Comandos**

### **🔧 Comandos Básicos**
| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `!ping` | Testa a latência do bot | Todos |
| `!info` | Mostra informações sobre o bot | Todos |
| `!help` | Lista todos os comandos disponíveis | Todos |
| `!desligar` | Desliga o bot de forma segura | Admin |

### **💰 Comandos de Economia**
| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `!saldo` | Mostra seu saldo de AC, total ganho e tempo em voz | Todos |
| `!diario` | Recompensa diária (70-100 AC) | Todos |
| `!distribuir <valor>` | Distribui AC para todos na mesma call | Economy Admin |
| `!pagar <@user> <valor>` | Gera e paga AC para um usuário específico | Economy Admin |
| `!remover <@user> <valor> [motivo]` | Remove AC de um usuário específico | Economy Admin |

### **🎲 Comandos de Sorteio**
| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `!criarsorteio Nome \| Valor` | Cria um sorteio com botões interativos | Lottery Admin |

**Botões Interativos:**
- 🎲 **Sortear** - Realiza o sorteio
- 🎫 **Comprar** - Compra tickets (preço escalável)
- ❌ **Cancelar** - Cancela o sorteio (reembolso automático)

### **🎛️ Sistema de Painel Automático**
- **Painel de Carteiras** - Atualização automática a cada 5 minutos no canal `painel-carteiras`
- **Ranking Completo** - Mostra TODOS os usuários (não apenas top 10)
- **Estatísticas** - Total em circulação, usuários ativos, distribuição

### **📈 Exemplos de Uso**

#### **Sistema de Economia**
```bash
# Usuário entra em canal "Ops Alpha" (categoria C.O.M.M.S OPS)
# Após 1 hora: +20 AC automático

# Comando diário estando no canal
!diario → "Você recebeu 85 AC! 🪙"

# Ver saldo
!saldo → "Saldo: 105 AC | Total Ganho: 105 AC | Tempo em Voz: 60 min"
```

#### **Sistema de Sorteios**
```bash
# Admin cria sorteio
!criarsorteio Nave Aurora | 50

# Usuários compram tickets:
# 1º ticket: 50 AC
# 2º ticket: 55 AC (50 × 1.1¹)
# 3º ticket: 60 AC (50 × 1.1²)

# Admin sorteia quando quiser
# Sistema escolhe vencedor baseado em probabilidade por tickets
```

---

## 📁 **Estrutura do Projeto**

```
arca-bot/
├── 📁 config/                    # Sistema de configuração centralizado
│   ├── settings.py              # Gerenciador de configurações
│   └── bot_config.json          # Configurações do bot (auto-gerado)
├── 📁 src/                      # Código fonte modular
│   ├── main.py                  # Entry point principal
│   ├── 📁 commands/             # Comandos organizados por categoria
│   │   ├── basic.py            # Comandos básicos (ping, info, help)
│   │   ├── economy.py          # Comandos de economia
│   │   └── lottery.py          # Comandos de sorteio
│   ├── 📁 core/                # Sistemas centrais
│   │   └── 📁 utils/           # Utilitários
│   │       ├── cache.py        # Sistema de cache
│   │       ├── permissions.py  # Sistema de permissões
│   │       ├── rate_limiter.py # Rate limiting
│   │       └── wallet_panel.py # Painel de carteiras
│   └── 📁 modules/             # Lógica de negócio
│       ├── economy.py          # Sistema de economia
│       └── lottery.py          # Sistema de sorteios
├── 📁 tests/                    # Suíte de testes
│   ├── test_bot.py             # Testes principais
│   ├── test_config.py          # Testes de configuração
│   └── test_new_structure.py   # Testes da nova estrutura
├── 📁 scripts/                  # Scripts de automação
│   ├── setup.bat              # Setup Windows
│   ├── setup.sh               # Setup Linux/Mac
│   └── test_installation.bat  # Teste de instalação
├── 📁 data/                     # Dados persistentes (criados automaticamente)
│   ├── economy_data.json       # Dados de economia
│   ├── lottery_data.json       # Dados de sorteios
│   └── panel_data.json         # Dados do painel (persistência)
├── 📁 backups/                  # Backups automáticos (criados automaticamente)
├── 📁 logs/                     # Logs do sistema (criados automaticamente)
├── run.py                       # Launcher principal
├── requirements.txt             # Dependências Python
├── pyproject.toml              # Configuração do projeto
├── .env.example                # Exemplo de variáveis de ambiente
├── .gitignore                  # Arquivos ignorados pelo Git
└── README.md                   # Este arquivo
```

---

## 🧪 **Testes**

### **Executar Testes**
```bash
# Windows
run_tests.bat

# Linux/Mac  
python -m pytest tests/ -v

# Com cobertura de código
python -m pytest tests/ --cov=src --cov-report=html
```

### **Estrutura de Testes**
- `tests/test_bot.py` - Testes dos sistemas principais
- `tests/test_config.py` - Testes de configuração
- `tests/test_new_structure.py` - Testes da nova arquitetura

### **Teste de Instalação**
```bash
# Windows
scripts\test_installation.bat

# Verificar dependências
python -c "import discord; print(f'Discord.py v{discord.__version__} OK')"
```

---

## 🐛 **Troubleshooting**

### **Bot não responde**
- ✅ Verifique se o token está correto no arquivo `.env`
- ✅ Certifique-se de que o bot está online no servidor
- ✅ Verifique as permissões do bot nos canais
- ✅ Confirme que os intents estão habilitados no Developer Portal

### **Canal log-cargos não encontrado**
- ✅ Crie um canal com o nome exato `log-cargos`
- ✅ Verifique se o bot tem permissão para ver e enviar mensagens no canal

### **Painel de carteiras não funciona**
- ✅ Crie um canal com o nome exato `painel-carteiras`
- ✅ Verifique se o bot tem permissão para gerenciar mensagens
- ✅ Verifique se os dados do painel estão sendo salvos em `data/panel_data.json`

### **Erros de intents**
- ✅ Habilite "Server Members Intent" no Discord Developer Portal
- ✅ Habilite "Message Content Intent" no Discord Developer Portal
- ✅ Reinicie o bot após habilitar os intents

### **Comandos não funcionam**
- ✅ Verifique se o prefixo está correto (padrão: `!`)
- ✅ Confirme que você tem as permissões necessárias
- ✅ Verifique se o bot tem permissão para ler mensagens

### **Sistema de economia não funciona**
- ✅ Crie a categoria `C.O.M.M.S OPS` com canais de voz
- ✅ Verifique se o bot tem permissão para ver estados de voz
- ✅ Confirme que os dados estão sendo salvos em `data/economy_data.json`

### **Logs e Monitoramento**
O bot mantém logs detalhados em:
- **Console**: Saída em tempo real
- **Arquivo**: Rotação automática em `logs/`

**Níveis de log:**
- `INFO`: Operações normais
- `WARNING`: Situações que merecem atenção  
- `ERROR`: Erros que impedem operações

---

## 🤝 **Contribuindo**

### **Como Contribuir**
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

### **Padrões de Código**
- Use **Python 3.8+** e siga PEP 8
- Documente todas as funções e classes
- Adicione testes para novas funcionalidades
- Use type hints sempre que possível

### **Estrutura de Commits**
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `test:` Testes
- `refactor:` Refatoração

---

## 📄 **Licença**

Este projeto está licenciado sob a **Licença MIT** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🔒 **Segurança**

- ⚠️ **NUNCA** compartilhe seu token do bot
- 🔐 Use arquivos `.env` para configurações sensíveis
- 🛡️ Mantenha as dependências atualizadas
- 🔍 Monitore os logs regularmente
- 📊 Faça backups regulares dos dados

---

## 🌟 **Organização ARCA**

Este bot foi desenvolvido especificamente para a **organização ARCA** no universo de **Star Citizen**. 

**Funcionalidades específicas:**
- Sistema de economia integrado com atividades da organização
- Monitoramento de canais de operações (C.O.M.M.S OPS)
- Sistema de recompensas por participação ativa
- Sorteios para engajamento da comunidade

Para mais informações sobre a organização ARCA, visite nossos canais oficiais.

---

**Desenvolvido com ❤️ pela comunidade ARCA**

---

## 📈 **Estatísticas do Projeto**

- **Versão**: 1.3.7
- **Linguagem**: Python 3.8+
- **Framework**: Discord.py 2.3+
- **Arquitetura**: Modular Enterprise
- **Licença**: MIT
- **Status**: Ativo e em desenvolvimento

# 🚀 ARCA Bot v1.3.7
**Bot Discord multipropósito para a organização ARCA (Star Citizen)**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.3+-blue.svg)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/Architecture-Modular-green.svg)](src/)

---

## 📋 **Índice**

- [🎯 Funcionalidades](#-funcionalidades)
- [🏗️ Arquitetura](#%EF%B8%8F-arquitetura)
- [⚙️ Instalação](#%EF%B8%8F-instalação)
- [🚀 Execução](#-execução)
- [📊 Comandos](#-comandos)
- [🧪 Testes](#-testes)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🔧 Configuração](#-configuração)
- [📚 Documentação](#-documentação)

---

## 🎯 **Funcionalidades**

### 💰 **Sistema de Economia**
- **Arca Coins (AC)** - Moeda virtual da organização
- **Recompensas por Voz** - 20 AC/hora por tempo em canais C.O.M.M.S OPS
- **Daily Rewards** - Bônus diário de 70-100 AC
- **Comandos Administrativos** - Distribuição e remoção de moedas

### 🎲 **Sistema de Sorteios**
- **Criação Dinâmica** - Sorteios com preços configuráveis
- **Interface Interativa** - Botões para comprar tickets e sortear
- **Painel Administrativo** - Controle completo para admins
- **Sistema de Tickets** - Compra com preços progressivos

### 🎛️ **Painel de Carteiras**
- **Ranking Completo** - Mostra TODOS os usuários (não apenas top 10)
- **Persistência Automática** - Sobrevive a reinicializações do bot
- **Atualização em Tempo Real** - Dados sempre atualizados a cada 5 minutos
- **Interface Visual** - Embed elegante com estatísticas detalhadas
- **Recuperação Inteligente** - Sistema recupera painéis após restart

### 🔒 **Sistema de Permissões**
- **Hierarquia de Níveis** - Owner > Admin > Discord Admin > Economy Admin > User
- **Verificação Automática** - Checagem por cargos e permissões
- **Controle Granular** - Diferentes níveis para diferentes comandos

### ⚡ **Sistemas de Performance**
- **Cache Inteligente** - Sistema TTL com limpeza automática
- **Rate Limiting** - Proteção avançada contra spam
- **Logs Estruturados** - Sistema de logging com rotação automática  
- **Backup Automático** - Proteção de dados a cada 6 horas
- **Configuração Centralizada** - Sistema JSON + fallbacks inteligentes

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
    ├── � Build Scripts (scripts/)
    └── � CI/CD Ready
```

---

## ⚙️ **Instalação**

### Pré-requisitos
- Python 3.11 ou superior
- Git (para clonar o repositório)
- Discord Bot Token

### 1. Clone o repositório
```bash
git clone https://github.com/SrGoes/arca-bot.git
cd arca-bot
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o ambiente
1. Copie o arquivo de exemplo:
   ```bash
   copy .env.example .env
   ```
2. Edite o arquivo `.env` e adicione seu token do bot:
   ```env
   DISCORD_BOT_TOKEN=seu_token_aqui
   ```

---

## 🚀 **Execução**

### Execução Simples
```bash
python run.py
```

### Com Ambiente Virtual (Recomendado)
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

---

## 📊 **Comandos**

## 🔧 Configuração do Bot Discord

### Criando o Bot
1. Acesse o [Discord Developer Portal](https://discord.com/developers/applications)
2. Clique em "New Application"
3. Dê um nome ao seu bot (ex: "ARCA Bot")
4. Vá para a aba "Bot"
5. Clique em "Add Bot"
6. Copie o token e cole no arquivo `.env`

### Intents Necessários
Certifique-se de habilitar os seguintes intents no Developer Portal:
- ✅ Server Members Intent
- ✅ Message Content Intent

### Convite do Bot
Use este link para convidar o bot (substitua CLIENT_ID pelo ID da sua aplicação):
```
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=3165184&scope=bot
```

## 📁 **Estrutura do Projeto**

```
arca-bot/
├── 📁 config/              # Sistema de configuração centralizado
│   ├── settings.py         # Gerenciador de configurações
│   └── bot_config.json     # Configurações do bot
├── 📁 src/                 # Código fonte modular
│   ├── 📁 commands/        # Comandos organizados por categoria
│   │   ├── basic.py        # Comandos básicos (ping, info, help)
│   │   ├── economy.py      # Comandos de economia
│   │   └── lottery.py      # Comandos de sorteio
│   ├── 📁 core/            # Sistemas centrais
│   │   └── 📁 utils/       # Utilitários
│   │       ├── cache.py           # Sistema de cache
│   │       ├── permissions.py     # Sistema de permissões
│   │       ├── rate_limiter.py    # Rate limiting
│   │       └── wallet_panel.py    # Painel de carteiras
│   ├── 📁 modules/         # Lógica de negócio
│   │   ├── economy.py      # Sistema de economia
│   │   └── lottery.py      # Sistema de sorteios
│   └── main.py             # Entry point principal
├── 📁 tests/               # Suíte de testes
│   ├── test_bot.py         # Testes principais
│   ├── test_config.py      # Testes de configuração
│   └── test_new_structure.py # Testes da nova estrutura
├── 📁 scripts/             # Scripts de automação
│   ├── setup.bat          # Setup Windows
│   ├── setup.sh           # Setup Linux/Mac
│   └── test_installation.bat # Teste de instalação
├── 📁 data/                # Dados persistentes (criados automaticamente)
│   ├── economy_data.json   # Dados de economia
│   ├── lottery_data.json   # Dados de sorteios
│   └── panel_data.json     # Dados do painel (persistência)
├── 📁 backups/             # Backups automáticos
├── 📁 logs/                # Logs do sistema
├── run.py                  # Launcher principal
├── requirements.txt        # Dependências Python
├── pyproject.toml          # Configuração do projeto
├── .env.example           # Exemplo de variáveis de ambiente
├── .gitignore             # Arquivos ignorados pelo Git
└── README.md              # Este arquivo
```

---

## 🔧 **Configuração**

### Configuração Automática
O bot criará automaticamente um arquivo `config/bot_config.json` com configurações padrão na primeira execução.

### Canais Necessários
1. **Categoria**: `C.O.M.M.S OPS` com canais de voz para ganhar AC
2. **Canal**: `log-cargos` para logs de cargos  
3. **Canal**: `painel-carteiras` para o painel de carteiras em tempo real
4. **Canal**: `sorteios` para sorteios (opcional)

### Cargos Administrativos
- `ECONOMIA_ADMIN` - Para comandos de economia
- `SORTEIO_ADMIN` - Para criar sorteios  
- `ADMIN` - Para comandos administrativos gerais

### Permissões do Bot
- Ver canais e histórico de mensagens
- Enviar mensagens e usar embeds
- Conectar e ver canais de voz (monitoramento)
- Gerenciar mensagens (painel de carteiras)

---

## 📚 **Documentação**

### Como Funciona

#### Sistema de Economia (Arca Coins)
1. **Ganho por Tempo**: 20 AC por hora em canais da categoria "C.O.M.M.S OPS"
2. **Recompensa Diária**: 70-100 AC com comando `!diario` (precisa estar em canal de voz válido)
3. **Comandos Admin**: Distribuir AC para todos na call ou pagar usuários específicos
4. **Persistência**: Dados salvos em JSON com backup automático

#### Sistema de Sorteios
1. **Criação**: Admins criam sorteios com nome e valor base do ticket
2. **Participação**: Usuários compram tickets com AC (preço escalável)
3. **Sorteio**: Sistema justo que sorteia baseado na quantidade de tickets
4. **Segurança**: Reembolso automático em caso de cancelamento

#### Sistema de Painel de Carteiras
1. **Atualização Automática**: A cada 5 minutos no canal configurado
2. **Ranking Completo**: Mostra todos os usuários (não limitado)
3. **Persistência**: Sobrevive a reinicializações do bot
4. **Estatísticas**: Total em circulação, usuários ativos, distribuição

### Configuração do Discord Bot

#### Criando o Bot
1. Acesse o [Discord Developer Portal](https://discord.com/developers/applications)
2. Clique em "New Application"
3. Dê um nome ao seu bot (ex: "ARCA Bot")
4. Vá para a aba "Bot"
5. Clique em "Add Bot"
6. Copie o token e cole no arquivo `.env`

#### Intents Necessários
Certifique-se de habilitar os seguintes intents no Developer Portal:
- ✅ Server Members Intent
- ✅ Message Content Intent

#### Convite do Bot
Use este link para convidar o bot (substitua CLIENT_ID pelo ID da sua aplicação):
```
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=3165184&scope=bot
```

### Exemplos de Uso

#### Economia
```
# Usuário entra em canal "Ops Alpha" (categoria C.O.M.M.S OPS)
# Após 1 hora: +20 AC automático

# Comando diário estando no canal
!diario → Você recebeu 85 AC!

# Ver saldo
!saldo → Saldo: 105 AC | Total Ganho: 105 AC | Tempo em Voz: 60 min
```

#### Sorteio
```
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

## 🐛 **Troubleshooting**

### Bot não responde
- Verifique se o token está correto no arquivo `.env`
- Certifique-se de que o bot está online no servidor
- Verifique as permissões do bot

### Canal log-cargos não encontrado
- Crie um canal com o nome exato `log-cargos`
- Verifique se o bot tem permissão para ver e enviar mensagens no canal

### Painel de carteiras não funciona
- Crie um canal com o nome exato `painel-carteiras`
- Verifique se o bot tem permissão para gerenciar mensagens
- Verifique se os dados do painel estão sendo salvos em `data/panel_data.json`

### Erros de intents
- Habilite "Server Members Intent" no Discord Developer Portal
- Habilite "Message Content Intent" no Discord Developer Portal
- Reinicie o bot após habilitar os intents

---

## 📊 **Logs**

O bot mantém logs detalhados em:
- **Console**: Saída em tempo real
- **Arquivo**: Rotação automática em `logs/`

Níveis de log:
- `INFO`: Operações normais
- `WARNING`: Situações que merecem atenção
- `ERROR`: Erros que impedem operações

---

## 🔒 **Segurança**

- ⚠️ **NUNCA** compartilhe seu token do bot
- 🔐 Use arquivos `.env` para configurações sensíveis
- 🛡️ Mantenha as dependências atualizadas
- 🔍 Monitore os logs regularmente

---

## 🤝 **Contribuindo**

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

### 🔧 **Comandos Básicos**
| Comando | Descrição |
|---------|-----------|
| `!ping` | Testa a latência do bot |
| `!info` | Mostra informações sobre o bot |
| `!help` | Lista todos os comandos disponíveis |
| `!desligar` | Desliga o bot de forma segura | Admin |

### 💰 **Comandos de Economia**
| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `!saldo` | Mostra seu saldo de AC, total ganho e tempo em voz | Todos |
| `!diario` | Recompensa diária (70-100 AC) | Todos |
| `!distribuir <valor>` | Distribui AC para todos na mesma call | Economy Admin |
| `!pagar <@user> <valor>` | Gera e paga AC para um usuário específico | Economy Admin |
| `!remover <@user> <valor> [motivo]` | Remove AC de um usuário específico | Economy Admin |

### 🎲 **Comandos de Sorteio**
| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `!criarsorteio Nome \| Valor` | Cria um sorteio com botões interativos | Lottery Admin |
| Botões: 🎲 Sortear, 🎫 Comprar, ❌ Cancelar | Interação com sorteios criados | Todos |

### 🎛️ **Sistema de Painel**
| Recurso | Descrição |
|---------|-----------|
| **Painel Automático** | Atualização a cada 5 minutos no canal `painel-carteiras` |
| **Ranking Completo** | Mostra TODOS os usuários (não apenas top 10) |
| **Persistência** | Sobrevive a reinicializações do bot |
| **Estatísticas** | Total em circulação, usuários ativos, etc. |

### ⚡ **Sistemas Automáticos**
- **Ganho por Voz**: 20 AC por hora em canais da categoria "C.O.M.M.S OPS"
- **Log de Cargos**: Mensagens automáticas quando membros recebem novos cargos
- **Backup**: Backup automático dos dados a cada 6 horas
- **Rate Limiting**: Proteção automática contra spam de comandos
- **Cache**: Sistema de cache para melhor performance

---

## 🧪 **Testes**

### Executar Testes
```bash
# Windows
run_tests.bat

# Linux/Mac  
python -m pytest tests/ -v
```

### Estrutura de Testes
- `tests/test_bot.py` - Testes dos sistemas principais
- `tests/test_config.py` - Testes de configuração
- `tests/test_new_structure.py` - Testes da nova arquitetura

**⚠️ Nota:** Alguns testes precisam ser atualizados para a nova estrutura modular.

## 🐛 Troubleshooting

### Bot não responde
- Verifique se o token está correto no arquivo `.env`
- Certifique-se de que o bot está online no servidor
- Verifique as permissões do bot

### Canal log-cargos não encontrado
- Crie um canal com o nome exato `log-cargos`
- Verifique se o bot tem permissão para ver e enviar mensagens no canal

### Painel de carteiras não funciona
- Crie um canal com o nome exato `painel-carteiras`
- Verifique se o bot tem permissão para gerenciar mensagens
- Verifique se os dados do painel estão sendo salvos em `data/panel_data.json`

### Erros de intents
- Habilite "Server Members Intent" no Discord Developer Portal
- Habilite "Message Content Intent" no Discord Developer Portal
- Reinicie o bot após habilitar os intents

---

## 📊 Logs

O bot mantém logs detalhados em:
- **Console**: Saída em tempo real
- **Arquivo**: Rotação automática em `logs/`

Níveis de log:
- `INFO`: Operações normais
- `WARNING`: Situações que merecem atenção
- `ERROR`: Erros que impedem operações

---

## 🔒 Segurança

- ⚠️ **NUNCA** compartilhe seu token do bot
- 🔐 Use arquivos `.env` para configurações sensíveis
- 🛡️ Mantenha as dependências atualizadas
- 🔍 Monitore os logs regularmente

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🌟 Organização ARCA

Este bot foi desenvolvido para a organização ARCA no universo de Star Citizen. Para mais informações sobre a organização, visite nossos canais oficiais.

---

**Desenvolvido com ❤️ pela comunidade ARCA**

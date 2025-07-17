# 🚀 ARCA Bot v1.3.7
**Bot Discord multipropósito para a organização ARCA (Star Citizen)**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.3+-blue.svg)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)](tests/)

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
- **Ranking Automático** - Top usuários mais ricos
- **Atualização em Tempo Real** - Dados sempre atualizados
- **Display Elegante** - Interface visual atrativa

### 🔒 **Sistema de Permissões**
- **Hierarquia de Níveis** - Owner > Admin > Discord Admin > Economy Admin > User
- **Verificação Automática** - Checagem por cargos e permissões
- **Controle Granular** - Diferentes níveis para diferentes comandos

### ⚡ **Sistemas de Performance**
- **Cache Inteligente** - Sistema TTL para otimização
- **Rate Limiting** - Proteção contra spam
- **Logs Estruturados** - Sistema de logging avançado
- **Backup Automático** - Proteção de dados a cada 6 horas

---

## 🏗️ **Arquitetura**

### 📊 **Padrão de Arquitetura: Modular MVC**

```
ARCA Bot v1.3.7
├── 🎯 Core Systems (src/core/)
│   ├── ⚙️ Config Management
│   ├── 🗄️ Cache System  
│   ├── 🛡️ Rate Limiting
│   ├── 🔒 Permissions
│   └── 🎛️ Wallet Panel
├── 🧩 Modules (src/modules/)
│   ├── 💰 Economy System
│   └── 🎲 Lottery System
├── 🎮 Commands (src/commands/)
│   ├── 💳 Economy Commands
│   ├── 🎯 Lottery Commands
│   └── 🔧 Basic Commands
└── 🧪 Testing & Utils
    ├── 📊 Unit Tests
    ├── 📝 Documentation
    └── 🔧 Scripts
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

### 4. Configure o servidor Discord
1. **Crie os canais necessários:**
   - Categoria `C.O.M.M.S OPS` com canais de voz para ganhar AC
   - Canal de texto `log-cargos` para logs de cargos
   - Canal de texto `painel-carteiras` para o painel de carteiras em tempo real
   - Canal de texto `sorteios` para sorteios (opcional)

2. **Crie os cargos administrativos:**
   - `ECONOMIA_ADMIN` - Para comandos de economia
   - `SORTEIO_ADMIN` - Para criar sorteios
   - `ADMIN` - Para comandos administrativos gerais
   
3. **Certifique-se de que o bot tem as seguintes permissões:**
   - Ver canais
   - Enviar mensagens
   - Usar embeds
   - Ver histórico de mensagens
   - Conectar e ver canais de voz (para monitorar tempo)
   - Gerenciar mensagens (para painel de carteiras)

### 5. Configure o bot (Opcional)
O bot criará automaticamente um arquivo `config/bot_config.json` com configurações padrão.
Para personalizar, edite este arquivo conforme necessário.

### 6. Execute os testes (Recomendado)
```bash
# Windows
run_tests.bat

# Linux/Mac
python tests/test_bot.py
```

### 7. Execute o bot
```bash
python bot.py
```

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

## 📁 Estrutura do Projeto

```
arca-bot/
├── bot.py              # Arquivo principal do bot (refatorado)
├── economy.py          # Sistema de economia (Arca Coins)
├── lottery.py          # Sistema de sorteios
├── requirements.txt    # Dependências Python (atualizadas)
├── .env.example       # Exemplo de variáveis de ambiente
├── .gitignore         # Arquivos ignorados pelo Git
├── README.md          # Este arquivo
├── LICENSE            # Licença MIT
├── run_tests.bat      # Script para executar testes
├── config/            # 🆕 Sistema de configuração
│   ├── settings.py    # Gerenciador de configurações
│   └── bot_config.json # Configurações do bot
├── utils/             # 🆕 Utilitários centralizados
│   ├── cache.py       # Sistema de cache
│   ├── rate_limiter.py # Rate limiting
│   ├── permissions.py # Sistema de permissões
│   └── wallet_panel.py # Painel de carteiras
├── tests/             # 🆕 Testes unitários
│   └── test_bot.py    # Suite de testes
├── economy_data.json  # Dados de economia (criado automaticamente)
├── lottery_data.json  # Dados de sorteios (criado automaticamente)
├── backups/           # Pasta de backups automáticos
└── bot.log            # Logs do bot (criado automaticamente)
```

## 🎯 Como Funciona

### Monitoramento de Cargos
O bot utiliza o evento `on_member_update` para detectar quando um membro recebe um novo cargo:

1. **Detecção**: Compara os cargos antes e depois da atualização
2. **Filtro**: Ignora remoções de cargo, foca apenas em adições
3. **Log**: Envia uma mensagem formatada no canal `log-cargos`
4. **Formato**: Embed elegante com informações do membro e cargo

### Sistema de Economia (Arca Coins)
Sistema completo de moeda virtual para a organização:

1. **Ganho por Tempo**: 20 AC por hora em canais da categoria "C.O.M.M.S OPS"
2. **Recompensa Diária**: 70-100 AC com comando `!diario` (precisa estar em canal de voz válido)
3. **Comandos Admin**: Distribuir AC para todos na call ou pagar usuários específicos
4. **Persistência**: Dados salvos em JSON com backup automático

### Sistema de Sorteios
Interface completa para sorteios organizacionais:

1. **Criação**: Admins criam sorteios com nome e valor base do ticket
2. **Participação**: Usuários compram tickets com AC (preço escalável)
3. **Sorteio**: Sistema justo que sorteia baseado na quantidade de tickets
4. **Segurança**: Reembolso automático em caso de cancelamento

### Exemplo de Uso - Economia
```
# Usuário entra em canal "Ops Alpha" (categoria C.O.M.M.S OPS)
# Após 1 hora: +20 AC automático

# Comando diário estando no canal
!diario → Você recebeu 85 AC!

# Ver saldo
!saldo → Saldo: 105 AC | Total Ganho: 105 AC | Tempo em Voz: 60 min
```

### Exemplo de Uso - Sorteio
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

### Exemplo de Mensagem de Log
```
🎉 Novo Cargo Atribuído
João recebeu o cargo Piloto!

Membro: @João
        João#1234
Cargo:  @Piloto
        Piloto
Servidor: ARCA Organization
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📝 Comandos Disponíveis

### 🔧 Comandos Básicos
| Comando | Descrição |
|---------|-----------|
| `!ping` | Testa a latência do bot |
| `!info` | Mostra informações sobre o bot |
| `!help` | Lista todos os comandos disponíveis |

### 💰 Comandos de Economia
| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `!saldo` | Mostra seu saldo de AC, total ganho e tempo em voz | Todos |
| `!diario` | Recompensa diária | Todos |

### 🎲 Comandos de Sorteio
| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| Botões: 🎲 Sortear, 🎫 Comprar, ❌ Cancelar | Interact com sorteios criados por admins | Todos |

### 📊 Comandos de Painel
| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `!painel status` | Ver status do sistema de painel | Todos |
| `!painel config` | Ver configuração atual | Todos |
| `!painel atualizar` | Forçar atualização do painel | Admin |
| `!painel criar` | Criar painel no canal configurado | Admin |

### 👑 Comandos Administrativos
| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `!distribuir <valor>` | Distribui AC para todos na mesma call | Economy Admin |
| `!pagar <@user> <valor>` | Gera e paga AC para um usuário específico | Economy Admin |
| `!remover <@user> <valor> [motivo]` | Remove AC de um usuário específico | Economy Admin |
| `!criarsorteio Nome \| Valor` | Cria um sorteio com botões interativos | Lottery Admin |
| `!cache [ação]` | Gerencia o sistema de cache | Admin |
| `!desligar` | Desliga o bot de forma segura | Admin |

**Botões do Sorteio:**
- 🎲 **Sortear**: Realiza o sorteio entre os participantes
- 🎫 **Comprar**: Compra um ticket com AC (preço escalável)
- ❌ **Cancelar**: Cancela o sorteio e reembolsa participantes

**Comando de Administração:**
- `!desligar` (aliases: `!shutdown`, `!off`): Desliga o bot de forma segura, mostrando estatísticas da sessão e uptime

### ⚡ Sistema Automático
- **Ganho por Voz**: 20 AC por hora em canais da categoria "C.O.M.M.S OPS"
- **Log de Cargos**: Mensagens automáticas quando membros recebem novos cargos
- **Painel de Carteiras**: Atualização automática a cada 5 minutos com ranking e estatísticas
- **Backup**: Backup automático dos dados a cada 6 horas
- **Rate Limiting**: Proteção automática contra spam de comandos
- **Cache**: Sistema de cache para melhor performance

## 🐛 Troubleshooting

### Bot não responde
- Verifique se o token está correto no arquivo `.env`
- Certifique-se de que o bot está online no servidor
- Verifique as permissões do bot

### Canal log-cargos não encontrado
- Crie um canal com o nome exato `log-cargos`
- Verifique se o bot tem permissão para ver e enviar mensagens no canal

### Erros de intents
- Habilite "Server Members Intent" no Discord Developer Portal
- Reinicie o bot após habilitar os intents

## 📊 Logs

O bot mantém logs detalhados em:
- **Console**: Saída em tempo real
- **Arquivo**: `bot.log` (rotação automática)

Níveis de log:
- `INFO`: Operações normais
- `WARNING`: Situações que merecem atenção
- `ERROR`: Erros que impedem operações

## 🔒 Segurança

- ⚠️ **NUNCA** compartilhe seu token do bot
- 🔐 Use arquivos `.env` para configurações sensíveis
- 🛡️ Mantenha as dependências atualizadas
- 🔍 Monitore os logs regularmente

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🌟 Organização ARCA

Este bot foi desenvolvido para a organização ARCA no universo de Star Citizen. Para mais informações sobre a organização, visite nossos canais oficiais.

---

**Desenvolvido com ❤️ pela comunidade ARCA**
Multipurpose Discord bot for ARCA, a Star Citizen organization. Handles role tracking, moderation, and operation planning. Built to support community management, events, and future automation needs

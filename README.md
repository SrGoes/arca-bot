# 🚀 ARCA Bot

Bot Discord multipropósito para a organização ARCA relacionada ao jogo Star Citizen.

## 📋 Funcionalidades

### ✅ Implementadas
- **Monitoramento de Cargos**: Detecta quando membros recebem novos cargos e registra no canal `log-cargos`
- **Sistema de Economia (Arca Coins)**: Moeda virtual com múltiplas formas de ganho
  - 20 AC por hora em canais de voz da categoria "C.O.M.M.S OPS"
  - Recompensa diária de 70-100 AC (comando `!diario`)
  - Comandos administrativos para distribuir e pagar AC
- **Sistema de Sorteios**: Criação e participação em sorteios com tickets escaláveis
  - Preço dos tickets aumenta: `1,1^(qty-1) × preço_base`
  - Interface com botões para sortear, comprar e cancelar
  - Reembolso automático em caso de cancelamento
- **Suporte Multi-Servidor**: Funciona em múltiplos servidores Discord simultaneamente
- **Sistema de Backup**: Backup automático dos dados a cada 6 horas
- **Logs Detalhados**: Sistema de logging completo com arquivos de log
- **Comandos Intuitivos**: Interface amigável com embeds elegantes

### 🔄 Planejadas
- Sistema de comandos expandido
- Gerenciamento de eventos
- Integração com APIs do Star Citizen
- Sistema de economia/pontos

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- Conta Discord Developer
- Bot Discord criado no Discord Developer Portal

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

### 4. Configure o servidor Discord
1. **Crie os canais necessários:**
   - Categoria `C.O.M.M.S OPS` com canais de voz para ganhar AC
   - Canal de texto `log-cargos` para logs de cargos
   - Canal de texto `sorteios` para sorteios (opcional)

2. **Crie os cargos administrativos:**
   - `ECONOMIA_ADMIN` - Para comandos de economia
   - `SORTEIO_ADMIN` - Para criar sorteios
   
3. **Certifique-se de que o bot tem as seguintes permissões:**
   - Ver canais
   - Enviar mensagens
   - Usar embeds
   - Ver histórico de mensagens
   - Conectar e ver canais de voz (para monitorar tempo)

### 5. Execute o bot
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
├── bot.py              # Arquivo principal do bot
├── economy.py          # Sistema de economia (Arca Coins)
├── lottery.py          # Sistema de sorteios
├── requirements.txt    # Dependências Python
├── config.example.py   # Exemplo de configuração
├── .env.example       # Exemplo de variáveis de ambiente
├── .gitignore         # Arquivos ignorados pelo Git
├── README.md          # Este arquivo
├── DOCS.md            # Documentação técnica detalhada
├── LICENSE            # Licença MIT
├── test_config.py     # Script de teste de configuração
├── setup.bat          # Script de instalação (Windows)
├── setup.sh           # Script de instalação (Linux/Mac)
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
| `!diario` | Recompensa diária de 70-100 AC (precisa estar em canal de voz válido) | Todos |
| `!distribuir <valor>` | Distribui AC para todos na mesma call | Admin |
| `!pagar <@user> <valor>` | Gera e paga AC para um usuário específico | Admin |

### 🎲 Comandos de Sorteio
| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `!criarsorteio Nome \| Valor` | Cria um sorteio com botões interativos | Admin |

**Botões do Sorteio:**
- 🎲 **Sortear**: Realiza o sorteio entre os participantes
- 🎫 **Comprar**: Compra um ticket com AC (preço escalável)
- ❌ **Cancelar**: Cancela o sorteio e reembolsa participantes

### ⚡ Sistema Automático
- **Ganho por Voz**: 20 AC por hora em canais da categoria "C.O.M.M.S OPS"
- **Log de Cargos**: Mensagens automáticas quando membros recebem novos cargos
- **Backup**: Backup automático dos dados a cada 6 horas

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

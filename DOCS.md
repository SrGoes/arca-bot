# 📚 Documentação ARCA Bot

## Índice
- [Configuração Inicial](#configuração-inicial)
- [Estrutura do Código](#estrutura-do-código)
- [Eventos Monitorados](#eventos-monitorados)
- [Expansão do Bot](#expansão-do-bot)
- [Troubleshooting](#troubleshooting)

## Configuração Inicial

### 1. Criando o Bot no Discord

1. Acesse [Discord Developer Portal](https://discord.com/developers/applications)
2. Clique em "New Application"
3. Nome: "ARCA Bot" (ou seu preferido)
4. Vá para "Bot" > "Add Bot"
5. **Importante**: Habilite os seguintes intents:
   - `Server Members Intent` ✅
   - `Message Content Intent` ✅

### 2. Configurando Permissões

O bot precisa das seguintes permissões no servidor:
```
Permissões necessárias:
├── Ver Canais (View Channels)
├── Enviar Mensagens (Send Messages)  
├── Incorporar Links (Embed Links)
├── Anexar Arquivos (Attach Files)
├── Ver Histórico de Mensagens (Read Message History)
└── Usar Emojis Externos (Use External Emojis)
```

Link de convite (substitua CLIENT_ID):
```
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=379968&scope=bot
```

### 3. Configuração do Servidor

Crie um canal chamado `log-cargos`:
1. Clique com botão direito no servidor
2. "Criar Canal" > "Canal de Texto"
3. Nome: `log-cargos`
4. Certifique-se de que o bot tem acesso

## Estrutura do Código

### Classe Principal: ARCABot

```python
class ARCABot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True      # Para on_member_update
        intents.guilds = True       # Para informações do servidor
        intents.message_content = True  # Para comandos
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='Bot ARCA para Star Citizen'
        )
```

### Eventos Principais

#### on_ready()
- Executado quando o bot conecta
- Configura status e atividade
- Lista servidores conectados

#### on_member_update()
- **Função principal** do bot
- Detecta mudanças em membros
- Filtra apenas adição de cargos
- Envia log para canal específico

#### on_guild_join/remove()
- Monitora entrada/saída de servidores
- Registra nos logs

## Eventos Monitorados

### Detecção de Novos Cargos

O bot funciona da seguinte forma:

```python
async def on_member_update(self, before: discord.Member, after: discord.Member):
    # 1. Verificar se houve mudança nos cargos
    if before.roles == after.roles:
        return
    
    # 2. Encontrar cargos adicionados (não removidos)
    added_roles = set(after.roles) - set(before.roles)
    
    # 3. Se não há cargos adicionados, ignorar
    if not added_roles:
        return
    
    # 4. Buscar canal de log
    log_channel = await self.get_log_channel(after.guild)
    
    # 5. Enviar mensagem para cada cargo adicionado
    for role in added_roles:
        embed = self.create_role_log_embed(after, role)
        await log_channel.send(embed=embed)
```

### Formato da Mensagem de Log

```
┌─────────────────────────────────────┐
│ 🎉 Novo Cargo Atribuído             │
│ João recebeu o cargo Piloto!        │
├─────────────────────────────────────┤
│ Membro:    @João                    │
│            João#1234                │
│ Cargo:     @Piloto                  │
│            Piloto                   │
│ Servidor:  ARCA Organization        │
└─────────────────────────────────────┘
ARCA Bot | Star Citizen • hoje às 14:30
```

## Expansão do Bot

### Adicionando Novos Comandos

```python
@bot.command(name='meucomando')
async def meu_comando(ctx, *, argumento=None):
    """Descrição do comando"""
    if not argumento:
        await ctx.send("❌ Forneça um argumento!")
        return
    
    embed = discord.Embed(
        title="✅ Comando Executado",
        description=f"Argumento recebido: {argumento}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
```

### Adicionando Novos Eventos

```python
@bot.event
async def on_message(message):
    # Ignorar mensagens do próprio bot
    if message.author == bot.user:
        return
    
    # Processar comandos
    await bot.process_commands(message)
    
    # Lógica adicional aqui
    if "star citizen" in message.content.lower():
        await message.add_reaction("🚀")
```

### Estrutura Modular (Futuro)

Para um bot maior, considere esta estrutura:

```
arca-bot/
├── bot.py                 # Arquivo principal
├── cogs/                  # Módulos do bot
│   ├── __init__.py
│   ├── roles.py          # Comandos de cargos
│   ├── events.py         # Gerenciamento de eventos
│   ├── moderation.py     # Comandos de moderação
│   └── starcitizen.py    # Integração Star Citizen
├── utils/                # Utilitários
│   ├── __init__.py
│   ├── database.py       # Conexão com banco
│   ├── embeds.py         # Templates de embeds
│   └── permissions.py    # Sistema de permissões
└── config/               # Configurações
    ├── settings.py       # Configurações gerais
    └── secrets.py        # Tokens e chaves
```

## Comandos Disponíveis

### !ping
Testa a conectividade do bot
```
Uso: !ping
Resposta: 🏓 Pong! Latência: 45ms
```

### !info
Mostra estatísticas do bot
```
Uso: !info
Resposta: 
├── Servidores: 3
├── Membros: 1,247
└── Latência: 45ms
```

## Troubleshooting

### Problemas Comuns

#### ❌ Bot não inicia
```
Erro: discord.errors.LoginFailure
Solução: Verificar token no arquivo .env
```

#### ❌ Canal não encontrado
```
Warning: Canal "log-cargos" não encontrado
Solução: 
1. Criar canal com nome exato "log-cargos"
2. Dar permissões ao bot no canal
```

#### ❌ Intents não habilitados
```
Erro: Intents not enabled
Solução: 
1. Discord Developer Portal > Bot
2. Habilitar "Server Members Intent"
3. Reiniciar o bot
```

#### ❌ Sem permissões
```
Erro: discord.errors.Forbidden
Solução:
1. Verificar permissões do bot no servidor
2. Bot precisa enviar mensagens e embeds
```

### Logs e Debugging

#### Verificar logs do bot:
```bash
# Logs em tempo real
tail -f bot.log

# Últimas 50 linhas
tail -50 bot.log

# Filtrar erros
grep "ERROR" bot.log
```

#### Níveis de log:
- `INFO`: Operações normais
- `WARNING`: Situações que merecem atenção  
- `ERROR`: Erros que impedem operações

### Testando o Bot

#### 1. Teste de conectividade:
```
!ping
```

#### 2. Teste de informações:
```
!info
```

#### 3. Teste de detecção de cargos:
- Adicione um cargo a um membro
- Verifique se aparece no canal `log-cargos`

## Performance e Otimização

### Recomendações:
- Use `discord.py[speed]` para melhor performance
- Implemente cache para dados frequentemente acessados
- Use tasks para operações periódicas
- Monitore uso de RAM e CPU

### Exemplo de Task Periódica:
```python
from discord.ext import tasks

@tasks.loop(hours=1)
async def backup_logs():
    """Backup dos logs a cada hora"""
    # Lógica de backup
    pass

@backup_logs.before_loop
async def before_backup():
    await bot.wait_until_ready()
```

## Próximos Passos

### Funcionalidades Planejadas:
1. **Sistema de Comandos Expandido**
   - Comandos de moderação
   - Sistema de permissões por cargo
   - Comandos específicos do Star Citizen

2. **Integração Star Citizen**
   - API do RSI
   - Verificação de organização
   - Status de naves

3. **Sistema de Eventos**
   - Criação de eventos
   - Sistema de inscrições
   - Lembretes automáticos

4. **Dashboard Web**
   - Interface de administração
   - Estatísticas em tempo real
   - Configuração via web

5. **Sistema de Economia**
   - Pontos por atividade
   - Loja virtual
   - Rankings

---

**Para mais informações, consulte o código-fonte ou abra uma issue no GitHub.**

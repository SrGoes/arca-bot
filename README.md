# 🚀 ARCA Bot

Bot Discord multipropósito para a organização ARCA relacionada ao jogo Star Citizen.

## 📋 Funcionalidades

### ✅ Implementadas
- **Monitoramento de Cargos**: Detecta quando membros recebem novos cargos e registra no canal `log-cargos`
- **Suporte Multi-Servidor**: Funciona em múltiplos servidores Discord simultaneamente
- **Logs Detalhados**: Sistema de logging completo com arquivos de log
- **Embeds Elegantes**: Mensagens formatadas com embeds coloridos
- **Comandos Básicos**: `!ping` e `!info` para teste e informações

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
1. Crie um canal chamado `log-cargos` no seu servidor
2. Certifique-se de que o bot tem as seguintes permissões:
   - Ver canais
   - Enviar mensagens
   - Usar embeds
   - Ver histórico de mensagens

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
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=379968&scope=bot
```

## 📁 Estrutura do Projeto

```
arca-bot/
├── bot.py              # Arquivo principal do bot
├── requirements.txt    # Dependências Python
├── .env.example       # Exemplo de configuração
├── .gitignore         # Arquivos ignorados pelo Git
├── README.md          # Este arquivo
├── LICENSE            # Licença MIT
└── bot.log            # Logs do bot (criado automaticamente)
```

## 🎯 Como Funciona

### Monitoramento de Cargos
O bot utiliza o evento `on_member_update` para detectar quando um membro recebe um novo cargo:

1. **Detecção**: Compara os cargos antes e depois da atualização
2. **Filtro**: Ignora remoções de cargo, foca apenas em adições
3. **Log**: Envia uma mensagem formatada no canal `log-cargos`
4. **Formato**: Embed elegante com informações do membro e cargo

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

| Comando | Descrição |
|---------|-----------|
| `!ping` | Testa a latência do bot |
| `!info` | Mostra informações sobre o bot |

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

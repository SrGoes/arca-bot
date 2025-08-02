# Arca Bot

Bot do Discord para a Arca com sistema de economia e sorteios.

> [!WARNING]
> [NodeJs](https://nodejs.org/en) versão necessária: 20.12 ou superior

## 🚀 Configuração

### 1. Variáveis de Ambiente

Copie o arquivo de exemplo e configure suas variáveis:

```bash
cp .env.example .env
```

Configure as seguintes variáveis no arquivo `.env`:

```bash
BOT_TOKEN=seu_token_do_bot
NODE_OPTIONS=--max-old-space-size=2048
LOG_LEVEL=2
VOICE_DEBUG=false
WEBHOOK_LOGS_URL=sua_webhook_url_opcional
```

### 2. Execução Local

```bash
# Instalar dependências
npm install

# Desenvolvimento (com hot reload)
npm run dev

# Build e produção
npm run build
npm start
```

## 🐳 Docker

### Usando Scripts de Gerenciamento

**Windows (PowerShell):**
```powershell
# Iniciar bot em background
.\docker-manage.ps1 start

# Ver logs
.\docker-manage.ps1 logs

# Parar bot
.\docker-manage.ps1 stop

# Reiniciar bot
.\docker-manage.ps1 restart

# Ver status
.\docker-manage.ps1 status
```

**Linux/macOS (Bash):**
```bash
# Dar permissão de execução
chmod +x docker-manage.sh

# Iniciar bot em background
./docker-manage.sh start

# Ver logs
./docker-manage.sh logs

# Parar bot
./docker-manage.sh stop
```

### Comandos Docker Manuais

```bash
# Build da imagem
docker build -t arca-bot .

# Executar com docker-compose
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar containers
docker-compose down
```

## 📁 Scripts Disponíveis

- `dev`: executa o bot em desenvolvimento com hot reload
- `build`: compila o projeto TypeScript
- `watch`: executa em modo watch para desenvolvimento
- `start`: executa o bot compilado
- `docker:build`: build da imagem Docker
- `docker:run`: executa com docker-compose
- `docker:stop`: para os containers
- `docker:logs`: exibe os logs

## 🔧 Resolução de Problemas

### Docker não inicia

1. **Verifique o arquivo .env:**
   ```bash
   # Certifique-se de que o BOT_TOKEN está configurado
   cat .env | grep BOT_TOKEN
   ```

2. **Verifique se o Docker está rodando:**
   ```bash
   docker --version
   docker-compose --version
   ```

3. **Rebuild da imagem:**
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

4. **Ver logs de erro:**
   ```bash
   docker-compose logs arca-bot
   ```

### Permissões no Linux

```bash
# Dar permissões para dados
sudo chown -R $USER:$USER ./data

# Dar permissão para script
chmod +x docker-manage.sh
```

## 🏗️ Estruturas

- [Comandos](src/discord/commands/): Comandos slash do Discord
- [Responders](src/discord/responders/): Respostas a interações (botões, selects)
- [Events](src/discord/events/): Eventos do Discord
- [Database](src/database/): Sistema de banco de dados local
- [Settings](src/settings/): Configurações do bot
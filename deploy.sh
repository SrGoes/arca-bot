#!/bin/bash

# Script de deployment para AWS EC2
# Execute este script na sua instância EC2

set -e

echo "🚀 Iniciando deployment do Arca Bot na AWS..."

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "📦 Instalando Docker..."
    sudo apt-get update
    sudo apt-get install -y docker.io docker-compose
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo "✅ Docker instalado com sucesso!"
fi

# Verificar se o repositório já existe
if [ ! -d "arca-bot" ]; then
    echo "📥 Clonando repositório..."
    git clone https://github.com/SrGoes/arca-bot.git
    cd arca-bot
else
    echo "🔄 Atualizando repositório..."
    cd arca-bot
    git pull origin main
fi

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📝 Criando .env a partir do template..."
    cp .env.example .env
    echo ""
    echo "🔧 Por favor, edite o arquivo .env com suas configurações:"
    echo "   - BOT_TOKEN: Token do seu bot Discord"
    echo "   - LOG_LEVEL: Nível de logs (3 é recomendado)"
    echo "   - WEBHOOK_LOGS_URL: URL do webhook para logs (opcional)"
    echo ""
    echo "Execute: nano .env"
    echo "Depois execute novamente este script."
    exit 1
fi

# Verificar se o BOT_TOKEN está configurado
if grep -q "your_discord_bot_token_here" .env; then
    echo "❌ BOT_TOKEN não foi configurado no arquivo .env"
    echo "🔧 Por favor, edite o arquivo .env com o token real do seu bot."
    echo "Execute: nano .env"
    exit 1
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down 2>/dev/null || true

# Criar diretório de dados se não existir
mkdir -p data/backups

# Build e start dos containers
echo "🏗️  Construindo e iniciando containers..."
docker-compose up -d --build

# Verificar se o container está rodando
echo "🔍 Verificando status do container..."
sleep 5

if docker-compose ps | grep -q "Up"; then
    echo "✅ Arca Bot deployado com sucesso!"
    echo ""
    echo "📊 Status dos containers:"
    docker-compose ps
    echo ""
    echo "📝 Para ver os logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Para parar o bot:"
    echo "   docker-compose down"
    echo ""
    echo "🔄 Para atualizar o bot:"
    echo "   git pull && docker-compose up -d --build"
else
    echo "❌ Falha no deployment. Verificando logs..."
    docker-compose logs
    exit 1
fi

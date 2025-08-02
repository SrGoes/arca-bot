#!/bin/sh

# Script de inicialização para Docker
echo "🐳 Iniciando Arca Bot..."

# Verificar se as variáveis necessárias estão definidas
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ Erro: BOT_TOKEN não definido"
    exit 1
fi

# Criar diretórios necessários
mkdir -p /app/data/backups
mkdir -p /app/logs

# Verificar se a build existe
if [ ! -d "/app/build" ]; then
    echo "❌ Erro: Diretório build não encontrado"
    exit 1
fi

# Verificar se o arquivo principal existe
if [ ! -f "/app/build/index.js" ]; then
    echo "❌ Erro: Arquivo build/index.js não encontrado"
    exit 1
fi

echo "✅ Iniciando bot..."
exec node --env-file .env build/index.js

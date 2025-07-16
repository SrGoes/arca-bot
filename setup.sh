#!/bin/bash
echo "🚀 ARCA Bot - Instalação e Configuração"
echo

echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python não encontrado! Por favor, instale Python 3.8 ou superior."
    exit 1
fi

python3 --version
echo

echo "Instalando dependências..."
pip3 install -r requirements.txt

echo
echo "Verificando arquivo .env..."
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env a partir do exemplo..."
    cp .env.example .env
    echo
    echo "⚠️  IMPORTANTE: Edite o arquivo .env e adicione seu token do bot!"
    echo "   DISCORD_BOT_TOKEN=seu_token_aqui"
    echo
else
    echo "✅ Arquivo .env já existe."
fi

echo
echo "📋 Próximos passos:"
echo "1. Edite o arquivo .env com seu token do Discord"
echo "2. Crie um canal chamado 'log-cargos' no seu servidor Discord"
echo "3. Execute: python3 bot.py"
echo
echo "🔗 Links úteis:"
echo "- Discord Developer Portal: https://discord.com/developers/applications"
echo "- Documentação discord.py: https://discordpy.readthedocs.io/"
echo

read -p "Pressione Enter para continuar..."

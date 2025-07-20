#!/bin/bash
echo "🚀 ARCA Bot - Instalação e Configuração"
echo

# Ir para a pasta do projeto (pasta pai)
cd "$(dirname "$0")/.."

echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python não encontrado! Por favor, instale Python 3.13 ou superior."
    exit 1
fi

python3 --version
echo

echo "Verificando requirements.txt..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ Arquivo requirements.txt não encontrado na raiz do projeto!"
    echo "Certifique-se de que o arquivo existe na pasta raiz."
    exit 1
fi

echo "✅ requirements.txt encontrado."
echo
echo "Instalando dependências..."
pip3 install -r requirements.txt

echo
echo "Verificando estrutura do projeto..."
if [ ! -f "src/main.py" ]; then
    echo "❌ Estrutura do projeto incorreta! Arquivo src/main.py não encontrado."
    exit 1
fi
if [ ! -f "run.py" ]; then
    echo "❌ Arquivo launcher run.py não encontrado!"
    exit 1
fi
echo "✅ Estrutura do projeto verificada."

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
echo "2. Configure seu servidor Discord:"
echo "   - Crie categoria 'C.O.M.M.S OPS' com canais de voz"
echo "   - Crie canal de texto 'log-cargos'"
echo "   - Crie canal de texto 'painel-carteiras'"
echo "   - Crie cargos: 'ECONOMIA_ADMIN', 'SORTEIO_ADMIN', 'ADMIN'"
echo "3. Execute: python3 run.py"
echo
echo "🔗 Links úteis:"
echo "- Discord Developer Portal: https://discord.com/developers/applications"
echo "- Documentação discord.py: https://discordpy.readthedocs.io/"
echo "- README completo: README.md"
echo

read -p "Pressione Enter para continuar..."

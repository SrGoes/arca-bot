@echo off
echo 🚀 ARCA Bot - Instalação e Configuração
echo.

echo Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado! Por favor, instale Python 3.8 ou superior.
    pause
    exit /b 1
)

echo.
echo Instalando dependências...
pip install -r requirements.txt

echo.
echo Verificando arquivo .env...
if not exist .env (
    echo 📝 Criando arquivo .env a partir do exemplo...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANTE: Edite o arquivo .env e adicione seu token do bot!
    echo    DISCORD_BOT_TOKEN=seu_token_aqui
    echo.
) else (
    echo ✅ Arquivo .env já existe.
)

echo.
echo 📋 Próximos passos:
echo 1. Edite o arquivo .env com seu token do Discord
echo 2. Crie um canal chamado 'log-cargos' no seu servidor Discord
echo 3. Execute: python bot.py
echo.
echo 🔗 Links úteis:
echo - Discord Developer Portal: https://discord.com/developers/applications
echo - Documentação discord.py: https://discordpy.readthedocs.io/
echo.

pause

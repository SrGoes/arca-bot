@echo off
echo 🚀 ARCA Bot - Instalação e Configuração
echo.

:: Ir para a pasta do projeto (pasta pai)
cd /d "%~dp0.."

echo Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado! Por favor, instale Python 3.8 ou superior.
    pause
    exit /b 1
)
    exit /b 1
)

echo.
echo Instalando dependências...
pip install -r requirements.txt

echo.
echo Verificando estrutura do projeto...
if not exist "src\main.py" (
    echo ❌ Estrutura do projeto incorreta! Arquivo src\main.py não encontrado.
    pause
    exit /b 1
)
if not exist "run.py" (
    echo ❌ Arquivo launcher run.py não encontrado!
    pause
    exit /b 1
)
echo ✅ Estrutura do projeto verificada.

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
echo 2. Configure seu servidor Discord:
echo    - Crie categoria 'C.O.M.M.S OPS' com canais de voz
echo    - Crie canal de texto 'log-cargos'
echo    - Crie canal de texto 'painel-carteiras' 
echo    - Crie cargos: 'ECONOMIA_ADMIN', 'SORTEIO_ADMIN', 'ADMIN'
echo 3. Execute: python run.py
echo.
echo 🔗 Links úteis:
echo - Discord Developer Portal: https://discord.com/developers/applications
echo - Documentação discord.py: https://discordpy.readthedocs.io/
echo - README completo: README.md
echo.

pause

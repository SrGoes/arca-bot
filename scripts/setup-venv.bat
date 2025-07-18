@echo off
echo.
echo ======================================
echo    ARCA Bot - Instalacao Automatica
echo ======================================
echo.

REM Ir para a pasta do projeto
cd /d "%~dp0.."

REM Verificar se Python 3.13 esta instalado
py -3.13 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3.13 nao encontrado!
    echo 📝 Instale Python 3.13+ em: https://python.org
    pause
    exit /b 1
)

echo ✅ Python 3.13 encontrado!
py -3.13 --version

REM Verificar se pip esta instalado
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip nao encontrado!
    echo 📝 Reinstale Python com pip incluido
    pause
    exit /b 1
)

echo ✅ pip encontrado!

REM Criar ambiente virtual
echo.
echo 🔧 Criando ambiente virtual...
py -3.13 -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Erro ao criar ambiente virtual!
    pause
    exit /b 1
)

REM Ativar ambiente virtual
echo 🔧 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Atualizar pip
echo 🔧 Atualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo 🔧 Instalando dependencias...
pip install -r requirements.txt

REM Instalar dependencias de desenvolvimento (opcional)
echo.
choice /C YN /M "Instalar dependencias de desenvolvimento (testes, formatacao)? [Y/N]: "
if %errorlevel%==1 (
    echo 🔧 Instalando dependencias de desenvolvimento...
    pip install -r requirements-dev.txt
)

REM Verificar se arquivo .env existe
if not exist .env (
    echo.
    echo 📝 Arquivo .env nao encontrado!
    echo 🔧 Copiando .env.example para .env...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANTE: Edite o arquivo .env e configure seu token do Discord!
    echo    Abra o arquivo .env e substitua "seu_token_aqui" pelo token real
    echo.
)

REM Executar testes rapidos
echo.
choice /C YN /M "Executar testes de instalacao? [Y/N]: "
if %errorlevel%==1 (
    echo 🧪 Executando testes...
    python -m pytest tests/test_new_structure.py -v
)

echo.
echo ✅ Instalacao concluida!
echo.
echo 📋 Proximos passos:
echo    1. Configure seu token no arquivo .env
echo    2. Execute: venv\Scripts\activate.bat
echo    3. Depois execute: python run.py
echo.
echo 🔗 Links uteis:
echo    - Discord Developer Portal: https://discord.com/developers/applications
echo    - Documentacao: README.md
echo.
pause

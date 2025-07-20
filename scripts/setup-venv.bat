@echo off
echo.
echo ======================================
echo    ARCA Bot - Instalacaecho.
echo ✅ Instalacao concluida!
echo.
echo 🔧 Verificando configuracao AWS Windows...
echo    - Firewall: Nao precisa configurar (conexoes outbound apenas)
echo    - Antivirus: Adicione excecao para pasta do bot se necessario
echo    - Memoria: Minimo 2GB RAM recomendado
echo.
echo 🌐 Testando conectividade Discord...
python -c "import requests; r=requests.get('https://discord.com/api/v10/gateway', timeout=10); print('✅ Discord API acessivel' if r.status_code==200 else '❌ Problema de conectividade')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Nao foi possivel testar conectividade Discord
    echo    Verifique se o Security Group permite HTTPS outbound
)
echo.
echo 📋 Proximos passos:ica
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
if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependencias!
    echo 💡 Verifique sua conexao com a internet
    echo 💡 No AWS, verifique se tem acesso ao PyPI
    pause
    exit /b 1
)

echo ✅ Todas as dependencias instaladas com sucesso!

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
if exist tests\test_new_structure.py (
    choice /C YN /M "Executar testes de instalacao? [Y/N]: "
    if %errorlevel%==1 (
        echo 🧪 Executando testes...
        python -m pytest tests/test_new_structure.py -v
        if %errorlevel% neq 0 (
            echo ⚠️  Alguns testes falharam, mas a instalacao esta OK
        )
    )
) else (
    echo ⚠️  Arquivo de teste nao encontrado, pulando testes...
)

echo.
echo ✅ Instalacao concluida!
echo.
echo � Verificando configuracao AWS Windows...
echo    - Firewall: Nao precisa configurar (conexoes outbound apenas)
echo    - Antivirus: Adicione excecao para pasta do bot se necessario
echo    - Memoria: Minimo 2GB RAM recomendado
echo.
echo �📋 Proximos passos:
echo    1. Configure seu token no arquivo .env
echo    2. Execute: venv\Scripts\activate.bat
echo    3. Depois execute: python run.py
echo.
echo 💡 Para rodar como servico Windows:
echo    1. Instale NSSM: choco install nssm
echo    2. Crie servico: nssm install "ARCA-Bot" "%CD%\venv\Scripts\python.exe" "%CD%\run.py"
echo    3. Inicie: nssm start "ARCA-Bot"
echo.
echo 🔗 Links uteis:
echo    - Discord Developer Portal: https://discord.com/developers/applications
echo    - Documentacao: README.md
echo.
pause

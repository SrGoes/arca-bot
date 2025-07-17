@echo off
echo 🧪 ARCA Bot - Teste Rápido de Instalação
echo.

:: Ir para a pasta do projeto (pasta pai)
cd /d "%~dp0.."

echo Testando estrutura do projeto...
if not exist "src\main.py" (
    echo ❌ ERRO: src\main.py não encontrado
    pause
    exit /b 1
)
if not exist "run.py" (
    echo ❌ ERRO: run.py não encontrado  
    pause
    exit /b 1
)
if not exist "requirements.txt" (
    echo ❌ ERRO: requirements.txt não encontrado
    pause
    exit /b 1
)
echo ✅ Estrutura do projeto OK

echo.
echo Testando imports Python...
python -c "import sys; sys.path.insert(0, 'src'); from main import ARCABot; print('✅ Main bot importado com sucesso')"
if %errorlevel% neq 0 (
    echo ❌ ERRO: Falha ao importar módulos principais
    pause
    exit /b 1
)

echo.
echo Testando sistema de configuração...
python -c "import sys, os; sys.path.insert(0, '.'); from config.settings import ConfigManager; print('✅ ConfigManager funcionando')"
if %errorlevel% neq 0 (
    echo ❌ ERRO: Sistema de configuração com problemas
    pause
    exit /b 1
)

echo.
echo Executando testes automatizados...
python tests\test_new_structure.py
if %errorlevel% neq 0 (
    echo ❌ ERRO: Alguns testes falharam
    pause
    exit /b 1
)

echo.
echo 🎉 SUCESSO! O ARCA Bot está pronto para uso.
echo.
echo Para iniciar o bot:
echo 1. Configure o arquivo .env com seu token
echo 2. Execute: python run.py
echo.

pause

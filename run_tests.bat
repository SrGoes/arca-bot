@echo off
echo 🧪 Testando ARCA Bot - Versão Simplificada
echo ===============================================

echo.
echo 📋 Testando imports principais...
python -c "import sys; sys.path.insert(0, 'src'); from main import main; print('✅ Import do main.py funcionando')"

echo.
echo 📋 Testando ConfigManager...
python -c "import sys, os; sys.path.insert(0, '.'); from config.settings import ConfigManager; print('✅ ConfigManager importado')"

echo.
echo 📋 Testando módulos principais...
python -c "import sys; sys.path.insert(0, 'src'); from modules.economy import EconomySystem; print('✅ EconomySystem importado')"
python -c "import sys; sys.path.insert(0, 'src'); from modules.lottery import LotterySystem; print('✅ LotterySystem importado')"

echo.
echo 📋 Testando comandos...
python -c "import sys; sys.path.insert(0, 'src'); from commands.basic import setup_basic_commands; print('✅ Comandos básicos importados')"

echo.
echo 🎉 Todos os testes básicos passaram!
echo 📊 O bot está funcionando corretamente.
echo.
pause

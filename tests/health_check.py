#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARCA Bot - Health Check Script

Script para verificar a saúde e integridade do projeto.
"""

import sys
import os
import importlib.util
import subprocess
import json
from pathlib import Path

# Adicionar o diretório pai ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    print("🐍 Verificando versão do Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 13:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (compatível)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requer 3.13+)")
        return False

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("\n📦 Verificando dependências...")
    
    dependencies = [
        ('discord.py', 'discord'),
        ('python-dotenv', 'dotenv'),
        ('PyNaCl', 'nacl')
    ]
    
    missing_packages = []
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} (não instalado)")
            missing_packages.append(package_name)
    
    return len(missing_packages) == 0

def check_file_structure():
    """Verifica a estrutura de arquivos do projeto"""
    print("\n📁 Verificando estrutura do projeto...")
    
    required_files = [
        '../run.py',
        '../src/main.py',
        '../src/commands/basic.py',
        '../src/commands/economy.py',
        '../src/commands/lottery.py',
        '../src/core/utils/cache.py',
        '../src/core/utils/permissions.py',
        '../src/core/utils/rate_limiter.py',
        '../src/core/utils/wallet_panel.py',
        '../src/modules/economy.py',
        '../src/modules/lottery.py',
        '../config/settings.py',
        '../config/bot_config.json',
        '../.env.example',
        '../pyproject.toml',
        '../requirements.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (não encontrado)")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_configuration():
    """Verifica se a configuração está correta"""
    print("\n⚙️ Verificando configuração...")
    
    # Verificar .env
    if os.path.exists('../.env'):
        print("✅ Arquivo .env encontrado")
        
        # Verificar se há token
        with open('../.env', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'DISCORD_BOT_TOKEN=' in content and 'seu_token_aqui' not in content:
                print("✅ Token do Discord configurado")
            else:
                print("⚠️  Token do Discord não configurado corretamente")
    else:
        print("❌ Arquivo .env não encontrado")
    
    # Verificar config.json
    config_path = '../config/bot_config.json'
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print("✅ Arquivo de configuração válido")
        except json.JSONDecodeError:
            print("❌ Arquivo de configuração JSON inválido")
    else:
        print("⚠️  Arquivo de configuração não encontrado (será criado automaticamente)")

def check_imports():
    """Verifica se todos os módulos podem ser importados"""
    print("\n🔍 Verificando importações...")
    
    # Adicionar src ao path
    sys.path.insert(0, '../src')
    
    modules_to_test = [
        'main',
        'commands.basic',
        'commands.economy',
        'commands.lottery',
        'core.utils.cache',
        'core.utils.permissions',
        'core.utils.rate_limiter',
        'core.utils.wallet_panel',
        'modules.economy',
        'modules.lottery'
    ]
    
    import_errors = []
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module} ({e})")
            import_errors.append(module)
    
    return len(import_errors) == 0

def check_tests():
    """Verifica se os testes podem ser executados"""
    print("\n🧪 Verificando testes...")
    
    # Estamos dentro da pasta tests/, então verificamos o diretório atual
    test_files = [f for f in os.listdir('.') if f.startswith("test_") and f.endswith(".py")]
    
    if not test_files:
        print("❌ Nenhum arquivo de teste encontrado")
        return False
    
    print(f"✅ {len(test_files)} arquivos de teste encontrados")
    
    # Executar testes básicos
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'test_new_structure.py', '-v'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Testes básicos passaram")
            return True
        else:
            print("❌ Alguns testes falharam")
            print(result.stdout)
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Testes expiraram (timeout)")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False

def main():
    """Função principal do health check"""
    print("🏥 ARCA Bot - Health Check")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("File Structure", check_file_structure),
        ("Configuration", check_configuration),
        ("Imports", check_imports),
        ("Tests", check_tests)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"❌ Erro em {check_name}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Resultado: {passed}/{total} verificações passaram")
    
    if passed == total:
        print("🎉 Projeto está saudável! Bot pronto para execução.")
        return 0
    else:
        print("⚠️  Alguns problemas foram encontrados. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

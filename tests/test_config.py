#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar a configuração do ARCA Bot
Testa todas as dependências e arquivos necessários
"""

import os
import sys

def test_configuration():
    """Testa a configuração completa do bot"""
    print("🔍 ARCA Bot - Teste de Configuração Completa")
    print("=" * 50)
    
    # 1. Verificar Python
    print(f"✅ Python: {sys.version}")
    
    # 2. Verificar arquivo .env
    if os.path.exists('.env'):
        print("✅ Arquivo .env encontrado")
        
        # Tentar ler o token
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'DISCORD_BOT_TOKEN=' in content:
                    # Verificar se não é placeholder
                    for line in content.split('\n'):
                        if line.startswith('DISCORD_BOT_TOKEN=') and not line.startswith('#'):
                            token = line.split('=', 1)[1].strip()
                            if token and token not in ['seu_token_aqui', 'YOUR_BOT_TOKEN_HERE']:
                                print("✅ Token configurado no .env")
                            else:
                                print("❌ Token não configurado ou é placeholder")
                            break
                else:
                    print("❌ DISCORD_BOT_TOKEN não encontrado no .env")
        except Exception as e:
            print(f"❌ Erro ao ler .env: {e}")
    else:
        print("❌ Arquivo .env não encontrado")
    
    # 3. Verificar dependências
    try:
        import discord
        print(f"✅ discord.py: {discord.__version__}")
    except ImportError:
        print("❌ discord.py não instalado")
        return False
    
    try:
        import dotenv
        print("✅ python-dotenv instalado")
    except ImportError:
        print("⚠️  python-dotenv não instalado (opcional)")
    
    # 4. Verificar estrutura de arquivos obrigatórios
    required_files = {
        'bot.py': 'Arquivo principal do bot',
        'economy.py': 'Sistema de economia',
        'lottery.py': 'Sistema de sorteios', 
        'requirements.txt': 'Dependências Python',
        'README.md': 'Documentação'
    }
    
    for file, description in required_files.items():
        if os.path.exists(file):
            print(f"✅ {file} - {description}")
        else:
            print(f"❌ {file} não encontrado - {description}")
    
    # 5. Verificar arquivos opcionais
    optional_files = {
        'config.example.py': 'Exemplo de configuração',
        'DOCS.md': 'Documentação técnica',
        'test_config.py': 'Script de teste',
        'setup.bat': 'Script de instalação Windows',
        'setup.sh': 'Script de instalação Linux/Mac'
    }
    
    print("\n📂 Arquivos Opcionais:")
    for file, description in optional_files.items():
        if os.path.exists(file):
            print(f"✅ {file} - {description}")
        else:
            print(f"⚠️  {file} - {description}")
    
    # 6. Verificar pastas que serão criadas automaticamente
    auto_created = ['backups', 'economy_data.json', 'lottery_data.json', 'bot.log']
    print("\n📁 Criados Automaticamente:")
    for item in auto_created:
        if os.path.exists(item):
            print(f"✅ {item} já existe")
        else:
            print(f"⏳ {item} será criado automaticamente")
    
    # 7. Teste de importação dos módulos
    print("\n🔧 Teste de Importação:")
    try:
        from economy import EconomySystem
        print("✅ EconomySystem importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar EconomySystem: {e}")
    
    try:
        from lottery import LotterySystem
        print("✅ LotterySystem importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar LotterySystem: {e}")
    
    print("\n" + "=" * 50)
    print("📋 Checklist de Configuração do Discord:")
    print("□ Criar categoria 'C.O.M.M.S OPS' com canais de voz")
    print("□ Criar canal de texto 'log-cargos'")  
    print("□ Criar canal de texto 'sorteios' (opcional)")
    print("□ Criar cargo 'ECONOMIA_ADMIN'")
    print("□ Criar cargo 'SORTEIO_ADMIN'")
    print("□ Configurar permissões do bot")
    print("□ Habilitar intents no Discord Developer Portal")
    
    print("\n📋 Próximos passos:")
    print("1. pip install -r requirements.txt")
    print("2. Configure token no .env")
    print("3. Configure servidor Discord conforme checklist")
    print("4. python bot.py")
    
    return True

if __name__ == '__main__':
    test_configuration()

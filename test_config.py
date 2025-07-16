#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar a configuração do ARCA Bot
"""

import os
import sys

def test_configuration():
    """Testa a configuração do bot"""
    print("🔍 ARCA Bot - Teste de Configuração")
    print("=" * 40)
    
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
    
    # 4. Verificar estrutura de arquivos
    required_files = ['bot.py', 'requirements.txt', 'README.md']
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} não encontrado")
    
    print("\n" + "=" * 40)
    print("📋 Próximos passos:")
    print("1. Instale dependências: pip install -r requirements.txt")
    print("2. Configure token no .env")
    print("3. Execute: python bot.py")
    
    return True

if __name__ == '__main__':
    test_configuration()

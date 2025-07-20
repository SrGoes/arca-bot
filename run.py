#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARCA Bot - Launcher

Script de execução principal do ARCA Bot.
Configura o path e inicia o bot.
"""

import os
import sys

# Correção SSL para AWS Windows - DEVE ser a primeira coisa
try:
    import ssl
    import certifi
    
    # Configurar SSL para AWS Windows
    cert_file = certifi.where()
    os.environ['SSL_CERT_FILE'] = cert_file
    os.environ['REQUESTS_CA_BUNDLE'] = cert_file
    os.environ['CURL_CA_BUNDLE'] = cert_file
    
    # Configurar contexto SSL padrão
    ssl_context = ssl.create_default_context(cafile=cert_file)
    ssl._create_default_https_context = lambda: ssl_context
    
    print("✅ SSL configurado para AWS Windows")
    
except ImportError:
    print("⚠️  Certifi não encontrado, instalando...")
    os.system('pip install certifi')
    try:
        import certifi
        cert_file = certifi.where()
        os.environ['SSL_CERT_FILE'] = cert_file
        os.environ['REQUESTS_CA_BUNDLE'] = cert_file
        print("✅ SSL configurado após instalar certifi")
    except:
        print("⚠️  Usando configuração SSL insegura")
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        
except Exception as e:
    print(f"⚠️  Erro ao configurar SSL: {e}")
    print("⚠️  Usando configuração SSL insegura")
    os.environ['PYTHONHTTPSVERIFY'] = '0'

# Adicionar src ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar e executar o bot
if __name__ == '__main__':
    from main import main
    main()

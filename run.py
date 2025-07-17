#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARCA Bot - Launcher

Script de execução principal do ARCA Bot.
Configura o path e inicia o bot.
"""

import os
import sys

# Adicionar src ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar e executar o bot
if __name__ == '__main__':
    from main import main
    main()

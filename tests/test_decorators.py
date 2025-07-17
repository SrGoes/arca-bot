#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para verificar se os decoradores estão funcionando corretamente
"""

import asyncio
import sys
import os
import discord
from unittest.mock import Mock, AsyncMock

# Configurar path para importações
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "..", "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Importar os decoradores
from core.utils.rate_limiter import rate_limit
from core.utils.permissions import require_economy_admin

async def test_decorators():
    """Teste para verificar se os decoradores preservam os argumentos corretamente"""
    
    print("🧪 Testando decoradores...")
    
    # Mock do contexto
    mock_ctx = Mock()
    mock_ctx.author = Mock()
    mock_ctx.author.id = 123456789
    mock_ctx.guild = Mock()
    mock_ctx.guild.id = 987654321
    mock_ctx.send = AsyncMock()
    
    # Mock do bot
    mock_bot = Mock()
    mock_bot.permission_manager = Mock()
    mock_bot.permission_manager.has_permission_level = Mock(return_value=True)
    mock_ctx.bot = mock_bot
    
    # Função de teste que simula o comando distribute_coins
    @rate_limit('admin')
    @require_economy_admin()
    async def test_distribute_coins(ctx, amount: int):
        """Função de teste que simula distribute_coins"""
        print(f"📊 Comando executado com ctx={type(ctx).__name__}, amount={amount} (tipo: {type(amount).__name__})")
        return f"Distribuindo {amount} moedas"
    
    # Função de teste que simula o comando clan_pay
    @rate_limit('admin') 
    @require_economy_admin()
    async def test_clan_pay(ctx, member: discord.Member, amount: int):
        """Função de teste que simula clan_pay"""
        print(f"💰 Comando executado com ctx={type(ctx).__name__}, member={member}, amount={amount} (tipo: {type(amount).__name__})")
        return f"Pagando {amount} moedas para {member}"
    
    # Função de teste que simula create_lottery
    @rate_limit('admin')
    @require_economy_admin()
    async def test_create_lottery(ctx, *, args=None):
        """Função de teste que simula create_lottery"""
        print(f"🎲 Comando executado com ctx={type(ctx).__name__}, args={args} (tipo: {type(args).__name__})")
        return f"Criando sorteio com args: {args}"
    
    # Mock de membro
    mock_member = Mock(spec=discord.Member)
    mock_member.display_name = "TestUser"
    
    try:
        # Testar distribute_coins
        print("\n🔸 Testando distribute_coins...")
        result = await test_distribute_coins(mock_ctx, 100)
        print(f"✅ Resultado: {result}")
        
        # Testar clan_pay
        print("\n🔸 Testando clan_pay...")
        result = await test_clan_pay(mock_ctx, mock_member, 50)
        print(f"✅ Resultado: {result}")
        
        # Testar create_lottery
        print("\n🔸 Testando create_lottery...")
        result = await test_create_lottery(mock_ctx, args="Nave Aurora | 100")
        print(f"✅ Resultado: {result}")
        
        print("\n🎉 Todos os testes de decoradores passaram!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no teste de decoradores: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Configurar ambiente de teste
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar teste
    result = asyncio.run(test_decorators())
    print(f"\n📊 Resultado final: {'✅ SUCESSO' if result else '❌ FALHA'}")

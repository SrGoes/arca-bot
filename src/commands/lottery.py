#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comandos de Sorteios - ARCA Bot

Todos os comandos relacionados ao sistema de sorteios.
"""

import discord
from discord.ext import commands
import uuid
from datetime import datetime

from core.utils.rate_limiter import rate_limit
from core.utils.permissions import require_lottery_admin


def setup_lottery_commands(bot):
    """Registra todos os comandos de sorteio no bot"""
    
    @bot.command(name='criarsorteio')
    @require_lottery_admin()
    @rate_limit('admin')
    async def create_lottery(ctx, *, args=None):
        """Cria um novo sorteio"""
        if not ctx.bot.lottery:
            await ctx.send("❌ Sistema de sorteio não está disponível!")
            return
        
        if not args:
            embed = discord.Embed(
                title="📋 Como Criar um Sorteio",
                description="Use: `!criarsorteio Nome do Sorteio | Valor do Ticket`",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Exemplo",
                value="`!criarsorteio Nave Aurora | 50`",
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        try:
            # Parse dos argumentos
            parts = args.split('|')
            if len(parts) != 2:
                raise ValueError("Formato inválido")
            
            name = parts[0].strip()
            price = int(parts[1].strip())
            
            if price <= 0:
                raise ValueError("Preço inválido")
            
            if len(name) < 3:
                raise ValueError("Nome muito curto")
            
        except ValueError:
            await ctx.send("❌ Formato inválido! Use: `!criarsorteio Nome do Sorteio | Valor do Ticket`")
            return
        
        # Gerar ID único para o sorteio
        lottery_id = str(uuid.uuid4())
        
        # Criar dados do sorteio
        lottery_data = {
            'id': lottery_id,
            'name': name,
            'base_price': price,
            'creator_id': ctx.author.id,
            'created_at': datetime.now().timestamp(),
            'participants': {},
            'ticket_prices': [],
            'channel_id': ctx.channel.id
        }
        
        # Criar embed e view públicos
        embed = ctx.bot.lottery.create_lottery_embed(lottery_data)
        view = ctx.bot.lottery.create_lottery_view(lottery_id, lottery_data)
        
        # Enviar mensagem pública
        message = await ctx.send("@everyone", embed=embed, view=view)
        
        # Salvar ID da mensagem pública no sorteio
        lottery_data['public_message_id'] = str(message.id)
        
        # Salvar sorteio
        ctx.bot.lottery.active_lotteries[lottery_id] = lottery_data
        ctx.bot.lottery.save_data()
        
        # Criar painel administrativo
        admin_embed = discord.Embed(
            title="🔧 Painel Administrativo - Sorteio",
            description=f"**{name}**",
            color=discord.Color.orange()
        )
        
        admin_embed.add_field(name="🎫 Total de Tickets", value="0", inline=True)
        admin_embed.add_field(name="👥 Participantes", value="0", inline=True)
        admin_embed.add_field(name="💰 Total Arrecadado", value="0 AC", inline=True)
        admin_embed.add_field(name="💰 Valor Base", value=f"{price} AC", inline=True)
        admin_embed.add_field(name="📋 Lista de Participantes", value="Nenhum participante ainda", inline=False)
        
        admin_view = ctx.bot.lottery.create_admin_panel_view(lottery_id, lottery_data)
        
        # Enviar painel admin
        try:
            admin_msg = await ctx.author.send(f"🔧 **Painel Administrativo do Sorteio**: {name}", embed=admin_embed, view=admin_view)
            ctx.bot.lottery.register_admin_panel(lottery_id, admin_msg, ctx.author.id)
            
            confirmation_embed = discord.Embed(
                title="✅ Sorteio Criado!",
                description=f"O painel administrativo foi enviado para {ctx.author.mention} via mensagem privada.",
                color=discord.Color.green()
            )
            confirmation_embed.add_field(
                name="📋 Informações",
                value=f"**Nome:** {name}\n**Valor Base:** {price} AC\n**Criador:** {ctx.author.mention}",
                inline=False
            )
            
            await ctx.send(embed=confirmation_embed, delete_after=30)
            
        except discord.Forbidden:
            warning_embed = discord.Embed(
                title="⚠️ Aviso - Mensagem Privada Bloqueada",
                description=f"{ctx.author.mention}, suas mensagens privadas estão bloqueadas. O painel será enviado aqui mas apenas você pode usá-lo.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=warning_embed, delete_after=10)
            
            admin_msg = await ctx.send(f"🔒 **Painel Administrativo de {ctx.author.mention}**", embed=admin_embed, view=admin_view)
            ctx.bot.lottery.register_admin_panel(lottery_id, admin_msg, ctx.author.id)

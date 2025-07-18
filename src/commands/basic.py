#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comandos Básicos e Administrativos - ARCA Bot

Comandos gerais, informações do bot e comandos administrativos.
"""

import discord
import asyncio
import time
import logging
from datetime import datetime, timezone

from core.utils.permissions import require_admin

logger = logging.getLogger("ARCA-Bot")

# Variável global para rastrear tempo de início
START_TIME = time.time()


def get_uptime():
    """Calcula o uptime do bot"""
    uptime_seconds = time.time() - START_TIME

    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def setup_basic_commands(bot):
    """Registra todos os comandos básicos no bot"""

    @bot.command(name="ping")
    async def ping(ctx):
        """Comando simples para testar se o bot está respondendo"""
        logger.info(
            f"Comando !ping executado por {ctx.author} ({ctx.author.id}) no servidor {ctx.guild.name if ctx.guild else 'DM'}"
        )

        latency = round(bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latência: {latency}ms",
            color=(
                discord.Color.green()
                if latency < 100
                else discord.Color.orange() if latency < 200 else discord.Color.red()
            ),
        )
        await ctx.send(embed=embed)

    @bot.command(name="info")
    async def info(ctx):
        """Mostra informações sobre o bot"""
        logger.info(
            f"Comando !info executado por {ctx.author} ({ctx.author.id}) no servidor {ctx.guild.name if ctx.guild else 'DM'}"
        )

        embed = discord.Embed(
            title="🤖 ARCA Bot",
            description="Bot multipropósito da organização ARCA para Star Citizen",
            color=discord.Color.blue(),
        )

        embed.add_field(
            name="📊 Estatísticas",
            value=f"Servidores: {len(bot.guilds)}\nUsuários: {len(bot.users)}",
            inline=True,
        )

        embed.add_field(
            name="⚡ Funcionalidades",
            value="• Sistema de Economia (AC)\n• Sistema de Sorteios\n• Log de Cargos\n• Recompensas por Voz",
            inline=True,
        )

        embed.add_field(
            name="💰 Comandos Economia",
            value="`!saldo` `!diario` `!distribuir` `!pagar` `!remover`",
            inline=False,
        )

        embed.add_field(
            name="🎲 Comandos Sorteio", value="`!criarsorteio`", inline=False
        )

        embed.set_footer(text="Desenvolvido pela ARCA Organization")

        await ctx.send(embed=embed)

    @bot.command(name="help", aliases=["ajuda"])
    async def help_command(ctx):
        """Lista todos os comandos disponíveis"""
        logger.info(
            f"Comando !help executado por {ctx.author} ({ctx.author.id}) no servidor {ctx.guild.name if ctx.guild else 'DM'}"
        )

        embed = discord.Embed(
            title="📚 Comandos ARCA Bot",
            description="Lista completa de comandos disponíveis",
            color=discord.Color.blue(),
        )

        # Comandos Básicos
        embed.add_field(
            name="🔧 Básicos",
            value="`!ping` - Latência do bot\n`!info` - Informações do bot\n`!help` - Esta mensagem",
            inline=False,
        )

        # Comandos de Economia (usuários)
        embed.add_field(
            name="💰 Economia",
            value=("`!saldo` - Ver seu saldo de AC\n" "`!diario` - Recompensa diária"),
            inline=False,
        )

        # Comandos de Sorteio (usuários)
        embed.add_field(
            name="🎲 Sorteios",
            value=(
                "Botões: 🎲 Sortear, 🎫 Comprar, ❌ Cancelar\n"
                "(Sorteios são criados por administradores)"
            ),
            inline=False,
        )

        # Comandos de Painel (Administrativos)
        embed.add_field(
            name="📊 Painel (Admin)",
            value=(
                "`!painel status` - Status do sistema (Admin)\n"
                "`!painel config` - Ver configuração (Admin)\n"
                "`!painel atualizar` - Forçar atualização (Admin)\n"
                "`!painel criar` - Criar painel (Admin)"
            ),
            inline=False,
        )

        # Comandos Administrativos (separado)
        embed.add_field(
            name="👑 Administrativos",
            value=(
                "`!distribuir <valor>` - Distribuir AC para todos na call\n"
                "`!pagar <@user> <valor>` - Pagar AC para usuário\n"
                "`!remover <@user> <valor>` - Remover AC de usuário\n"
                "`!criarsorteio Nome | Valor` - Criar sorteio\n"
                "`!cache [ação]` - Gerenciar cache\n"
                "`!desligar` - Desligar bot"
            ),
            inline=False,
        )

        embed.set_footer(
            text="ARCA Bot | Star Citizen - Desenvolvido pela ARCA Organization"
        )

        await ctx.send(embed=embed)

    @bot.command(name="painel")
    @require_admin()
    async def manage_panel(ctx, action: str = None):
        """Gerencia o painel de carteiras (admins)"""
        if not ctx.bot.wallet_panel:
            await ctx.send("❌ Sistema de painel não está disponível!")
            return

        if not action:
            embed = discord.Embed(
                title="🎛️ Gerenciamento do Painel",
                description="Comandos disponíveis para gerenciar o painel de carteiras",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name="📊 Comandos",
                value=(
                    f"`{ctx.prefix}painel criar` - Criar painel no canal configurado\n"
                    f"`{ctx.prefix}painel atualizar` - Forçar atualização do painel\n"
                    f"`{ctx.prefix}painel status` - Ver status do sistema\n"
                    f"`{ctx.prefix}painel config` - Ver configuração atual"
                ),
                inline=False,
            )
            await ctx.send(embed=embed)
            return

        if action.lower() == "criar":
            success = await ctx.bot.wallet_panel.create_panel_in_guild(ctx.guild)
            if success:
                await ctx.send(
                    f"✅ Painel criado no canal **#{ctx.bot.config.general.wallet_panel_channel}**!"
                )
            else:
                await ctx.send(
                    f"❌ Erro ao criar painel. Verifique se o canal **#{ctx.bot.config.general.wallet_panel_channel}** existe!"
                )

        elif action.lower() == "atualizar":
            await ctx.send("🔄 Atualizando painel...")
            await ctx.bot.wallet_panel.force_update_all()
            await ctx.send("✅ Painel atualizado!")

        elif action.lower() == "status":
            embed = discord.Embed(
                title="📊 Status do Sistema de Painel", color=discord.Color.green()
            )
            embed.add_field(
                name="🔧 Sistema",
                value=f"Ativo: {'✅' if ctx.bot.wallet_panel.is_running else '❌'}",
                inline=True,
            )
            embed.add_field(
                name="📝 Painéis Ativos",
                value=str(len(ctx.bot.wallet_panel.panel_messages)),
                inline=True,
            )
            embed.add_field(
                name="⏱️ Intervalo de Atualização",
                value=f"{ctx.bot.wallet_panel.update_interval // 60} minutos",
                inline=True,
            )
            await ctx.send(embed=embed)

        elif action.lower() == "config":
            embed = discord.Embed(
                title="⚙️ Configuração do Painel", color=discord.Color.blue()
            )
            embed.add_field(
                name="📍 Canal Configurado",
                value=f"#{ctx.bot.config.general.wallet_panel_channel}",
                inline=False,
            )

            # Verificar se o canal existe
            panel_channel = await ctx.bot.wallet_panel.get_wallet_channel(ctx.guild)
            embed.add_field(
                name="✅ Canal Existe",
                value="Sim" if panel_channel else "❌ Não encontrado",
                inline=True,
            )

            if panel_channel:
                embed.add_field(
                    name="🔒 Permissões",
                    value=(
                        "✅ OK"
                        if panel_channel.permissions_for(ctx.guild.me).send_messages
                        else "❌ Sem permissão"
                    ),
                    inline=True,
                )

            await ctx.send(embed=embed)

        else:
            await ctx.send(
                "❌ Ação inválida! Use: `criar`, `atualizar`, `status` ou `config`"
            )

    @bot.command(name="cache")
    @require_admin()
    async def cache_management(ctx, action: str = None):
        """Gerencia o sistema de cache (admins)"""
        if not ctx.bot.cache_manager:
            await ctx.send("❌ Sistema de cache não está disponível!")
            return

        if not action:
            stats = ctx.bot.cache_manager.get_stats()
            embed = discord.Embed(
                title="📊 Estatísticas do Cache", color=discord.Color.blue()
            )

            if stats.get("enabled"):
                embed.add_field(
                    name="📈 Taxa de Acerto", value=f"{stats['hit_rate']}%", inline=True
                )
                embed.add_field(name="🎯 Acertos", value=stats["hits"], inline=True)
                embed.add_field(name="❌ Erros", value=stats["misses"], inline=True)
                embed.add_field(
                    name="📦 Itens",
                    value=f"{stats['size']}/{stats['max_size']}",
                    inline=True,
                )
                embed.add_field(
                    name="⏱️ TTL Padrão", value=f"{stats['default_ttl']}s", inline=True
                )
                embed.add_field(
                    name="💡 Comandos",
                    value=f"`{ctx.prefix}cache limpar` - Limpar cache",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="Status", value="❌ Cache desabilitado", inline=False
                )

            await ctx.send(embed=embed)
            return

        if action.lower() == "limpar":
            ctx.bot.cache_manager.clear()
            await ctx.send("✅ Cache limpo com sucesso!")
        else:
            await ctx.send("❌ Ação inválida! Use: `limpar`")

    @bot.command(name="desligar", aliases=["shutdown", "off"])
    @require_admin()
    async def shutdown(ctx):
        """Comando para desligar o bot de forma segura"""
        logger.info(
            f"Comando !desligar executado por {ctx.author} ({ctx.author.id}) no servidor {ctx.guild.name if ctx.guild else 'DM'}"
        )

        try:
            # Embed de confirmação
            embed = discord.Embed(
                title="🔴 Desligando Bot",
                description="O ARCA Bot será desligado...",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="👤 Executado por",
                value=f"{ctx.author.mention} (`{ctx.author}`)",
                inline=False,
            )
            embed.add_field(
                name="📊 Estatísticas da Sessão",
                value=f"⏱️ **Uptime**: {get_uptime()}\n"
                f"🏓 **Latência**: {round(ctx.bot.latency * 1000)}ms\n"
                f"🖥️ **Servidores**: {len(ctx.bot.guilds)}",
                inline=False,
            )
            embed.set_footer(text="Até logo! 👋")

            await ctx.send(embed=embed)

            # Log da ação
            logger.info(
                f"Bot sendo desligado por {ctx.author} ({ctx.author.id}) em {ctx.guild.name if ctx.guild else 'DM'}"
            )

            # Aguardar um momento para a mensagem ser enviada
            await asyncio.sleep(2)

            # Desligar o bot
            await ctx.bot.close()

        except Exception as e:
            logger.error(f"Erro ao desligar bot: {e}")
            error_embed = discord.Embed(
                title="❌ Erro ao Desligar",
                description=f"Ocorreu um erro: {str(e)}",
                color=discord.Color.red(),
            )
            await ctx.send(embed=error_embed)

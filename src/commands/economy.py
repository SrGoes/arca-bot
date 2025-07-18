#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comandos de Economia - ARCA Bot

Todos os comandos relacionados ao sistema de economia e Arca Coins.
"""

import discord
import asyncio
import random
import logging
from datetime import datetime, timedelta, timezone

from core.utils.rate_limiter import rate_limit
from core.utils.permissions import require_economy_admin

logger = logging.getLogger("ARCA-Bot")


async def delete_command_if_configured(ctx, command_type="admin"):
    """
    Deleta o comando original se estiver configurado para isso

    Args:
        ctx: Context do comando
        command_type: Tipo do comando ('admin' ou 'user')
    """
    try:
        # Verificar configuração baseada no tipo de comando
        should_delete = False
        if command_type == "admin":
            should_delete = getattr(
                ctx.bot.config.economy, "delete_admin_commands", False
            )
        elif command_type == "lottery":
            should_delete = getattr(
                ctx.bot.config.lottery, "delete_command_after_creation", False
            )

        if should_delete:
            # Usar função robusta se disponível
            try:
                from ..modules.lottery import robust_discord_operation

                delete_success, _ = await robust_discord_operation(
                    lambda: ctx.message.delete(),
                    f"Deleção do comando {ctx.command.name} do usuário {ctx.author.id}",
                    ctx.bot.config.connectivity,
                )

                if not delete_success:
                    logger.warning(
                        f"Não foi possível deletar comando {ctx.command.name} do usuário {ctx.author.id}"
                    )

            except ImportError:
                # Fallback para método simples se robust_discord_operation não estiver disponível
                await ctx.message.delete()

    except Exception as e:
        # Em caso de erro, apenas loga mas não interrompe o fluxo
        logger.debug(f"Erro ao deletar comando {ctx.command.name}: {e}")
        pass


def setup_economy_commands(bot):
    """Registra todos os comandos de economia no bot"""

    @bot.command(name="saldo", aliases=["balance", "bal"])
    @rate_limit("economy")
    async def check_balance(ctx):
        """Verifica o saldo de Arca Coins"""
        logger.info(
            f"Comando !saldo executado por {ctx.author} ({ctx.author.id}) no servidor {ctx.guild.name if ctx.guild else 'DM'}"
        )

        if not ctx.bot.economy:
            await ctx.send("❌ Sistema de economia não está disponível!")
            return

        # Verificar cache primeiro
        cached_data = ctx.bot.cache_manager.get(f"user_balance_{ctx.author.id}")
        if cached_data:
            balance, user_data = cached_data
        else:
            balance = ctx.bot.economy.get_balance(ctx.author.id)
            user_data = ctx.bot.economy.get_user_data(ctx.author.id)
            # Cache por 60 segundos
            ctx.bot.cache_manager.set(
                f"user_balance_{ctx.author.id}", (balance, user_data), 60
            )

        embed = discord.Embed(title="💰 Seu Saldo ARCA", color=discord.Color.gold())

        embed.add_field(name="💳 Saldo Atual", value=f"{balance} AC", inline=True)

        embed.add_field(
            name="📈 Total Ganho", value=f"{user_data['total_earned']} AC", inline=True
        )

        embed.add_field(
            name="⏱️ Tempo em Voz",
            value=f"{user_data['voice_time']} minutos",
            inline=True,
        )

        embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
        )

        embed.set_footer(text="ARCA Bot | Star Citizen")

        await ctx.send(embed=embed)

    @bot.command(name="diario", aliases=["daily"])
    @rate_limit("daily")
    async def daily_reward(ctx):
        """Recompensa diária (precisa estar em canal de voz da categoria C.O.M.M.S OPS)"""
        logger.info(
            f"Comando !diario executado por {ctx.author} ({ctx.author.id}) no servidor {ctx.guild.name if ctx.guild else 'DM'}"
        )

        if not ctx.bot.economy:
            await ctx.send("❌ Sistema de economia não está disponível!")
            return

        # Verificar se está em canal de voz válido
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send(
                "❌ Você precisa estar em um canal de voz para receber a recompensa diária!"
            )
            return

        if not ctx.bot.economy.is_in_comms_category(ctx.author.voice.channel):
            await ctx.send(
                f"❌ Você precisa estar em um canal de voz da categoria **{ctx.bot.economy.voice_channels_category}**!"
            )
            return

        user_data = ctx.bot.economy.get_user_data(ctx.author.id)

        # Verificar se já recebeu hoje
        if user_data["last_daily"]:
            last_daily = datetime.fromisoformat(user_data["last_daily"]).replace(tzinfo=timezone.utc)
            if (datetime.now(timezone.utc) - last_daily).days < 1:
                # Calcular próximo reset (próximo dia às 00:00)
                next_reset = (last_daily + timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                hours_left = (next_reset - datetime.now(timezone.utc)).total_seconds() / 3600

                if hours_left > 1:
                    time_text = (
                        f"**{int(hours_left)}h {int((hours_left % 1) * 60)}min**"
                    )
                else:
                    time_text = f"**{int(hours_left * 60)}min**"

                await ctx.send(
                    f"🕐 **Recompensa Diária Já Coletada!**\n\n"
                    f"⏰ Próxima recompensa disponível em: {time_text}\n"
                    f"📅 Reset: <t:{int(next_reset.timestamp())}:R>\n\n"
                    f"💡 *A recompensa diária reseta à meia-noite (00:00)*",
                    delete_after=15,
                )
                return

        # Dar recompensa aleatória
        reward = random.randint(
            ctx.bot.economy.daily_reward_min, ctx.bot.economy.daily_reward_max
        )
        ctx.bot.economy.add_coins(ctx.author.id, reward, "Recompensa diária")

        # Atualizar última recompensa diária
        user_data["last_daily"] = datetime.now(timezone.utc).isoformat()
        ctx.bot.economy.save_data()

        logger.info(
            f"Recompensa diária de {reward} AC concedida para {ctx.author} ({ctx.author.id})"
        )

        embed = discord.Embed(
            title="🎁 Recompensa Diária!",
            description=f"Você recebeu **{reward} AC**!",
            color=discord.Color.green(),
        )

        new_balance = ctx.bot.economy.get_balance(ctx.author.id)
        embed.add_field(name="💳 Novo Saldo", value=f"{new_balance} AC", inline=True)

        embed.set_footer(text="Volte amanhã para mais!")

        await ctx.send(embed=embed)

    @bot.command(name="distribuir")
    @require_economy_admin()
    @rate_limit("admin")
    async def distribute_coins(ctx, amount: int):
        """Distribui moedas para todos na mesma call (só admins)"""
        logger.info(
            f"Comando !distribuir executado por {ctx.author} ({ctx.author.id}) com valor {amount}"
        )

        if not ctx.bot.economy:
            await ctx.send("❌ Sistema de economia não está disponível!")
            return

        if amount <= 0:
            await ctx.send("❌ O valor deve ser positivo!")
            return

        # Verificar se está em canal de voz
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ Você precisa estar em um canal de voz!")
            return

        voice_channel = ctx.author.voice.channel
        members_in_voice = [
            member for member in voice_channel.members if not member.bot
        ]

        if not members_in_voice:
            await ctx.send("❌ Não há membros no canal de voz!")
            return

        # Distribuir moedas
        total_distributed = 0
        for member in members_in_voice:
            ctx.bot.economy.add_coins(
                member.id, amount, f"Distribuição por {ctx.author.display_name}"
            )
            total_distributed += amount

        logger.info(
            f"Distribuição de {amount} AC para {len(members_in_voice)} membros no canal {voice_channel.name} - Total: {total_distributed} AC"
        )

        embed = discord.Embed(
            title="💰 Distribuição de Moedas",
            description=f"**{amount} AC** distribuído para **{len(members_in_voice)}** membros!",
            color=discord.Color.green(),
        )

        embed.add_field(
            name="💳 Total Distribuído", value=f"{total_distributed} AC", inline=True
        )

        embed.add_field(name="📍 Canal", value=voice_channel.name, inline=True)

        members_list = ", ".join(
            [member.display_name for member in members_in_voice[:10]]
        )
        if len(members_in_voice) > 10:
            members_list += f" e mais {len(members_in_voice) - 10}..."

        embed.add_field(name="👥 Membros", value=members_list, inline=False)

        await ctx.send(embed=embed)

        # Deletar comando administrativo se configurado
        await delete_command_if_configured(ctx, "admin")

    @bot.command(name="pagar")
    @require_economy_admin()
    @rate_limit("admin")
    async def clan_pay(ctx, member: discord.Member, amount: int):
        """Paga um membro gerando novas moedas (só admins)"""
        logger.info(
            f"Comando !pagar executado por {ctx.author} ({ctx.author.id}) para {member} ({member.id}) com valor {amount}"
        )

        if not ctx.bot.economy:
            await ctx.send("❌ Sistema de economia não está disponível!")
            return

        if amount <= 0:
            await ctx.send("❌ O valor deve ser positivo!")
            return

        if member.bot:
            await ctx.send("❌ Não é possível pagar bots!")
            return

        # Adicionar moedas (gerar novas)
        ctx.bot.economy.add_coins(
            member.id, amount, f"Pagamento do clã por {ctx.author.display_name}"
        )

        logger.info(
            f"Pagamento de {amount} AC realizado para {member} ({member.id}) por {ctx.author} ({ctx.author.id})"
        )

        embed = discord.Embed(
            title="💰 Pagamento do Clã",
            description=f"**{amount} AC** foi pago para {member.mention}!",
            color=discord.Color.green(),
        )

        new_balance = ctx.bot.economy.get_balance(member.id)
        embed.add_field(name="💳 Novo Saldo", value=f"{new_balance} AC", inline=True)

        embed.add_field(name="👤 Pago por", value=ctx.author.mention, inline=True)

        await ctx.send(embed=embed)

        # Deletar comando administrativo se configurado
        await delete_command_if_configured(ctx, "admin")

    @bot.command(name="remover", aliases=["remove"])
    @require_economy_admin()
    @rate_limit("admin")
    async def remove_coins(
        ctx,
        member: discord.Member,
        amount: int,
        *,
        reason: str = "Remoção administrativa",
    ):
        """Remove moedas de um membro (só admins de economia)"""
        logger.info(
            f"Comando !remover executado por {ctx.author} ({ctx.author.id}) para {member} ({member.id}) com valor {amount} - Motivo: {reason}"
        )

        if not ctx.bot.economy:
            await ctx.send("❌ Sistema de economia não está disponível!")
            return

        if amount <= 0:
            await ctx.send("❌ O valor deve ser positivo!")
            return

        if member.bot:
            await ctx.send("❌ Não é possível remover AC de bots!")
            return

        # Verificar saldo atual
        current_balance = ctx.bot.economy.get_balance(member.id)
        if current_balance < amount:
            await ctx.send(
                f"⚠️ **Saldo Insuficiente**\n"
                f"{member.display_name} possui apenas **{current_balance} AC**\n"
                f"Você está tentando remover **{amount} AC**\n\n"
                f"Deseja remover todo o saldo disponível? Digite `confirmar` para prosseguir."
            )

            def check(m):
                return (
                    m.author == ctx.author
                    and m.channel == ctx.channel
                    and m.content.lower() == "confirmar"
                )

            try:
                await ctx.bot.wait_for("message", check=check, timeout=30.0)
                amount = current_balance  # Remover apenas o que tem
            except asyncio.TimeoutError:
                await ctx.send("❌ Operação cancelada por timeout.")
                return

        # Remover moedas
        if ctx.bot.economy.remove_coins(member.id, amount):
            # Limpar cache
            ctx.bot.cache_manager.delete(f"user_balance_{member.id}")

            logger.info(
                f"Remoção de {amount} AC realizada para {member} ({member.id}) por {ctx.author} ({ctx.author.id}) - Motivo: {reason}"
            )

            embed = discord.Embed(
                title="💸 Remoção de AC",
                description=f"**{amount} AC** foi removido de {member.mention}!",
                color=discord.Color.red(),
            )

            new_balance = ctx.bot.economy.get_balance(member.id)
            embed.add_field(
                name="💳 Novo Saldo", value=f"{new_balance} AC", inline=True
            )

            embed.add_field(
                name="👤 Removido por", value=ctx.author.mention, inline=True
            )

            embed.add_field(name="📝 Motivo", value=reason, inline=False)

            await ctx.send(embed=embed)

            # Deletar comando administrativo se configurado
            await delete_command_if_configured(ctx, "admin")
        else:
            await ctx.send("❌ Erro ao remover moedas!")

            # Deletar comando mesmo em caso de erro se configurado
            await delete_command_if_configured(ctx, "admin")

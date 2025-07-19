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

    @bot.command(name="backup_calls", aliases=["bk_calls"])
    @require_economy_admin()
    @rate_limit("admin")
    async def force_backup_calls(ctx):
        """Força backup dos dados de tracking de voz (só admins)"""
        logger.info(
            f"Comando !backup_calls executado por {ctx.author} ({ctx.author.id})"
        )

        if not ctx.bot.economy:
            await ctx.send("❌ Sistema de economia não está disponível!")
            return

        try:
            # Forçar salvamento dos dados de tracking
            ctx.bot.economy.save_voice_tracking_data()
            
            # Informações dos dados salvos
            active_sessions = len(ctx.bot.economy.voice_tracking)
            tracked_messages = len(ctx.bot.economy.voice_tracking_messages)
            
            embed = discord.Embed(
                title="💾 Backup Forçado Concluído",
                description="Dados de tracking de voz salvos com sucesso!",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.add_field(
                name="🎤 Sessões Ativas", 
                value=f"**{active_sessions}** usuários em call", 
                inline=True
            )
            
            embed.add_field(
                name="📤 Mensagens Trackadas", 
                value=f"**{tracked_messages}** mensagens salvas", 
                inline=True
            )
            
            embed.add_field(
                name="📂 Arquivo", 
                value="`data/voice_tracking_data.json`", 
                inline=False
            )
            
            embed.set_footer(text="ARCA Organization - Sistema de Economia")
            
            await ctx.send(embed=embed)
            
            logger.info(f"Backup forçado executado com sucesso: {active_sessions} sessões, {tracked_messages} mensagens")
            
        except Exception as e:
            logger.error(f"Erro no backup forçado: {e}")
            
            await ctx.send(
                f"❌ **Erro ao forçar backup!**\n"
                f"```\n{str(e)}\n```"
            )

        # Deletar comando administrativo se configurado
        await delete_command_if_configured(ctx, "admin")

    @bot.command(name="status_calls", aliases=["call_status", "calls"])
    @require_economy_admin()
    @rate_limit("admin")
    async def status_calls(ctx):
        """Mostra status detalhado das calls ativas (só admins)"""
        logger.info(
            f"Comando !status_calls executado por {ctx.author} ({ctx.author.id})"
        )

        if not ctx.bot.economy:
            await ctx.send("❌ Sistema de economia não está disponível!")
            return

        try:
            voice_tracking = ctx.bot.economy.voice_tracking
            tracking_messages = ctx.bot.economy.voice_tracking_messages
            current_time = datetime.now(timezone.utc)
            
            embed = discord.Embed(
                title="🎤 Status das Calls Ativas",
                description="Informações detalhadas do sistema de tracking",
                color=discord.Color.blue(),
                timestamp=current_time
            )
            
            if not voice_tracking:
                embed.add_field(
                    name="📊 Status Geral",
                    value="**Nenhuma call ativa no momento**",
                    inline=False
                )
            else:
                # Agrupar por canal
                channels_data = {}
                for user_id, track_data in voice_tracking.items():
                    channel_id = track_data["channel_id"]
                    if channel_id not in channels_data:
                        channels_data[channel_id] = []
                    channels_data[channel_id].append((user_id, track_data))
                
                embed.add_field(
                    name="📊 Resumo Geral",
                    value=f"**{len(voice_tracking)}** usuários em **{len(channels_data)}** canais",
                    inline=False
                )
                
                # Detalhes por canal
                for channel_id, users_data in channels_data.items():
                    try:
                        channel = ctx.bot.get_channel(channel_id)
                        channel_name = channel.name if channel else f"Canal {channel_id}"
                    except:
                        channel_name = f"Canal {channel_id}"
                    
                    users_info = []
                    for user_id, track_data in users_data:
                        try:
                            user = ctx.bot.get_user(user_id)
                            user_name = user.display_name if user else f"User {user_id}"
                        except:
                            user_name = f"User {user_id}"
                        
                        # Calcular tempo em call
                        start_time = track_data["start_time"]
                        time_diff = current_time - start_time
                        total_minutes = int(time_diff.total_seconds() / 60)
                        
                        # Calcular AC ganho até agora
                        periods_completed = total_minutes // ctx.bot.economy.min_voice_time_for_reward
                        coins_per_period = ctx.bot.economy.ac_per_hour / (60 / ctx.bot.economy.min_voice_time_for_reward)
                        coins_earned = int(periods_completed * coins_per_period)
                        
                        if total_minutes >= 60:
                            time_str = f"{total_minutes // 60}h {total_minutes % 60}m"
                        else:
                            time_str = f"{total_minutes}m"
                        
                        users_info.append(f"• {user_name}: {time_str} ({coins_earned} AC)")
                    
                    # Verificar se há mensagem de tracking
                    has_message = "✅" if channel_id in tracking_messages else "❌"
                    
                    field_value = f"**Mensagem de tracking:** {has_message}\n" + "\n".join(users_info)
                    
                    embed.add_field(
                        name=f"🎤 {channel_name}",
                        value=field_value,
                        inline=False
                    )
            
            # Informações técnicas
            embed.add_field(
                name="🔧 Informações Técnicas",
                value=(
                    f"**Mensagens trackadas:** {len(tracking_messages)}\n"
                    f"**Arquivo de dados:** `voice_tracking_data.json`\n"
                    f"**Tempo máx. restart:** {ctx.bot.economy.max_restart_time_for_recovery} min\n"
                    f"**Última atualização:** <t:{int(current_time.timestamp())}:R>"
                ),
                inline=False
            )
            
            embed.set_footer(text="ARCA Organization - Sistema de Tracking")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro no status das calls: {e}")
            
            await ctx.send(
                f"❌ **Erro ao verificar status das calls!**\n"
                f"```\n{str(e)}\n```"
            )

        # Deletar comando administrativo se configurado
        await delete_command_if_configured(ctx, "admin")

    @bot.command(name="force_backup", aliases=["backup", "bk"])
    @require_economy_admin()
    @rate_limit("admin")
    async def force_backup(ctx):
        """Força backup completo dos dados do bot (só admins)"""
        logger.info(
            f"Comando !force_backup executado por {ctx.author} ({ctx.author.id})"
        )

        if not ctx.bot.economy:
            await ctx.send("❌ Sistema de economia não está disponível!")
            return

        try:
            from datetime import datetime, timezone
            import shutil
            import os
            
            # Forçar backup do sistema de economia
            economy_backup_created = False
            voice_backup_created = False
            panel_backup_created = False
            lottery_backup_created = False
            
            # Backup da economia
            if os.path.exists(ctx.bot.economy.data_file):
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                economy_backup_file = os.path.join(
                    ctx.bot.economy.backup_dir, f"economy_backup_manual_{timestamp}.json"
                )
                os.makedirs(ctx.bot.economy.backup_dir, exist_ok=True)
                shutil.copy2(ctx.bot.economy.data_file, economy_backup_file)
                economy_backup_created = True
                
            # Backup do voice tracking
            if os.path.exists(ctx.bot.economy.voice_tracking_file):
                voice_backup_file = os.path.join(
                    ctx.bot.economy.backup_dir, f"voice_tracking_backup_manual_{timestamp}.json"
                )
                shutil.copy2(ctx.bot.economy.voice_tracking_file, voice_backup_file)
                voice_backup_created = True
            
            # Backup dos painéis (carteiras + loterias)
            panel_file = "data/panel_data.json"
            if os.path.exists(panel_file):
                panel_backup_file = os.path.join(
                    ctx.bot.economy.backup_dir, f"panel_data_backup_manual_{timestamp}.json"
                )
                shutil.copy2(panel_file, panel_backup_file)
                panel_backup_created = True
            
            # Backup dos dados de sorteios ativos
            lottery_file = "data/lottery_data.json"
            if os.path.exists(lottery_file):
                lottery_backup_file = os.path.join(
                    ctx.bot.economy.backup_dir, f"lottery_data_backup_manual_{timestamp}.json"
                )
                shutil.copy2(lottery_file, lottery_backup_file)
                lottery_backup_created = True
            
            # Backup do histórico de sorteios
            lottery_history_file = "data/lottery_history.json"
            if os.path.exists(lottery_history_file):
                lottery_history_backup_file = os.path.join(
                    ctx.bot.economy.backup_dir, f"lottery_history_backup_manual_{timestamp}.json"
                )
                shutil.copy2(lottery_history_file, lottery_history_backup_file)
                lottery_backup_created = True
            
            # Forçar salvamento dos dados atuais
            ctx.bot.economy.save_data()
            ctx.bot.economy.save_voice_tracking_data()
            
            # Forçar salvamento dos painéis se disponíveis
            if hasattr(ctx.bot, 'wallet_panel') and ctx.bot.wallet_panel:
                await ctx.bot.wallet_panel._save_panel_data()
            if hasattr(ctx.bot, 'lottery_panel') and ctx.bot.lottery_panel:
                ctx.bot.lottery_panel.save_panel_data()
            
            # Forçar salvamento dos dados de sorteios se disponíveis
            if hasattr(ctx.bot, 'lottery') and ctx.bot.lottery:
                ctx.bot.lottery.save_data()
                ctx.bot.lottery.save_history()
            
            # Informações dos dados
            total_users = len(ctx.bot.economy.user_data)
            active_sessions = len(ctx.bot.economy.voice_tracking)
            tracked_messages = len(getattr(ctx.bot.economy, 'message_tracking', {}))
            
            # Contar painéis
            panel_count = 0
            if hasattr(ctx.bot, 'wallet_panel') and ctx.bot.wallet_panel:
                panel_count += len(getattr(ctx.bot.wallet_panel, 'panel_messages', {}))
            if hasattr(ctx.bot, 'lottery_panel') and ctx.bot.lottery_panel:
                panel_count += len(getattr(ctx.bot.lottery_panel, 'panel_messages', {}))
            
            # Contar sorteios
            lottery_count = 0
            if hasattr(ctx.bot, 'lottery') and ctx.bot.lottery:
                lottery_count = len(getattr(ctx.bot.lottery, 'active_lotteries', {}))
            
            embed = discord.Embed(
                title="💾 Backup Completo Forçado",
                description="Backup manual executado com sucesso!",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.add_field(
                name="👥 Dados de Usuários", 
                value=f"**{total_users}** usuários salvos", 
                inline=True
            )
            
            embed.add_field(
                name="🎤 Sessões de Voz", 
                value=f"**{active_sessions}** sessões ativas", 
                inline=True
            )
            
            embed.add_field(
                name="📤 Mensagens Trackadas", 
                value=f"**{tracked_messages}** mensagens", 
                inline=True
            )
            
            embed.add_field(
                name="📊 Painéis Ativos", 
                value=f"**{panel_count}** painéis", 
                inline=True
            )
            
            embed.add_field(
                name="🎲 Sorteios Ativos", 
                value=f"**{lottery_count}** sorteios", 
                inline=True
            )
            
            embed.add_field(
                name="⏰ Timestamp", 
                value=f"`{timestamp}`", 
                inline=True
            )
            
            # Status dos backups
            backup_status = []
            if economy_backup_created:
                backup_status.append("✅ Economia")
            if voice_backup_created:
                backup_status.append("✅ Voice Tracking")
            if panel_backup_created:
                backup_status.append("✅ Painéis (Carteiras + Loterias)")
            if lottery_backup_created:
                backup_status.append("✅ Sorteios + Histórico")
                
            embed.add_field(
                name="📂 Arquivos de Backup",
                value="\n".join(backup_status) if backup_status else "⚠️ Nenhum arquivo para backup",
                inline=False
            )
            
            embed.add_field(
                name="📁 Localização",
                value=f"`{ctx.bot.economy.backup_dir}/`",
                inline=False
            )
            
            embed.set_footer(text="ARCA Organization - Sistema de Backup")
            
            await ctx.send(embed=embed)
            
            logger.info(f"Backup manual executado com sucesso: {total_users} usuários, {active_sessions} sessões")
            
        except Exception as e:
            logger.error(f"Erro no backup forçado: {e}")
            
            await ctx.send(
                f"❌ **Erro ao forçar backup!**\n"
                f"```\n{str(e)}\n```"
            )

        # Deletar comando administrativo se configurado
        await delete_command_if_configured(ctx, "admin")

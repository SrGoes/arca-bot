#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comandos do Painel de Loterias - ARCA Bot

Comandos administrativos para gerenciar o painel de histórico de loterias.
"""

import discord
import logging
from datetime import datetime, timezone

from core.utils.permissions import require_economy_admin

logger = logging.getLogger("ARCA-Bot")


async def delete_command_if_configured(ctx, command_type="admin"):
    """
    Deleta o comando original se estiver configurado para isso
    """
    try:
        should_delete = getattr(
            ctx.bot.config.economy, "delete_admin_commands", False
        )

        if should_delete:
            try:
                from ..modules.lottery import robust_discord_operation

                delete_success, _ = await robust_discord_operation(
                    lambda: ctx.message.delete(),
                    f"Deleção do comando {ctx.command.name} do usuário {ctx.author.id}",
                    ctx.bot.config.connectivity,
                )
                if not delete_success:
                    logger.warning(
                        f"Falha ao deletar comando {ctx.command.name} do usuário {ctx.author.id}"
                    )
            except Exception as e:
                logger.warning(f"Erro ao tentar deletar comando: {e}")
                try:
                    await ctx.message.delete()
                except Exception:
                    pass

    except Exception as e:
        logger.warning(f"Erro na verificação de deleção de comando: {e}")


def setup_lottery_panel_commands(bot):
    """Registra todos os comandos do painel de loterias no bot"""

    @bot.command(name="painel_loteria_status", aliases=["lottery_panel_status"])
    @require_economy_admin()
    async def lottery_panel_status(ctx):
        """
        Mostra o status do painel de histórico de loterias
        """
        try:
            if not hasattr(ctx.bot, 'lottery_panel') or not ctx.bot.lottery_panel:
                await ctx.send("❌ Sistema de painel de loterias não está disponível.")
                return

            panel = ctx.bot.lottery_panel
            
            embed = discord.Embed(
                title="📊 Status do Painel de Loterias",
                description="Estado atual do sistema de painel de histórico",
                color=0x00ff00 if panel.is_running else 0xff9900,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Status geral
            status_text = "🟢 Ativo" if panel.is_running else "🟡 Inativo"
            embed.add_field(
                name="🔄 Status",
                value=status_text,
                inline=True
            )
            
            # Estatísticas por servidor
            guild_count = len(panel.panel_message_ids)
            embed.add_field(
                name="🏰 Servidores Ativos",
                value=f"{guild_count} servidor(es)",
                inline=True
            )
            
            # Histórico disponível
            if hasattr(ctx.bot.lottery, 'lottery_history'):
                history_count = len(ctx.bot.lottery.lottery_history)
                embed.add_field(
                    name="📋 Registros no Histórico",
                    value=f"{history_count} sorteio(s)",
                    inline=True
                )
            
            # Informações específicas do servidor atual
            if ctx.guild.id in panel.panel_message_ids:
                message_info = panel.panel_message_ids[ctx.guild.id]
                embed.add_field(
                    name="📍 Status neste Servidor",
                    value=f"Canal: <#{message_info['channel_id']}>\nMensagem: [Ver Painel](https://discord.com/channels/{ctx.guild.id}/{message_info['channel_id']}/{message_info['message_id']})",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📍 Status neste Servidor",
                    value="⚠️ Painel não configurado neste servidor",
                    inline=False
                )
            
            embed.set_footer(text="ARCA Organization - Sistema de Painel de Loterias")
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Erro ao verificar status do painel de loterias: {e}")
            await ctx.send(f"❌ Erro ao verificar status: {str(e)}")

        # Deletar comando administrativo se configurado
        await delete_command_if_configured(ctx, "admin")

    @bot.command(name="painel_loteria_criar", aliases=["lottery_panel_create"])
    @require_economy_admin()
    async def lottery_panel_create(ctx, channel: discord.TextChannel = None):
        """
        Cria ou recria o painel de histórico de loterias em um canal
        """
        try:
            if not hasattr(ctx.bot, 'lottery_panel') or not ctx.bot.lottery_panel:
                await ctx.send("❌ Sistema de painel de loterias não está disponível.")
                return

            # Se não especificar canal, usar o atual
            if not channel:
                channel = ctx.channel

            panel = ctx.bot.lottery_panel
            
            # Criar ou recriar painel
            success = await panel.create_panel(ctx.guild.id, channel.id, force_recreate=True)
            
            if success:
                embed = discord.Embed(
                    title="✅ Painel de Loterias Criado",
                    description=f"Painel criado com sucesso no canal {channel.mention}",
                    color=0x00ff00,
                    timestamp=datetime.now(timezone.utc)
                )
                
                embed.add_field(
                    name="📍 Localização",
                    value=f"Canal: {channel.mention}",
                    inline=False
                )
                
                embed.add_field(
                    name="🔄 Atualização",
                    value=f"Atualiza a cada {ctx.bot.config.lottery.panel_update_interval} segundos",
                    inline=False
                )
                
                embed.set_footer(text="ARCA Organization - Painel Criado")
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Falha ao criar o painel. Verifique as permissões do bot no canal.")

        except Exception as e:
            logger.error(f"Erro ao criar painel de loterias: {e}")
            await ctx.send(f"❌ Erro ao criar painel: {str(e)}")

        # Deletar comando administrativo se configurado
        await delete_command_if_configured(ctx, "admin")

    @bot.command(name="painel_loteria_remover", aliases=["lottery_panel_remove"])
    @require_economy_admin()
    async def lottery_panel_remove(ctx):
        """
        Remove o painel de histórico de loterias deste servidor
        """
        try:
            if not hasattr(ctx.bot, 'lottery_panel') or not ctx.bot.lottery_panel:
                await ctx.send("❌ Sistema de painel de loterias não está disponível.")
                return

            panel = ctx.bot.lottery_panel
            
            if ctx.guild.id not in panel.panels:
                await ctx.send("⚠️ Este servidor não possui um painel de loterias configurado.")
                return

            # Remover painel
            success = await panel.remove_panel(ctx.guild.id)
            
            if success:
                embed = discord.Embed(
                    title="✅ Painel de Loterias Removido",
                    description="Painel removido com sucesso deste servidor",
                    color=0x00ff00,
                    timestamp=datetime.now(timezone.utc)
                )
                
                embed.set_footer(text="ARCA Organization - Painel Removido")
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Falha ao remover o painel.")

        except Exception as e:
            logger.error(f"Erro ao remover painel de loterias: {e}")
            await ctx.send(f"❌ Erro ao remover painel: {str(e)}")

        # Deletar comando administrativo se configurado
        await delete_command_if_configured(ctx, "admin")

    @bot.command(name="painel_loteria_atualizar", aliases=["lottery_panel_update"])
    @require_economy_admin()
    async def lottery_panel_update(ctx):
        """
        Força atualização do painel de loterias
        """
        try:
            if not hasattr(ctx.bot, 'lottery_panel') or not ctx.bot.lottery_panel:
                await ctx.send("❌ Sistema de painel de loterias não está disponível.")
                return

            panel = ctx.bot.lottery_panel
            
            # Verificar se há painel configurado neste servidor
            if ctx.guild.id not in panel.panel_message_ids:
                await ctx.send("⚠️ Este servidor não possui um painel de loterias configurado.")
                return

            # Forçar atualização
            await panel.force_update(ctx.guild)
            
            embed = discord.Embed(
                title="🔄 Painel de Loterias Atualizado",
                description="Painel atualizado com sucesso!",
                color=0x00ff00,
                timestamp=datetime.now(timezone.utc)
            )
            
            message_info = panel.panel_message_ids[ctx.guild.id]
            embed.add_field(
                name="📍 Localização",
                value=f"Canal: <#{message_info['channel_id']}>\n[Ver Painel](https://discord.com/channels/{ctx.guild.id}/{message_info['channel_id']}/{message_info['message_id']})",
                inline=False
            )
            
            embed.set_footer(text="ARCA Organization - Painel Atualizado")
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Erro ao atualizar painel de loterias: {e}")
            await ctx.send(f"❌ Erro ao atualizar painel: {str(e)}")

        # Deletar comando administrativo se configurado
        await delete_command_if_configured(ctx, "admin")

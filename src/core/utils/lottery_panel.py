#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Painel de Sorteios do ARCA Bot

Exibe um painel em tempo real com o histórico de sorteios
em um canal específico, com atualização automática.

Autor: ARCA Organization
Licença: MIT
"""

import discord
import asyncio
import logging
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger("ARCA-Bot")


@dataclass
class LotteryEntry:
    """Entrada de sorteio para o painel"""

    id: str
    name: str
    creator_id: int
    status: str  # "ativo", "finalizado", "cancelado"
    participants_count: int
    total_tickets: int
    total_value: int
    base_price: int
    created_at: float
    finished_at: Optional[float]
    winner: Optional[Dict]


class LotteryPanel:
    """Sistema de painel de sorteios"""

    def __init__(self, bot, lottery_system):
        self.bot = bot
        self.lottery_system = lottery_system
        self.config = bot.config.lottery
        self.panel_messages: Dict[int, discord.Message] = {}  # guild_id -> message
        self.panel_data_file = "data/panel_data.json"  # Usar mesmo arquivo que wallet_panel
        self.update_task = None
        self.update_interval = getattr(self.config, 'panel_update_interval', 300)  # 5 minutos
        self.is_running = False

        # Carregar dados do painel
        self.load_panel_data()

    def load_panel_data(self):
        """Carrega dados salvos do painel"""
        try:
            if os.path.exists(self.panel_data_file):
                with open(self.panel_data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Recuperar dados do lottery panel da estrutura compartilhada
                    lottery_data = data.get("lottery_panels", {})
                    self.panel_message_ids = lottery_data.get("panel_message_ids", {})
                logger.info(f"Dados do painel de sorteios carregados")
            else:
                self.panel_message_ids = {}
                logger.info("Dados do painel de sorteios não encontrados, criando novos")
        except Exception as e:
            logger.error(f"Erro ao carregar dados do painel de sorteios: {e}")
            self.panel_message_ids = {}

    def save_panel_data(self):
        """Salva dados do painel"""
        try:
            os.makedirs(
                (
                    os.path.dirname(self.panel_data_file)
                    if os.path.dirname(self.panel_data_file)
                    else "."
                ),
                exist_ok=True,
            )

            # Carregar dados existentes para preservar wallet_panels
            existing_data = {}
            if os.path.exists(self.panel_data_file):
                try:
                    with open(self.panel_data_file, "r", encoding="utf-8") as f:
                        existing_data = json.load(f)
                except:
                    existing_data = {}

            # Salvar apenas os IDs das mensagens do lottery panel
            panel_data = {}
            for guild_id, message in self.panel_messages.items():
                panel_data[str(guild_id)] = message.id

            lottery_panel_data = {
                "panel_message_ids": panel_data,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }

            # Manter estrutura compartilhada
            final_data = existing_data.copy()
            final_data["lottery_panels"] = lottery_panel_data

            with open(self.panel_data_file, "w", encoding="utf-8") as f:
                json.dump(final_data, f, indent=2, ensure_ascii=False)

            logger.debug("Dados do painel de sorteios salvos")
        except Exception as e:
            logger.error(f"Erro ao salvar dados do painel de sorteios: {e}")

    async def start_panel_system(self):
        """Inicia o sistema de painel"""
        if self.is_running:
            logger.warning("Sistema de painel de sorteios já está rodando")
            return

        if not getattr(self.config, 'history_panel_enabled', True):
            logger.info("Painel de histórico de sorteios desabilitado na configuração")
            return

        self.is_running = True
        logger.info("Iniciando sistema de painel de sorteios...")

        # Aguardar o bot estar pronto
        await self.bot.wait_until_ready()

        # Tentar recuperar mensagens existentes
        await self.recover_panel_messages()

        # Iniciar task de atualização
        self.update_task = asyncio.create_task(self.update_loop())

    async def stop_panel_system(self):
        """Para o sistema de painel"""
        if not self.is_running:
            return

        self.is_running = False
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass

        logger.info("Sistema de painel de sorteios parado")

    async def recover_panel_messages(self):
        """Recupera mensagens do painel após restart"""
        try:
            for guild_id_str, message_id in self.panel_message_ids.items():
                try:
                    guild_id = int(guild_id_str)
                    guild = self.bot.get_guild(guild_id)
                    if not guild:
                        continue

                    # Buscar canal do painel
                    panel_channel = discord.utils.get(
                        guild.channels, 
                        name=getattr(self.config, 'history_panel_channel', 'painel-sorteios')
                    )
                    
                    if not panel_channel:
                        continue

                    # Tentar buscar a mensagem
                    try:
                        message = await panel_channel.fetch_message(message_id)
                        self.panel_messages[guild_id] = message
                        logger.info(f"Mensagem do painel de sorteios recuperada para {guild.name}")
                    except discord.NotFound:
                        logger.info(f"Mensagem do painel não encontrada em {guild.name}, será criada nova")
                        del self.panel_message_ids[guild_id_str]

                except Exception as e:
                    logger.error(f"Erro ao recuperar painel para guild {guild_id}: {e}")

        except Exception as e:
            logger.error(f"Erro na recuperação de painéis: {e}")

    async def update_loop(self):
        """Loop principal de atualização do painel"""
        while self.is_running:
            try:
                await self.update_all_panels()
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no loop de atualização do painel de sorteios: {e}")
                await asyncio.sleep(60)  # Aguardar 1 minuto antes de tentar novamente

    async def update_all_panels(self):
        """Atualiza todos os painéis ativos"""
        try:
            for guild in self.bot.guilds:
                try:
                    # Buscar canal do painel
                    panel_channel = discord.utils.get(
                        guild.channels, 
                        name=getattr(self.config, 'history_panel_channel', 'painel-sorteios')
                    )
                    
                    if not panel_channel:
                        continue

                    await self.update_panel_for_guild(guild, panel_channel)

                except Exception as e:
                    logger.error(f"Erro ao atualizar painel para {guild.name}: {e}")

        except Exception as e:
            logger.error(f"Erro na atualização de painéis: {e}")

    async def update_panel_for_guild(self, guild: discord.Guild, channel: discord.TextChannel):
        """Atualiza o painel para uma guild específica"""
        try:
            # Criar embed do painel
            embed = await self.create_lottery_panel_embed(guild)
            
            # Verificar se já existe mensagem do painel
            if guild.id in self.panel_messages:
                try:
                    message = self.panel_messages[guild.id]
                    await message.edit(embed=embed)
                    logger.debug(f"Painel de sorteios atualizado para {guild.name}")
                except (discord.NotFound, discord.HTTPException):
                    # Mensagem foi deletada, criar nova
                    del self.panel_messages[guild.id]
                    if str(guild.id) in self.panel_message_ids:
                        del self.panel_message_ids[str(guild.id)]

            # Se não existe mensagem, criar nova
            if guild.id not in self.panel_messages:
                try:
                    message = await channel.send(embed=embed)
                    self.panel_messages[guild.id] = message
                    self.panel_message_ids[str(guild.id)] = message.id
                    self.save_panel_data()
                    logger.info(f"Painel de sorteios criado para {guild.name}")
                except discord.Forbidden:
                    logger.warning(f"Sem permissão para enviar mensagem no canal {channel.name} em {guild.name}")
                except Exception as e:
                    logger.error(f"Erro ao criar painel em {guild.name}: {e}")

        except Exception as e:
            logger.error(f"Erro ao atualizar painel para {guild.name}: {e}")

    async def create_lottery_panel_embed(self, guild: discord.Guild) -> discord.Embed:
        """Cria embed do painel de sorteios"""
        embed = discord.Embed(
            title="🎲 **PAINEL DE SORTEIOS ARCA** 🎲",
            description="*Histórico e status dos sorteios da organização*",
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc)
        )

        # Adicionar sorteios ativos
        active_lotteries = []
        for lottery_id, lottery_data in self.lottery_system.active_lotteries.items():
            if lottery_data.get("guild_id") == guild.id:
                active_lotteries.append(lottery_data)

        if active_lotteries:
            active_text = []
            for lottery in active_lotteries[:3]:  # Máximo 3 ativos
                status = "🏆 Finalizado" if lottery.get("winner") else "❌ Cancelado" if lottery.get("cancelled") else "🎲 Ativo"
                participants = len(lottery.get("participants", {}))
                active_text.append(f"**{lottery.get('name', 'Sem nome')}**\n{status} • {participants} participantes")
            
            embed.add_field(
                name="🎯 Sorteios Ativos",
                value="\n\n".join(active_text),
                inline=False
            )
        else:
            embed.add_field(
                name="🎯 Sorteios Ativos",
                value="*Nenhum sorteio ativo no momento*",
                inline=False
            )

        # Adicionar histórico recente
        recent_history = []
        guild_history = [
            entry for entry in self.lottery_system.lottery_history 
            if entry.get("guild_id") == guild.id
        ]
        
        # Ordenar por data mais recente
        guild_history.sort(key=lambda x: x.get("finished_at", 0), reverse=True)
        
        max_history = getattr(self.config, 'max_history_entries', 10)
        for entry in guild_history[:max_history]:
            try:
                # Formatação da data
                finished_at = entry.get("finished_at")
                if finished_at:
                    date_str = f"<t:{int(finished_at)}:d>"
                else:
                    date_str = "Data desconhecida"
                
                # Status icon
                status_icon = "🏆" if entry.get("status") == "finalizado" else "❌"
                
                # Winner info
                winner_info = ""
                if entry.get("winner") and entry.get("status") == "finalizado":
                    winner_id = entry["winner"].get("user_id")
                    if winner_id:
                        winner_info = f" • Vencedor: <@{winner_id}>"
                
                # Valor total
                total_value = entry.get("total_value", 0)
                
                recent_history.append(
                    f"{status_icon} **{entry.get('name', 'Sem nome')}**\n"
                    f"📅 {date_str} • 💰 {total_value} AC • 👥 {entry.get('participants_count', 0)}{winner_info}"
                )
                
            except Exception as e:
                logger.error(f"Erro ao formatar entry do histórico: {e}")
                continue

        if recent_history:
            embed.add_field(
                name="📚 Histórico Recente",
                value="\n\n".join(recent_history),
                inline=False
            )
        else:
            embed.add_field(
                name="📚 Histórico Recente",
                value="*Nenhum sorteio no histórico*",
                inline=False
            )

        # Estatísticas gerais
        total_lotteries = len(guild_history)
        total_participants = sum(entry.get("participants_count", 0) for entry in guild_history)
        total_value_distributed = sum(entry.get("total_value", 0) for entry in guild_history)
        
        embed.add_field(
            name="📊 Estatísticas Gerais",
            value=(
                f"🎲 **Total de sorteios:** {total_lotteries}\n"
                f"👥 **Total de participações:** {total_participants}\n"
                f"💰 **Valor total movimentado:** {total_value_distributed} AC"
            ),
            inline=False
        )

        embed.set_footer(
            text=f"🎮 ARCA Organization | Atualizado a cada {self.update_interval // 60} minutos"
        )

        return embed

    async def force_update(self, guild: discord.Guild = None):
        """Força atualização do painel"""
        if guild:
            panel_channel = discord.utils.get(
                guild.channels, 
                name=getattr(self.config, 'history_panel_channel', 'painel-sorteios')
            )
            if panel_channel:
                await self.update_panel_for_guild(guild, panel_channel)
        else:
            await self.update_all_panels()

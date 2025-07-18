#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Painel de Carteiras do ARCA Bot

Exibe um painel em tempo real com os saldos de todos os usuários
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
class WalletEntry:
    """Entrada de carteira para o painel"""

    user_id: int
    display_name: str
    balance: int
    total_earned: int
    voice_time: int
    last_activity: datetime


class WalletPanel:
    """Sistema de painel de carteiras"""

    def __init__(self, bot, economy_system):
        self.bot = bot
        self.economy = economy_system
        self.config = bot.config.general
        self.panel_messages: Dict[int, discord.Message] = {}  # guild_id -> message
        self.panel_data_file = (
            "data/panel_data.json"  # Arquivo para salvar dados do painel
        )
        self.update_task = None
        self.update_interval = 300  # 5 minutos
        self.is_running = False

        # Carregar dados salvos do painel
        self._load_panel_data()

    def _load_panel_data(self):
        """Carrega dados salvos do painel"""
        try:
            if os.path.exists(self.panel_data_file):
                with open(self.panel_data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Os dados serão recarregados na inicialização usando os IDs salvos
                    logger.info(
                        f"📂 Dados do painel carregados: {len(data)} servidores"
                    )
            else:
                logger.info(
                    "📂 Nenhum arquivo de dados do painel encontrado, será criado automaticamente"
                )
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados do painel: {e}")

    async def _save_panel_data(self):
        """Salva dados do painel"""
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(self.panel_data_file), exist_ok=True)

            # Preparar dados para salvar
            data = {}
            for guild_id, message in self.panel_messages.items():
                guild = self.bot.get_guild(guild_id)
                if guild:
                    data[str(guild_id)] = {
                        "guild_name": guild.name,
                        "channel_id": message.channel.id,
                        "channel_name": message.channel.name,
                        "message_id": message.id,
                        "last_updated": datetime.now(timezone.utc).isoformat(),
                    }

            # Salvar no arquivo
            with open(self.panel_data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Dados do painel salvos: {len(data)} servidores")

        except Exception as e:
            logger.error(f"❌ Erro ao salvar dados do painel: {e}")

    async def start(self):
        """Inicia o sistema de painel"""
        if self.is_running:
            return

        logger.info("🚀 Iniciando sistema de painel de carteiras...")
        self.is_running = True

        # Buscar painéis existentes em todos os servidores
        await self._find_existing_panels()

        self.update_task = asyncio.create_task(self._update_loop())
        logger.info("✅ Sistema de painel de carteiras iniciado completamente")

    async def _find_existing_panels(self):
        """Busca painéis existentes nos canais configurados"""
        total_guilds = len(self.bot.guilds)
        panels_found = 0
        panels_created = 0

        logger.info(f"🔍 Buscando painéis existentes em {total_guilds} servidor(es)...")

        # Tentar carregar dados salvos primeiro
        try:
            if os.path.exists(self.panel_data_file):
                with open(self.panel_data_file, "r", encoding="utf-8") as f:
                    saved_data = json.load(f)

                # Tentar recuperar painéis salvos
                for guild_id_str, panel_info in saved_data.items():
                    guild_id = int(guild_id_str)
                    guild = self.bot.get_guild(guild_id)

                    if guild:
                        try:
                            channel = guild.get_channel(panel_info["channel_id"])
                            if channel:
                                message = await channel.fetch_message(
                                    panel_info["message_id"]
                                )
                                if message and message.author == self.bot.user:
                                    self.panel_messages[guild_id] = message
                                    panels_found += 1
                                    logger.info(
                                        f"✅ Painel salvo recuperado no servidor {guild.name} (ID: {message.id})"
                                    )

                                    # Atualizar o painel encontrado imediatamente
                                    await self.update_panel(guild)
                                    logger.info(
                                        f"🔄 Painel atualizado no servidor {guild.name}"
                                    )
                                    continue
                        except Exception as e:
                            logger.warning(
                                f"⚠️ Painel salvo não pôde ser recuperado no servidor {guild.name}: {e}"
                            )
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados salvos: {e}")

        # Para guilds sem painel salvo ou recuperação falhou, buscar manualmente
        for guild in self.bot.guilds:
            if guild.id in self.panel_messages:
                continue  # Já foi recuperado dos dados salvos

            try:
                channel = await self.get_wallet_channel(guild)
                if not channel:
                    logger.warning(
                        f"❌ Canal '{self.config.wallet_panel_channel}' não encontrado no servidor {guild.name}"
                    )
                    continue

                logger.info(
                    f"🔎 Verificando canal #{channel.name} no servidor {guild.name}..."
                )

                # Buscar mensagens do bot no canal
                panel_found = False
                async for message in channel.history(limit=50):
                    if (
                        message.author == self.bot.user
                        and message.embeds
                        and "💰 Painel de Carteiras ARCA" in message.embeds[0].title
                    ):

                        self.panel_messages[guild.id] = message
                        panels_found += 1
                        panel_found = True
                        logger.info(
                            f"✅ Painel existente encontrado no servidor {guild.name} (ID: {message.id})"
                        )

                        # Salvar dados do painel encontrado
                        await self._save_panel_data()

                        # Atualizar o painel encontrado imediatamente
                        await self.update_panel(guild)
                        logger.info(f"🔄 Painel atualizado no servidor {guild.name}")
                        break

                if not panel_found:
                    # Se não encontrou painel, criar um novo
                    logger.info(
                        f"❓ Nenhum painel encontrado no servidor {guild.name}, criando novo..."
                    )
                    success = await self.create_panel_in_guild(guild)
                    if success:
                        panels_created += 1
                        logger.info(f"✅ Novo painel criado no servidor {guild.name}")
                    else:
                        logger.error(
                            f"❌ Falha ao criar painel no servidor {guild.name}"
                        )

            except Exception as e:
                logger.error(f"❌ Erro ao buscar painel no servidor {guild.name}: {e}")

        # Salvar dados atualizados
        await self._save_panel_data()

        logger.info(
            f"📊 Resumo de painéis: {panels_found} encontrados, {panels_created} criados, {total_guilds} servidores verificados"
        )

    async def stop(self):
        """Para o sistema de painel"""
        self.is_running = False
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
        logger.info("Sistema de painel de carteiras parado")

    async def _update_loop(self):
        """Loop principal de atualização"""
        logger.info(
            f"🔄 Loop de atualização automática iniciado (intervalo: {self.update_interval // 60} minutos)"
        )

        while self.is_running:
            try:
                logger.info(
                    "🔄 Iniciando atualização automática de todos os painéis..."
                )
                await self._update_all_panels()
                logger.info(
                    f"✅ Atualização automática concluída. Próxima em {self.update_interval // 60} minutos"
                )
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop de atualização do painel: {e}")
                await asyncio.sleep(60)  # Esperar 1 minuto em caso de erro

    async def _update_all_panels(self):
        """Atualiza todos os painéis em todos os servidores"""
        updated_count = 0

        for guild in self.bot.guilds:
            try:
                if guild.id in self.panel_messages:
                    await self.update_panel(guild)
                    updated_count += 1
                else:
                    logger.warning(
                        f"⚠️ Painel não encontrado para o servidor {guild.name}, tentando criar..."
                    )
                    success = await self.create_panel_in_guild(guild)
                    if success:
                        updated_count += 1
                        logger.info(
                            f"✅ Painel criado e atualizado no servidor {guild.name}"
                        )
            except Exception as e:
                logger.error(
                    f"❌ Erro ao atualizar painel do servidor {guild.name}: {e}"
                )

        logger.info(
            f"📊 Painéis atualizados: {updated_count}/{len(self.bot.guilds)} servidores"
        )

    async def get_wallet_channel(
        self, guild: discord.Guild
    ) -> Optional[discord.TextChannel]:
        """Encontra o canal de painel de carteiras"""
        channel_name = self.config.wallet_panel_channel

        for channel in guild.text_channels:
            if channel.name.lower() == channel_name.lower():
                return channel
        return None

    def _get_wallet_data(self, guild: discord.Guild) -> List[WalletEntry]:
        """Obtém dados de carteira para o servidor"""
        wallet_entries = []

        # Filtrar apenas membros do servidor atual
        guild_member_ids = {member.id for member in guild.members if not member.bot}

        for user_id_str, user_data in self.economy.user_data.items():
            user_id = int(user_id_str)

            # Verificar se o usuário está no servidor
            if user_id not in guild_member_ids:
                continue

            # Obter membro do servidor
            member = guild.get_member(user_id)
            if not member:
                continue

            # Criar entrada de carteira
            entry = WalletEntry(
                user_id=user_id,
                display_name=member.display_name,
                balance=user_data.get("balance", 0),
                total_earned=user_data.get("total_earned", 0),
                voice_time=user_data.get("voice_time", 0),
                last_activity=(
                    datetime.fromisoformat(user_data.get("last_daily"))
                    if user_data.get("last_daily")
                    else datetime.now(timezone.utc)
                ),
            )

            wallet_entries.append(entry)

        # Ordenar por saldo (maior para menor)
        wallet_entries.sort(key=lambda x: x.balance, reverse=True)

        return wallet_entries

    def _create_panel_embed(
        self, guild: discord.Guild, wallet_data: List[WalletEntry]
    ) -> discord.Embed:
        """Cria o embed do painel de carteiras"""
        embed = discord.Embed(
            title="💰 Painel de Carteiras ARCA",
            description=f"**{guild.name}** | Atualizado automaticamente a cada 5 minutos",
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc),
        )

        if not wallet_data:
            embed.add_field(
                name="📊 Status", value="Nenhum usuário com AC encontrado", inline=False
            )
            return embed

        # Estatísticas gerais
        total_ac = sum(entry.balance for entry in wallet_data)
        total_earned = sum(entry.total_earned for entry in wallet_data)
        active_users = len([entry for entry in wallet_data if entry.balance > 0])

        embed.add_field(
            name="📊 Estatísticas Gerais",
            value=(
                f"**Total em Circulação:** {total_ac:,} AC\n"
                f"**Total Já Distribuído:** {total_earned:,} AC\n"
                f"**Usuários Ativos:** {active_users}\n"
                f"**Total de Usuários:** {len(wallet_data)}"
            ),
            inline=False,
        )

        # Todos os usuários (limitado a 1024 caracteres por field do Discord)
        all_users = wallet_data

        leaderboard_text = ""
        for i, entry in enumerate(all_users, 1):
            # Emojis para top 3
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"**{i}.**"

            line = f"{medal} {entry.display_name} - **{entry.balance:,} AC**\n"

            # Verificar se ainda cabe no limit do Discord (1024 caracteres por field)
            if len(leaderboard_text + line) > 1024:
                # Se não cabe, adicionar indicação de mais usuários
                remaining = len(all_users) - i + 1
                if remaining > 0:
                    leaderboard_text += f"... e mais {remaining} usuários"
                break

            leaderboard_text += line

        embed.add_field(
            name="🏆 Ranking de Carteiras",
            value=leaderboard_text or "Nenhum usuário encontrado",
            inline=False,
        )

        # Estatísticas de distribuição
        if len(wallet_data) >= 5:
            # Quartis de distribuição
            sorted_balances = sorted(
                [entry.balance for entry in wallet_data if entry.balance > 0],
                reverse=True,
            )
            if sorted_balances:
                median_balance = sorted_balances[len(sorted_balances) // 2]
                avg_balance = total_ac // len(sorted_balances)

                embed.add_field(
                    name="📈 Distribuição de Riqueza",
                    value=(
                        f"**Maior Carteira:** {sorted_balances[0]:,} AC\n"
                        f"**Carteira Mediana:** {median_balance:,} AC\n"
                        f"**Carteira Média:** {avg_balance:,} AC\n"
                        f"**Menor Carteira:** {sorted_balances[-1]:,} AC"
                    ),
                    inline=True,
                )

        # Últimas atividades
        recent_active = sorted(
            [entry for entry in wallet_data if entry.balance > 0],
            key=lambda x: x.last_activity,
            reverse=True,
        )[:5]

        if recent_active:
            activity_text = ""
            for entry in recent_active:
                days_ago = (datetime.now(timezone.utc) - entry.last_activity).days
                if days_ago == 0:
                    activity_str = "hoje"
                elif days_ago == 1:
                    activity_str = "ontem"
                else:
                    activity_str = f"{days_ago} dias atrás"

                activity_text += f"👤 **{entry.display_name}** - {activity_str}\n"

            embed.add_field(
                name="🕐 Atividade Recente", value=activity_text, inline=True
            )

        embed.set_footer(
            text="ARCA Bot | Painel atualizado automaticamente",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None,
        )

        return embed

    async def update_panel(self, guild: discord.Guild):
        """Atualiza o painel de um servidor específico"""
        try:
            # Encontrar canal
            channel = await self.get_wallet_channel(guild)
            if not channel:
                # Se não tem o canal, remove da lista de painéis
                if guild.id in self.panel_messages:
                    del self.panel_messages[guild.id]
                logger.warning(
                    f"⚠️ Canal de painel não encontrado no servidor {guild.name}"
                )
                return

            # Obter dados
            wallet_data = self._get_wallet_data(guild)
            embed = self._create_panel_embed(guild, wallet_data)

            # Verificar se já existe uma mensagem
            if guild.id in self.panel_messages:
                try:
                    # Tentar atualizar mensagem existente
                    message = self.panel_messages[guild.id]
                    await message.edit(embed=embed)
                    logger.info(
                        f"🔄 Painel atualizado no servidor {guild.name} (#{channel.name})"
                    )
                    return
                except (discord.NotFound, discord.HTTPException):
                    # Mensagem foi deletada, criar nova
                    del self.panel_messages[guild.id]
                    logger.warning(
                        f"⚠️ Mensagem de painel perdida no servidor {guild.name}, criando nova..."
                    )

            # Criar nova mensagem
            try:
                # Limpar mensagens antigas do bot no canal (últimas 10)
                async for msg in channel.history(limit=10):
                    if msg.author == self.bot.user and "Painel de Carteiras" in (
                        msg.embeds[0].title if msg.embeds else ""
                    ):
                        try:
                            await msg.delete()
                        except Exception:
                            pass

                # Enviar nova mensagem
                message = await channel.send(embed=embed)
                self.panel_messages[guild.id] = message

                # Salvar dados do painel
                await self._save_panel_data()

                logger.info(
                    f"✅ Novo painel criado no servidor {guild.name} (#{channel.name})"
                )
                logger.info(f"Painel de carteiras criado/atualizado em {guild.name}")

            except discord.Forbidden:
                logger.warning(
                    f"Sem permissão para enviar mensagem no canal {channel.name} em {guild.name}"
                )
            except Exception as e:
                logger.error(f"Erro ao criar painel em {guild.name}: {e}")

        except Exception as e:
            logger.error(f"Erro ao atualizar painel em {guild.name}: {e}")

    async def force_update_all(self):
        """Força atualização imediata de todos os painéis"""
        await self._update_all_panels()

    async def create_panel_in_guild(self, guild: discord.Guild) -> bool:
        """Cria painel em um servidor específico"""
        try:
            channel = await self.get_wallet_channel(guild)
            if not channel:
                return False

            await self.update_panel(guild)
            return True
        except Exception as e:
            logger.error(f"Erro ao criar painel em {guild.name}: {e}")
            return False

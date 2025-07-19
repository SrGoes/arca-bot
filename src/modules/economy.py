#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Economia do ARCA Bot

Gerencia Arca Coins (AC), recompensas por tempo em voz,
comandos diários e distribuição de moedas.

Autor: ARCA Organization
Licença: MIT
"""

import json
import os
import shutil
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import discord
from discord.ext import tasks
import logging

logger = logging.getLogger("ARCA-Bot")


class EconomySystem:
    """Sistema de economia do bot ARCA"""

    def __init__(self, bot):
        self.bot = bot
        self.data_file = os.path.join("data", "economy_data.json")
        self.backup_dir = "backups"
        self.config = bot.config.economy  # Usar configuração centralizada

        # Configurações do config
        self.voice_channels_category = self.config.voice_channels_category
        self.ac_per_hour = self.config.ac_per_hour
        self.daily_reward_min = self.config.daily_reward_min
        self.daily_reward_max = self.config.daily_reward_max
        self.admin_role_name = self.config.admin_role_name
        self.min_voice_time_for_reward = self.config.min_voice_time_for_reward

        # Dados em memória
        self.user_data = {}
        self.voice_tracking = (
            {}
        )  # {user_id: {'start_time': datetime, 'channel_id': int, 'last_reward_time': datetime}}
        self.voice_status_messages = (
            {}
        )  # {channel_id: {'message': Message, 'last_update': datetime}}

        # Carregar dados
        self.load_data()

        # Iniciar tarefas em background
        self.voice_reward_task.start()
        self.voice_status_task.start()
        self.backup_task.start()

    def load_data(self):
        """Carrega dados do arquivo JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.user_data = data.get("users", {})
                logger.info(
                    f"Dados de economia carregados: {len(self.user_data)} usuários"
                )
            else:
                self.user_data = {}
                logger.info("Arquivo de economia não encontrado, criando novo")
        except Exception as e:
            logger.error(f"Erro ao carregar dados de economia: {e}")
            self.user_data = {}

    def save_data(self):
        """Salva dados no arquivo JSON"""
        try:
            os.makedirs(
                (
                    os.path.dirname(self.data_file)
                    if os.path.dirname(self.data_file)
                    else "."
                ),
                exist_ok=True,
            )

            data = {"users": self.user_data, "last_updated": datetime.now(timezone.utc).isoformat()}

            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug("Dados de economia salvos")
        except Exception as e:
            logger.error(f"Erro ao salvar dados de economia: {e}")

    def get_user_data(self, user_id: int) -> Dict:
        """Obtém dados do usuário, criando se necessário"""
        user_id_str = str(user_id)
        if user_id_str not in self.user_data:
            self.user_data[user_id_str] = {
                "balance": 0,
                "last_daily": None,
                "total_earned": 0,
                "voice_time": 0,  # Tempo total em minutos
            }
        return self.user_data[user_id_str]

    def add_coins(self, user_id: int, amount: int, reason: str = ""):
        """Adiciona moedas ao usuário"""
        user_data = self.get_user_data(user_id)
        user_data["balance"] += amount
        user_data["total_earned"] += amount
        self.save_data()
        logger.info(f"Adicionados {amount} AC para usuário {user_id}. Motivo: {reason}")

    def remove_coins(self, user_id: int, amount: int) -> bool:
        """Remove moedas do usuário. Retorna True se bem-sucedido"""
        user_data = self.get_user_data(user_id)
        if user_data["balance"] >= amount:
            user_data["balance"] -= amount
            self.save_data()
            return True
        return False

    def refund_coins(self, user_id: int, amount: int, reason: str = ""):
        """Reembolsa moedas ao usuário sem afetar o total_earned"""
        user_data = self.get_user_data(user_id)
        user_data["balance"] += amount
        self.save_data()
        logger.info(f"Reembolsados {amount} AC para usuário {user_id}. Motivo: {reason}")

    def get_balance(self, user_id: int) -> int:
        """Obtém saldo do usuário"""
        return self.get_user_data(user_id)["balance"]

    def is_in_comms_category(self, channel: discord.VoiceChannel) -> bool:
        """Verifica se o canal está na categoria C.O.M.M.S OPS"""
        if not channel.category:
            return False
        return channel.category.name.upper() == self.voice_channels_category.upper()

    def has_admin_role(self, member: discord.Member) -> bool:
        """Verifica se o membro tem cargo de administrador de economia"""
        return any(role.name == self.admin_role_name for role in member.roles)

    @tasks.loop(minutes=1)
    async def voice_reward_task(self):
        """Task que roda a cada 1 minuto para dar recompensas graduais de voz baseadas no tempo real"""
        try:
            current_time = datetime.now(timezone.utc)

            for user_id, tracking_data in list(self.voice_tracking.items()):
                start_time = tracking_data["start_time"]
                last_reward_time = tracking_data.get("last_reward_time", start_time)

                # Calcular tempo desde a última recompensa em minutos decimais
                time_since_reward = current_time - last_reward_time
                minutes_since_reward = time_since_reward.total_seconds() / 60

                # Dar recompensa a cada 1 minuto completo
                if minutes_since_reward >= 1:
                    # Calcular quantos minutos completos se passaram
                    complete_minutes = int(minutes_since_reward)

                    # Calcular AC baseado na configuração: usar ac_per_hour e min_voice_time_for_reward
                    # Exemplo: se ac_per_hour = 20 e min_voice_time_for_reward = 3
                    # Então: 1 AC a cada 3 minutos (20 AC / (60/3) = 20/20 = 1 AC por período)
                    coins_per_period = self.ac_per_hour / (
                        60 / self.min_voice_time_for_reward
                    )
                    periods_completed = (
                        complete_minutes // self.min_voice_time_for_reward
                    )
                    coins_earned = int(periods_completed * coins_per_period)

                    # Se há moedas para dar
                    if coins_earned > 0:
                        self.add_coins(
                            user_id,
                            coins_earned,
                            f"Tempo em voz ({complete_minutes} min)",
                        )

                        # Atualizar tempo de voz no perfil do usuário
                        user_data = self.get_user_data(user_id)
                        user_data["voice_time"] += complete_minutes

                        # Atualizar tempo da última recompensa para os minutos recompensados
                        minutes_rewarded = (
                            periods_completed * self.min_voice_time_for_reward
                        )
                        new_last_reward = last_reward_time + timedelta(
                            minutes=minutes_rewarded
                        )
                        self.voice_tracking[user_id][
                            "last_reward_time"
                        ] = new_last_reward

                        logger.info(
                            f"Usuário {user_id} recebeu {coins_earned} AC por {complete_minutes} min em voz (configuração: {self.min_voice_time_for_reward}min/{coins_per_period}AC)"
                        )

        except Exception as e:
            logger.error(f"Erro na task de recompensa de voz: {e}")

    @tasks.loop(minutes=2)
    async def voice_status_task(self):
        """Task que atualiza status de voz nos canais a cada 2 minutos"""
        try:
            current_time = datetime.now(timezone.utc)
            logger.info(
                f"🎤 Executando voice_status_task - {len(self.voice_tracking)} usuários sendo trackados"
            )

            # Agrupar usuários por canal
            channels_users = {}
            for user_id, tracking_data in self.voice_tracking.items():
                channel_id = tracking_data["channel_id"]
                if channel_id not in channels_users:
                    channels_users[channel_id] = []
                channels_users[channel_id].append(user_id)

            # Atualizar mensagem para cada canal
            for channel_id, user_ids in channels_users.items():
                try:
                    channel = self.bot.get_channel(channel_id)
                    if not channel:
                        continue

                    # Criar embed com status dos usuários
                    embed = await self.create_voice_status_embed(user_ids, current_time)

                    # Verificar se já existe mensagem para este canal
                    if channel_id in self.voice_status_messages:
                        # Tentar editar mensagem existente
                        try:
                            message = self.voice_status_messages[channel_id]["message"]
                            await message.edit(embed=embed)
                            self.voice_status_messages[channel_id][
                                "last_update"
                            ] = current_time
                        except (discord.NotFound, discord.HTTPException):
                            # Mensagem foi deletada, criar nova
                            del self.voice_status_messages[channel_id]

                    # Se não existe mensagem, criar nova
                    if channel_id not in self.voice_status_messages:
                        try:
                            message = await channel.send(embed=embed)
                            self.voice_status_messages[channel_id] = {
                                "message": message,
                                "last_update": current_time,
                            }
                            logger.info(
                                f"📤 Status da call enviado no canal {channel.name}"
                            )
                        except discord.Forbidden:
                            logger.warning(
                                f"Sem permissão para enviar mensagem no canal {channel_id}"
                            )
                        except Exception as e:
                            logger.error(
                                f"Erro ao enviar mensagem no canal {channel_id}: {e}"
                            )

                except Exception as e:
                    logger.error(f"Erro ao processar canal {channel_id}: {e}")

            # Limpar mensagens de canais vazios
            for channel_id in list(self.voice_status_messages.keys()):
                if channel_id not in channels_users:
                    try:
                        message = self.voice_status_messages[channel_id]["message"]
                        await message.delete()
                        logger.info(
                            f"🗑️ Status da call removido do canal {channel_id} (vazio)"
                        )
                    except Exception:
                        pass
                    del self.voice_status_messages[channel_id]

        except Exception as e:
            logger.error(f"Erro na task de status de voz: {e}")

    @voice_status_task.before_loop
    async def before_voice_status_task(self):
        """Aguarda o bot estar pronto antes de iniciar a task"""
        await self.bot.wait_until_ready()

    async def create_voice_status_embed(
        self, user_ids: List[int], current_time: datetime
    ) -> discord.Embed:
        """Cria embed com status dos usuários em voz"""
        embed = discord.Embed(
            title="🎤 Status da Call - ARCA",
            description="**Usuários em C.O.M.M.S OPS**",
            color=discord.Color.blue(),
            timestamp=current_time,
        )

        total_users = len(user_ids)
        status_lines = []

        for user_id in user_ids:
            if user_id in self.voice_tracking:
                tracking_data = self.voice_tracking[user_id]
                start_time = tracking_data["start_time"]

                # Calcular tempo total
                time_diff = current_time - start_time
                total_minutes = int(time_diff.total_seconds() / 60)
                hours = total_minutes // 60
                minutes = total_minutes % 60

                # Calcular AC ganho até agora baseado na configuração
                periods_completed = total_minutes // self.min_voice_time_for_reward
                coins_per_period = self.ac_per_hour / (
                    60 / self.min_voice_time_for_reward
                )
                coins_earned = int(periods_completed * coins_per_period)

                # Formatar tempo
                if hours > 0:
                    time_str = f"{hours}h {minutes}m"
                else:
                    time_str = f"{minutes}m"

                # Buscar usuário
                try:
                    user = self.bot.get_user(user_id)
                    display_name = user.display_name if user else f"Usuário {user_id}"
                except Exception:
                    display_name = f"Usuário {user_id}"

                status_lines.append(
                    f"👤 **{display_name}**\n⏱️ {time_str} | 💰 {coins_earned} AC"
                )

        if status_lines:
            embed.add_field(
                name=f"📊 {total_users} usuário(s) ativo(s)",
                value="\n\n".join(status_lines),
                inline=False,
            )
        else:
            embed.add_field(
                name="📊 Nenhum usuário ativo", value="Canal vazio", inline=False
            )

        coins_per_period = self.ac_per_hour / (60 / self.min_voice_time_for_reward)
        embed.set_footer(text="ARCA Bot | Atualizado a cada 1 min")

        return embed

    @tasks.loop(hours=6)
    async def backup_task(self):
        """Cria backup dos dados a cada 6 horas"""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)

            if os.path.exists(self.data_file):
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(
                    self.backup_dir, f"economy_backup_{timestamp}.json"
                )
                shutil.copy2(self.data_file, backup_file)

                # Manter apenas os últimos 10 backups
                backups = sorted(
                    [
                        f
                        for f in os.listdir(self.backup_dir)
                        if f.startswith("economy_backup_")
                    ]
                )
                while len(backups) > 10:
                    oldest = backups.pop(0)
                    os.remove(os.path.join(self.backup_dir, oldest))

                logger.info(f"Backup criado: {backup_file}")

        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")

    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        """Monitora mudanças de estado de voz"""
        user_id = member.id
        current_time = datetime.now(timezone.utc)

        # Verificar se houve mudança real de canal (ignorar mute/unmute, deaf/undeaf, etc.)
        before_channel = before.channel
        after_channel = after.channel

        # Se não houve mudança de canal, ignorar o evento
        if before_channel == after_channel:
            return

        # Usuário saiu de um canal válido
        if before_channel and self.is_in_comms_category(before_channel):
            if user_id in self.voice_tracking:
                # Calcular tempo final e dar última recompensa
                tracking_data = self.voice_tracking[user_id]
                start_time = tracking_data["start_time"]
                last_reward_time = tracking_data.get("last_reward_time", start_time)

                # Calcular tempo total
                total_time_diff = current_time - start_time
                total_minutes = total_time_diff.total_seconds() / 60

                # Calcular tempo desde última recompensa
                time_since_reward = current_time - last_reward_time
                minutes_since_reward = time_since_reward.total_seconds() / 60

                # Dar recompensa final se houver tempo não recompensado (usar configuração)
                if minutes_since_reward >= self.min_voice_time_for_reward:
                    # Aplicar a mesma lógica configurável
                    complete_minutes = int(minutes_since_reward)
                    coins_per_period = self.ac_per_hour / (
                        60 / self.min_voice_time_for_reward
                    )
                    periods_completed = (
                        complete_minutes // self.min_voice_time_for_reward
                    )
                    final_coins = int(periods_completed * coins_per_period)
                    if final_coins > 0:
                        self.add_coins(
                            user_id,
                            final_coins,
                            f"Tempo final em voz ({complete_minutes} min)",
                        )

                # Atualizar tempo total de voz
                user_data = self.get_user_data(user_id)
                user_data["voice_time"] += int(total_minutes)

                # Remover do tracking
                del self.voice_tracking[user_id]

                logger.info(
                    f"Usuário {user_id} saiu da call após {total_minutes:.1f} minutos"
                )

        # Usuário entrou em um canal válido
        if after_channel and self.is_in_comms_category(after_channel):
            self.voice_tracking[user_id] = {
                "start_time": current_time,
                "channel_id": after_channel.id,
                "last_reward_time": current_time,
            }
            logger.info(f"Usuário {user_id} entrou na call no canal {after_channel.id}")

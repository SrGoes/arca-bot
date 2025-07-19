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
import asyncio
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
        self.voice_tracking_file = os.path.join("data", "voice_tracking_data.json")
        self.backup_dir = "backups"
        self.config = bot.config.economy  # Usar configuração centralizada

        # Configurações do config
        self.voice_channels_category = self.config.voice_channels_category
        self.ac_per_hour = self.config.ac_per_hour
        self.daily_reward_min = self.config.daily_reward_min
        self.daily_reward_max = self.config.daily_reward_max
        self.admin_role_name = self.config.admin_role_name
        self.min_voice_time_for_reward = self.config.min_voice_time_for_reward
        self.max_restart_time_for_recovery = self.config.max_restart_time_for_recovery
        
        # Configurações do sistema de mensagens
        self.message_reward_enabled = self.config.message_reward_enabled
        self.messages_for_reward = self.config.messages_for_reward
        self.message_reward_min = self.config.message_reward_min
        self.message_reward_max = self.config.message_reward_max
        self.message_reward_cooldown = self.config.message_reward_cooldown
        self.send_voice_summary_dm = self.config.send_voice_summary_dm

        # Dados em memória
        self.user_data = {}
        self.voice_tracking = (
            {}
        )  # {user_id: {'start_time': datetime, 'channel_id': int, 'last_reward_time': datetime}}
        self.voice_status_messages = (
            {}
        )  # {channel_id: {'message': Message, 'last_update': datetime}}
        self.voice_tracking_messages = (
            {}
        )  # {channel_id: {'message_id': int, 'last_update': datetime}}
        self.message_tracking = (
            {}
        )  # {user_id: {'count': int, 'last_reward': datetime}}

        # Carregar dados
        self.load_data()
        self.load_voice_tracking_data()

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

    def load_voice_tracking_data(self):
        """Carrega dados de tracking de voz do arquivo JSON"""
        try:
            if os.path.exists(self.voice_tracking_file):
                with open(self.voice_tracking_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    # Recuperar dados de tracking ativo
                    tracking_data = data.get("voice_tracking", {})
                    tracking_messages = data.get("tracking_messages", {})
                    last_save_time = data.get("last_save_time")
                    
                    current_time = datetime.now(timezone.utc)
                    
                    # Verificar se o restart foi recente (tempo configurável)
                    if last_save_time:
                        last_save = datetime.fromisoformat(last_save_time.replace('Z', '+00:00'))
                        time_diff = (current_time - last_save).total_seconds()
                        time_diff_minutes = time_diff / 60
                        
                        if time_diff_minutes <= self.max_restart_time_for_recovery:
                            logger.info(f"🔄 Restart rápido detectado ({time_diff_minutes:.1f}min ≤ {self.max_restart_time_for_recovery}min). Recuperando sessões de voz ativas...")
                            
                            # Restaurar tracking ativo
                            for user_id, track_data in tracking_data.items():
                                # Converter strings ISO para datetime
                                if isinstance(track_data.get("start_time"), str):
                                    track_data["start_time"] = datetime.fromisoformat(track_data["start_time"].replace('Z', '+00:00'))
                                if isinstance(track_data.get("last_reward_time"), str):
                                    track_data["last_reward_time"] = datetime.fromisoformat(track_data["last_reward_time"].replace('Z', '+00:00'))
                                
                                self.voice_tracking[int(user_id)] = track_data
                            
                            # Restaurar IDs das mensagens de tracking
                            for channel_id, msg_data in tracking_messages.items():
                                self.voice_tracking_messages[int(channel_id)] = msg_data
                            
                            logger.info(f"✅ Recuperadas {len(self.voice_tracking)} sessões de voz e {len(self.voice_tracking_messages)} mensagens")
                        else:
                            logger.info(f"⏰ Restart demorado detectado ({time_diff_minutes:.1f}min > {self.max_restart_time_for_recovery}min). Limpando dados antigos...")
                            # Restart demorado - limpar mensagens antigas
                            asyncio.create_task(self.cleanup_old_tracking_messages(tracking_messages))
                    else:
                        logger.info("📝 Primeira inicialização ou dados sem timestamp")
                        
            else:
                logger.info("Arquivo de tracking de voz não encontrado, criando novo")
                
        except Exception as e:
            logger.error(f"Erro ao carregar dados de tracking de voz: {e}")
            self.voice_tracking = {}
            self.voice_tracking_messages = {}

    async def cleanup_old_tracking_messages(self, old_tracking_messages):
        """Remove mensagens de tracking antigas após restart demorado"""
        try:
            await self.bot.wait_until_ready()
            
            for channel_id, msg_data in old_tracking_messages.items():
                try:
                    channel = self.bot.get_channel(int(channel_id))
                    if channel and msg_data.get("message_id"):
                        try:
                            message = await channel.fetch_message(msg_data["message_id"])
                            await message.delete()
                            logger.info(f"🗑️ Mensagem de tracking antiga removida do canal {channel.name}")
                        except discord.NotFound:
                            logger.debug(f"Mensagem de tracking não encontrada no canal {channel_id}")
                        except Exception as e:
                            logger.warning(f"Erro ao remover mensagem antiga do canal {channel_id}: {e}")
                except Exception as e:
                    logger.error(f"Erro geral ao processar limpeza do canal {channel_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Erro na limpeza de mensagens antigas: {e}")

    def save_voice_tracking_data(self):
        """Salva dados de tracking de voz no arquivo JSON"""
        try:
            os.makedirs(
                (
                    os.path.dirname(self.voice_tracking_file)
                    if os.path.dirname(self.voice_tracking_file)
                    else "."
                ),
                exist_ok=True,
            )

            # Converter dados para formato serializável
            tracking_data = {}
            for user_id, track_data in self.voice_tracking.items():
                tracking_data[str(user_id)] = {
                    "start_time": track_data["start_time"].isoformat() if isinstance(track_data["start_time"], datetime) else track_data["start_time"],
                    "channel_id": track_data["channel_id"],
                    "last_reward_time": track_data["last_reward_time"].isoformat() if isinstance(track_data["last_reward_time"], datetime) else track_data["last_reward_time"]
                }

            # Converter mensagens de tracking
            tracking_messages = {}
            for channel_id, msg_data in self.voice_tracking_messages.items():
                tracking_messages[str(channel_id)] = msg_data

            data = {
                "voice_tracking": tracking_data,
                "tracking_messages": tracking_messages,
                "last_save_time": datetime.now(timezone.utc).isoformat()
            }

            with open(self.voice_tracking_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug("Dados de tracking de voz salvos")
        except Exception as e:
            logger.error(f"Erro ao salvar dados de tracking de voz: {e}")

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
                            
                            # Atualizar/salvar ID da mensagem no tracking persistente
                            self.voice_tracking_messages[channel_id] = {
                                "message_id": message.id,
                                "last_update": current_time.isoformat()
                            }
                        except (discord.NotFound, discord.HTTPException):
                            # Mensagem foi deletada, criar nova
                            del self.voice_status_messages[channel_id]
                            if channel_id in self.voice_tracking_messages:
                                del self.voice_tracking_messages[channel_id]

                    # Se não existe mensagem, criar nova
                    if channel_id not in self.voice_status_messages:
                        try:
                            message = await channel.send(embed=embed)
                            self.voice_status_messages[channel_id] = {
                                "message": message,
                                "last_update": current_time,
                            }
                            
                            # Salvar ID da mensagem para persistência
                            self.voice_tracking_messages[channel_id] = {
                                "message_id": message.id,
                                "last_update": current_time.isoformat()
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
                    
                    # Remover também do tracking persistente
                    if channel_id in self.voice_tracking_messages:
                        del self.voice_tracking_messages[channel_id]

            # Salvar dados de tracking após cada atualização
            self.save_voice_tracking_data()

        except Exception as e:
            logger.error(f"Erro na task de status de voz: {e}")

    @voice_status_task.before_loop
    async def before_voice_status_task(self):
        """Aguarda o bot estar pronto antes de iniciar a task"""
        await self.bot.wait_until_ready()
        
        # Tentar recuperar mensagens de tracking após restart
        await self.recover_tracking_messages()

    async def recover_tracking_messages(self):
        """Recupera mensagens de tracking existentes após restart"""
        try:
            if not self.voice_tracking_messages:
                return
                
            logger.info(f"🔄 Tentando recuperar {len(self.voice_tracking_messages)} mensagens de tracking...")
            
            for channel_id, msg_data in list(self.voice_tracking_messages.items()):
                try:
                    channel = self.bot.get_channel(channel_id)
                    if not channel:
                        logger.warning(f"Canal {channel_id} não encontrado, removendo do tracking")
                        del self.voice_tracking_messages[channel_id]
                        continue
                    
                    if "message_id" not in msg_data:
                        logger.warning(f"ID de mensagem não encontrado para canal {channel_id}")
                        del self.voice_tracking_messages[channel_id]
                        continue
                    
                    # Tentar buscar a mensagem
                    try:
                        message = await channel.fetch_message(msg_data["message_id"])
                        
                        # Restaurar referência da mensagem em memória
                        self.voice_status_messages[channel_id] = {
                            "message": message,
                            "last_update": datetime.now(timezone.utc)
                        }
                        
                        logger.info(f"✅ Mensagem de tracking recuperada no canal {channel.name}")
                        
                    except discord.NotFound:
                        logger.info(f"⚠️ Mensagem de tracking não encontrada no canal {channel.name}, será criada nova")
                        del self.voice_tracking_messages[channel_id]
                    except Exception as e:
                        logger.error(f"Erro ao recuperar mensagem do canal {channel.name}: {e}")
                        del self.voice_tracking_messages[channel_id]
                        
                except Exception as e:
                    logger.error(f"Erro geral ao processar canal {channel_id}: {e}")
                    
            logger.info(f"🔄 Recuperação concluída. {len(self.voice_status_messages)} mensagens ativas")
            
        except Exception as e:
            logger.error(f"Erro na recuperação de mensagens de tracking: {e}")

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
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            
            # Lista de arquivos para backup
            backup_files = [
                (self.data_file, f"economy_backup_{timestamp}.json"),
                (self.voice_tracking_file, f"voice_tracking_backup_{timestamp}.json"),
                ("data/panel_data.json", f"panel_data_backup_{timestamp}.json"),
                ("data/lottery_data.json", f"lottery_data_backup_{timestamp}.json"),
                ("data/lottery_history.json", f"lottery_history_backup_{timestamp}.json"),
            ]
            
            backup_count = 0
            for source_file, backup_name in backup_files:
                if os.path.exists(source_file):
                    backup_file = os.path.join(self.backup_dir, backup_name)
                    shutil.copy2(source_file, backup_file)
                    backup_count += 1

            # Manter apenas os últimos 10 backups de cada tipo
            backup_types = ["economy_backup_", "voice_tracking_backup_", "panel_data_backup_", 
                           "lottery_data_backup_", "lottery_history_backup_"]
            
            for backup_type in backup_types:
                backups = sorted([
                    f for f in os.listdir(self.backup_dir) 
                    if f.startswith(backup_type) and f.endswith('.json')
                ])
                while len(backups) > 10:
                    oldest = backups.pop(0)
                    os.remove(os.path.join(self.backup_dir, oldest))

            logger.info(f"Backup automático criado: {backup_count} arquivos salvos (timestamp: {timestamp})")

        except Exception as e:
            logger.error(f"Erro ao criar backup automático: {e}")

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

                # Calcular total de moedas ganhas nesta sessão
                total_periods_completed = int(total_minutes) // self.min_voice_time_for_reward
                coins_per_period = self.ac_per_hour / (60 / self.min_voice_time_for_reward)
                total_coins_earned = int(total_periods_completed * coins_per_period)

                # Dar recompensa final se houver tempo não recompensado (usar configuração)
                if minutes_since_reward >= self.min_voice_time_for_reward:
                    # Aplicar a mesma lógica configurável
                    complete_minutes = int(minutes_since_reward)
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

                # Salvar dados após mudança
                self.save_voice_tracking_data()
                
                # Enviar resumo por DM se configurado
                if self.send_voice_summary_dm:
                    await self.send_voice_summary_dm_to_user(member, total_minutes, total_coins_earned)

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
            
            # Salvar dados após mudança
            self.save_voice_tracking_data()
            
            logger.info(f"Usuário {user_id} entrou na call no canal {after_channel.id}")

    async def on_message(self, message: discord.Message):
        """Processa mensagens para recompensas"""
        if not self.message_reward_enabled:
            return
            
        # Ignorar bots e comandos
        if message.author.bot or message.content.startswith('!'):
            return
            
        user_id = message.author.id
        current_time = datetime.now(timezone.utc)
        
        # Verificar se usuário está em cooldown
        if user_id in self.message_tracking:
            last_reward = self.message_tracking[user_id].get('last_reward')
            if last_reward:
                time_diff = (current_time - last_reward).total_seconds() / 60
                if time_diff < self.message_reward_cooldown:
                    # Ainda em cooldown, apenas incrementar contador
                    self.message_tracking[user_id]['count'] += 1
                    return
        
        # Inicializar tracking se não existir
        if user_id not in self.message_tracking:
            self.message_tracking[user_id] = {'count': 0, 'last_reward': None}
        
        # Incrementar contador
        self.message_tracking[user_id]['count'] += 1
        
        # Verificar se atingiu o limite para recompensa
        if self.message_tracking[user_id]['count'] >= self.messages_for_reward:
            import random
            
            # Calcular recompensa aleatória
            reward = random.randint(self.message_reward_min, self.message_reward_max)
            
            # Dar recompensa
            self.add_coins(user_id, reward, f"Recompensa por {self.message_tracking[user_id]['count']} mensagens")
            
            # Resetar contador e atualizar último prêmio
            self.message_tracking[user_id]['count'] = 0
            self.message_tracking[user_id]['last_reward'] = current_time
            
            # Enviar mensagem no mesmo canal
            try:
                embed = discord.Embed(
                    title="💬 Recompensa por Atividade",
                    description=f"🎉 {message.author.mention} ganhou **{reward} AC** por participar ativamente do chat!",
                    color=discord.Color.gold()
                )
                await message.channel.send(embed=embed)
                
                logger.info(f"Usuário {user_id} recebeu {reward} AC por {self.messages_for_reward} mensagens")
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem de recompensa: {e}")

    async def send_voice_summary_dm_to_user(self, member: discord.Member, total_minutes: float, total_coins: int):
        """Envia resumo da sessão de voz por DM"""
        try:
            # Formatar tempo
            hours = int(total_minutes // 60)
            minutes = int(total_minutes % 60)
            
            if hours > 0:
                time_str = f"{hours}h {minutes}m"
            else:
                time_str = f"{minutes}m"
            
            embed = discord.Embed(
                title="🎤 Resumo da Sessão de Voz",
                description=f"Olá **{member.display_name}**! Aqui está o resumo da sua participação na call:",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.add_field(
                name="⏱️ Tempo Total",
                value=time_str,
                inline=True
            )
            
            embed.add_field(
                name="💰 AC Ganhos",
                value=f"{total_coins} AC",
                inline=True
            )
            
            # Saldo atual
            current_balance = self.get_balance(member.id)
            embed.add_field(
                name="💳 Saldo Atual",
                value=f"{current_balance} AC",
                inline=True
            )
            
            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            embed.set_footer(text="ARCA Organization - Obrigado por participar!")
            
            await member.send(embed=embed)
            logger.info(f"Resumo de voz enviado por DM para {member.display_name} ({member.id})")
            
        except discord.Forbidden:
            logger.info(f"Não foi possível enviar DM para {member.display_name} (DMs fechadas)")
        except Exception as e:
            logger.error(f"Erro ao enviar DM para {member.display_name}: {e}")

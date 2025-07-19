#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Sorteios d        # Determinar cor e ícones baseado no status
        if lottery_data.get('winner'):
                         # Criar embed atualizado para admin com título mais destacado
                lottery_name = lottery_data['name']

                # Determinar status e cor do embed admin
                if lottery_data.get('winner'):
                    admin_color = discord.Color.green()
                    status_icon = "🏆"
                    status_text = "FINALIZADO"
                elif lottery_data.get('cancelled'):
                    admin_color = discord.Color.red()
                    status_icon = "❌"
                    status_text = "CANCELADO"
                else:
                    admin_color = discord.Color.orange()
                    status_icon = "🎲"
                    status_text = "ATIVO"

                admin_embed = discord.Embed(
                    title=f"🛠️ **PAINEL ADMINISTRATIVO** 🛠️",
                    description=(
                        f"## 🎯 **{lottery_name.upper()}** 🎯\n"
                        f"**Status:** `{status_text}` {status_icon}\n\n"
                        f"*{'🎉 Sorteio finalizado!' if lottery_data.get('winner') else '⚡ Controle total do sorteio - Use os botões abaixo'}*"
                    ),
                    color=admin_color
                )e_icon = "🏆"
            color = discord.Color.green()
            status_text = "FINALIZADO"
        elif lottery_data.get('cancelled'):
            title_icon = "❌"
            color = discord.Color.red()
            status_text = "CANCELADO"
        else:
            title_icon = "🎲"
            color = discord.Color.gold()
            status_text = "ATIVO"

        embed = discord.Embed(
            title=f"{title_icon} **SORTEIO ARCA** {title_icon}",
            description=(
                f"# 🎊 **{lottery_name.upper()}** 🎊\n\n"
                f"**Status:** `{status_text}`\n"
                f"*{'🎉 Parabéns ao vencedor!' if lottery_data.get('winner') else '✨ Participe agora e concorra a este prêmio incrível! ✨'}*"
            ),
            color=color
        )A Bot

Gerencia criação, participação e sorteio de eventos com
sistema de tickets escaláveis usando Arca Coins.

Autor: ARCA Organization
Licença: MIT
"""

import asyncio
import json
import os
import random
from datetime import datetime, timezone
from typing import Dict
import discord
import logging

logger = logging.getLogger("ARCA-Bot")


async def robust_discord_operation(
    operation,
    operation_name: str,
    config=None,
    max_retries: int = None,
    delay: float = None,
):
    """
    Executa uma operação do Discord com retry automático para problemas de conectividade

    Args:
        operation: Função assíncrona a ser executada
        operation_name: Nome da operação para logging
        config: Configuração de conectividade (ConnectivityConfig)
        max_retries: Número máximo de tentativas (sobrescreve config)
        delay: Delay entre tentativas em segundos (sobrescreve config)

    Returns:
        Tuple[bool, Any]: (sucesso, resultado)
    """
    # Usar configuração padrão se não fornecida
    if config:
        retries = max_retries if max_retries is not None else config.max_retries
        retry_delay = delay if delay is not None else config.retry_delay
        handle_503 = config.handle_503_errors
    else:
        retries = max_retries if max_retries is not None else 3
        retry_delay = delay if delay is not None else 2.0
        handle_503 = True

    for attempt in range(retries):
        try:
            result = await operation()
            return True, result
        except discord.HTTPException as e:
            if e.status == 503 and handle_503:  # Service Unavailable
                logger.warning(
                    f"{operation_name}: Tentativa {attempt + 1}/{retries} falhou (503 Service Unavailable)"
                )
                if attempt < retries - 1:  # Não esperar na última tentativa
                    await asyncio.sleep(retry_delay)
                continue
            else:
                logger.error(f"{operation_name}: Erro HTTP {e.status}: {e}")
                return False, None
        except Exception as e:
            logger.error(f"{operation_name}: Erro inesperado: {e}")
            return False, None

    logger.error(f"{operation_name}: Falhou após {retries} tentativas")
    return False, None


async def safe_interaction_response(
    interaction: discord.Interaction,
    content: str = None,
    embed: discord.Embed = None,
    ephemeral: bool = True,
    view: discord.ui.View = None,
):
    """
    Responde a uma interação de forma segura, lidando com interações expiradas

    Args:
        interaction: A interação do Discord
        content: Conteúdo da mensagem
        embed: Embed da mensagem
        ephemeral: Se a resposta deve ser efêmera
        view: View com botões/componentes

    Returns:
        bool: True se conseguiu responder, False caso contrário
    """
    try:
        # Verificar se a interação e response existem
        if (
            not interaction
            or not hasattr(interaction, "response")
            or interaction.response is None
        ):
            logger.warning("Interação inválida ou response não disponível")
            return False

        # Verificar se a interação já foi respondida
        if interaction.response.is_done():
            # Usar followup se já foi respondida
            await interaction.followup.send(
                content=content, embed=embed, ephemeral=ephemeral, view=view
            )
            return True
        else:
            # Usar response normal
            await interaction.response.send_message(
                content=content, embed=embed, ephemeral=ephemeral, view=view
            )
            return True

    except discord.InteractionResponded:
        # Interação já foi respondida, tentar followup
        try:
            await interaction.followup.send(
                content=content, embed=embed, ephemeral=ephemeral, view=view
            )
            return True
        except Exception as e:
            logger.error(f"Erro no followup da interação: {e}")
            return False

    except discord.NotFound:
        # Interação expirada (15+ minutos)
        logger.warning("Interação expirada (Unknown interaction)")
        return False

    except discord.HTTPException as e:
        if e.status == 404 and "Unknown interaction" in str(e):
            logger.warning("Interação desconhecida (provavelmente expirada)")
            return False
        else:
            logger.error(f"Erro HTTP na interação: {e}")
            return False

    except AttributeError as e:
        # Erro de atributo (como is_finished vs is_done)
        logger.error(f"Erro de atributo na interação: {e}")
        return False

    except Exception as e:
        logger.error(f"Erro inesperado na interação: {e}")
        return False


class LotterySystem:
    """Sistema de sorteios do bot ARCA"""

    def __init__(self, bot, economy_system):
        self.bot = bot
        self.economy = economy_system
        self.data_file = os.path.join("data", "lottery_data.json")
        self.config = bot.config.lottery  # Usar configuração centralizada

        # Dados em memória
        self.active_lotteries = {}  # {message_id: lottery_data}
        self.admin_panels = {}  # {lottery_id: {'message': Message, 'user_id': int}}

        # Carregar dados
        self.load_data()

    def load_data(self):
        """Carrega dados dos sorteios ativos"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.active_lotteries = json.load(f)
                logger.info(
                    f"Dados de sorteio carregados: {len(self.active_lotteries)} sorteios ativos"
                )
            else:
                self.active_lotteries = {}
                logger.info("Arquivo de sorteio não encontrado, criando novo")
        except Exception as e:
            logger.error(f"Erro ao carregar dados de sorteio: {e}")
            self.active_lotteries = {}

    def save_data(self):
        """Salva dados dos sorteios"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.active_lotteries, f, indent=2, ensure_ascii=False)
            logger.debug("Dados de sorteio salvos")
        except Exception as e:
            logger.error(f"Erro ao salvar dados de sorteio: {e}")

    def has_admin_role(self, member: discord.Member) -> bool:
        """Verifica se o membro pode criar sorteios"""
        return any(role.name == self.config.admin_role_name for role in member.roles)

    def calculate_next_ticket_price(
        self, base_price: int, user_tickets_count: int
    ) -> int:
        """Calcula o preço do próximo ticket para um usuário específico: 1.1^(qty) * base_price"""
        return int(base_price * (1.1**user_tickets_count))

    def create_lottery_embed(self, lottery_data: Dict) -> discord.Embed:
        """Cria embed para o sorteio"""
        # Criar título mais chamativo
        lottery_name = lottery_data["name"]

        embed = discord.Embed(
            title="� **SORTEIO ARCA** 🎉",
            description=f"# 🏆 **{lottery_name.upper()}**\n\n*Participe agora e concorra a este prêmio incrível!*",
            color=discord.Color.gold(),
        )

        # Informações básicas em linha
        embed.add_field(
            name="👥 Participantes",
            value=f"**{len(lottery_data['participants'])}**",
            inline=True,
        )

        # Mostrar preço do próximo ticket (baseado no primeiro ticket do usuário)
        next_ticket_price = self.calculate_next_ticket_price(
            lottery_data["base_price"], 0
        )
        embed.add_field(
            name="💰 Preço Inicial", value=f"**{next_ticket_price} AC**", inline=True
        )

        embed.add_field(
            name="📅 Criado",
            value=f"<t:{int(lottery_data['created_at'])}:R>",
            inline=True,
        )

        # Informações do vencedor (se houver)
        if lottery_data.get("winner"):
            winner_user_id = lottery_data["winner"]["user_id"]
            embed.add_field(
                name="� **GRANDE VENCEDOR** 🎊",
                value=(
                    f"🏆 <@{winner_user_id}>\n"
                    f"🎯 **Parabéns pelo prêmio conquistado!**"
                ),
                inline=False,
            )

        # Informação de cancelamento
        if lottery_data.get("cancelled"):
            embed.add_field(
                name="⚠️ Sorteio Cancelado",
                value="Este sorteio foi cancelado e os valores foram reembolsados automaticamente.",
                inline=False,
            )

        # Footer personalizado
        embed.set_footer(
            text="🎮 ARCA Organization | Star Citizen | Boa sorte a todos!"
        )

        return embed

    def create_lottery_view(self, lottery_id: str, lottery_data: Dict):
        """Cria view com botões para o sorteio (apenas Comprar e Cancelar)"""
        return LotteryView(self, lottery_id, lottery_data)

    def create_admin_panel_view(self, lottery_id: str, lottery_data: Dict):
        """Cria view administrativa com botão de sortear"""
        return AdminLotteryView(self, lottery_id, lottery_data)

    def register_admin_panel(
        self, lottery_id: str, message: discord.Message, user_id: int
    ):
        """Registra uma mensagem de painel admin para atualizações"""
        self.admin_panels[lottery_id] = {"message": message, "user_id": user_id}
        logger.info(
            f"Painel admin registrado para sorteio {lottery_id} (usuário {user_id})"
        )

    async def update_admin_panel(self, lottery_id: str, lottery_data: Dict):
        """Atualiza o painel administrativo se existir"""
        logger.info(f"Tentando atualizar painel admin para sorteio {lottery_id}")

        if lottery_id in self.admin_panels:
            logger.info(f"Painel admin encontrado para sorteio {lottery_id}")
            try:
                panel_data = self.admin_panels[lottery_id]
                message = panel_data["message"]

                # Criar embed atualizado para admin com título mais destacado
                lottery_name = lottery_data["name"]
                admin_embed = discord.Embed(
                    title="�️ **PAINEL ADMINISTRATIVO** 🛠️",
                    description=f"## 🎯 **{lottery_name.upper()}**\n\n*Controle total do sorteio - Use os botões abaixo*",
                    color=discord.Color.orange(),
                )

                total_tickets = sum(
                    len(tickets) for tickets in lottery_data["participants"].values()
                )
                total_value = sum(
                    sum(ticket["price"] for ticket in tickets)
                    for tickets in lottery_data["participants"].values()
                )

                admin_embed.add_field(
                    name="🎫 Total de Tickets",
                    value=f"**{total_tickets}**",
                    inline=True,
                )

                admin_embed.add_field(
                    name="👥 Participantes",
                    value=f"**{len(lottery_data['participants'])}**",
                    inline=True,
                )

                admin_embed.add_field(
                    name="💰 Total Arrecadado",
                    value=f"**{total_value} AC**",
                    inline=True,
                )

                admin_embed.add_field(
                    name="💰 Valor Base",
                    value=f"**{lottery_data['base_price']} AC**",
                    inline=True,
                )

                # Lista de participantes com tickets (sem mostrar valores individuais)
                if lottery_data["participants"]:
                    participants_list = []
                    for user_id, tickets in lottery_data["participants"].items():
                        try:
                            user = self.bot.get_user(int(user_id))
                            user_name = (
                                user.display_name if user else f"Usuário {user_id}"
                            )
                        except Exception:
                            user_name = f"Usuário {user_id}"

                        ticket_count = len(tickets)
                        participants_list.append(
                            f"🎫 **{user_name}**: {ticket_count} ticket(s)"
                        )

                    # Limitar a 10 participantes para não estourar o limite do embed
                    if len(participants_list) > 10:
                        shown_participants = participants_list[:10]
                        shown_participants.append(
                            f"... e mais {len(participants_list) - 10} participante(s)"
                        )
                    else:
                        shown_participants = participants_list

                    admin_embed.add_field(
                        name="📋 Participantes do Sorteio",
                        value="\n".join(shown_participants),
                        inline=False,
                    )
                else:
                    admin_embed.add_field(
                        name="📋 Participantes do Sorteio",
                        value="*Aguardando participantes...*",
                        inline=False,
                    )

                # Criar nova view admin
                admin_view = AdminLotteryView(self, lottery_id, lottery_data)

                # Atualizar mensagem com retry
                edit_success, _ = await robust_discord_operation(
                    lambda: message.edit(embed=admin_embed, view=admin_view),
                    f"Atualização do painel admin para sorteio {lottery_id}",
                    self.bot.config.connectivity,
                )

                if edit_success:
                    logger.info(
                        f"Painel admin atualizado com sucesso para sorteio {lottery_id}"
                    )
                else:
                    logger.warning(
                        f"Falha ao atualizar painel admin para sorteio {lottery_id}"
                    )

            except (discord.NotFound, discord.HTTPException):
                # Mensagem foi deletada, remover do tracking
                logger.warning(
                    f"Mensagem do painel admin não encontrada, removendo do tracking: {lottery_id}"
                )
                del self.admin_panels[lottery_id]
            except Exception as e:
                logger.error(f"Erro geral ao atualizar painel admin: {e}")
        else:
            logger.info(f"Nenhum painel admin registrado para sorteio {lottery_id}")


class LotteryView(discord.ui.View):
    """View com botões para interação com sorteio (apenas Comprar e Cancelar)"""

    def __init__(self, lottery_system, lottery_id: str, lottery_data: Dict):
        super().__init__(timeout=None)
        self.lottery_system = lottery_system
        self.lottery_id = lottery_id
        self.lottery_data = lottery_data

    @discord.ui.button(label="🎫 Comprar", style=discord.ButtonStyle.primary)
    async def buy_ticket(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Compra um ticket"""
        try:
            user_id = str(interaction.user.id)

            # Verificar se já foi sorteado
            if self.lottery_data.get("winner") or self.lottery_data.get("cancelled"):
                response_success = await safe_interaction_response(
                    interaction, "❌ Este sorteio já foi finalizado!", ephemeral=True
                )
                if not response_success:
                    logger.warning(
                        f"Não foi possível responder à interação de sorteio finalizado do usuário {interaction.user.id}"
                    )
                return

            # Calcular preço do ticket baseado na quantidade individual do usuário
            user_tickets_count = len(self.lottery_data["participants"].get(user_id, []))
            ticket_price = self.lottery_system.calculate_next_ticket_price(
                self.lottery_data["base_price"], user_tickets_count
            )

            # Verificar saldo
            user_balance = self.lottery_system.economy.get_balance(interaction.user.id)
            if user_balance < ticket_price:
                response_success = await safe_interaction_response(
                    interaction,
                    f"❌ Saldo insuficiente! Você tem {user_balance} AC, mas precisa de {ticket_price} AC.",
                    ephemeral=True,
                )
                if not response_success:
                    logger.warning(
                        f"Não foi possível responder à interação de saldo insuficiente do usuário {interaction.user.id}"
                    )
                return

            # Debitar moedas
            if not self.lottery_system.economy.remove_coins(
                interaction.user.id, ticket_price
            ):
                response_success = await safe_interaction_response(
                    interaction, "❌ Erro ao debitar moedas!", ephemeral=True
                )
                if not response_success:
                    logger.warning(
                        f"Não foi possível responder à interação de erro ao debitar do usuário {interaction.user.id}"
                    )
                return

            # Adicionar ticket
            if user_id not in self.lottery_data["participants"]:
                self.lottery_data["participants"][user_id] = []

            ticket_number = len(self.lottery_data["participants"][user_id]) + 1
            self.lottery_data["participants"][user_id].append(
                {
                    "number": ticket_number,
                    "price": ticket_price,
                    "bought_at": datetime.now(timezone.utc).timestamp(),
                }
            )

            # Salvar preço do ticket
            if "ticket_prices" not in self.lottery_data:
                self.lottery_data["ticket_prices"] = []
            self.lottery_data["ticket_prices"].append(ticket_price)

            # Salvar dados
            self.lottery_system.active_lotteries[self.lottery_id] = self.lottery_data
            self.lottery_system.save_data()

            # Calcular próximo preço para este usuário
            next_price = self.lottery_system.calculate_next_ticket_price(
                self.lottery_data["base_price"], user_tickets_count + 1
            )

            # Atualizar embed público da mensagem principal
            embed = self.lottery_system.create_lottery_embed(self.lottery_data)

            # Enviar confirmação privada primeiro
            response_success = await safe_interaction_response(
                interaction,
                f"✅ **Ticket #{ticket_number} comprado com sucesso!**\n"
                f"💰 Valor pago: {ticket_price} AC\n"
                f"💸 Seu próximo ticket custará: {next_price} AC\n"
                f"💳 Saldo restante: {user_balance - ticket_price} AC",
                ephemeral=True,
            )

            if not response_success:
                logger.warning(
                    f"Não foi possível responder à confirmação de compra de ticket do usuário {interaction.user.id}"
                )
                # Continuar mesmo assim, pois a compra já foi processada

            # Buscar e editar a mensagem original do sorteio com retry
            try:
                # A mensagem original é a que contém esta view
                original_message = interaction.message

                # Operação robusta de edição
                edit_success, _ = await robust_discord_operation(
                    lambda: original_message.edit(embed=embed, view=self),
                    f"Edição da mensagem do sorteio {self.lottery_id} após compra de ticket",
                    self.lottery_system.bot.config.connectivity,
                )

                if not edit_success:
                    logger.warning(
                        f"Falha ao atualizar mensagem do sorteio {self.lottery_id}, mas ticket foi processado"
                    )

                # Atualizar painel admin se existir
                logger.info(
                    f"Chamando update_admin_panel para sorteio {self.lottery_id}"
                )
                await self.lottery_system.update_admin_panel(
                    self.lottery_id, self.lottery_data
                )

            except Exception as e:
                logger.error(f"Erro geral ao atualizar mensagem do sorteio: {e}")
                # Se não conseguir editar, pelo menos loggar o erro

        except Exception as e:
            logger.error(f"Erro ao comprar ticket: {e}")
            # Tentar responder com erro usando função segura
            response_success = await safe_interaction_response(
                interaction, "❌ Erro interno ao comprar ticket!", ephemeral=True
            )
            if not response_success:
                logger.error(
                    f"Não foi possível responder ao erro de compra de ticket para o usuário {interaction.user.id}"
                )


class AdminLotteryView(discord.ui.View):
    """View administrativa com botões de sortear e cancelar"""

    def __init__(self, lottery_system, lottery_id: str, lottery_data: Dict):
        super().__init__(timeout=None)
        self.lottery_system = lottery_system
        self.lottery_id = lottery_id
        self.lottery_data = lottery_data

    @discord.ui.button(label="🎲 Sortear", style=discord.ButtonStyle.success)
    async def draw_lottery(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Sorteia o vencedor"""
        try:
            # Verificar se é o criador ou admin
            if interaction.user.id != self.lottery_data[
                "creator_id"
            ] and not self.lottery_system.has_admin_role(interaction.user):

                # Buscar o nome do criador para uma mensagem mais amigável
                try:
                    creator = interaction.guild.get_member(
                        self.lottery_data["creator_id"]
                    )
                    creator_name = creator.display_name if creator else "criador"
                except Exception:
                    creator_name = "criador"

                await interaction.response.send_message(
                    f"🔒 **Acesso Negado**\n\n"
                    f"Apenas o {creator_name} do sorteio ou administradores com o cargo `{self.lottery_system.admin_role_name}` podem sortear!\n\n"
                    f"💡 Se você é o criador, verifique suas mensagens privadas para o painel administrativo.",
                    ephemeral=True,
                )
                return

            # Verificar se há participantes
            if not self.lottery_data["participants"]:
                await interaction.response.send_message(
                    "❌ Não há participantes no sorteio!", ephemeral=True
                )
                return

            # Verificar se já foi sorteado
            if self.lottery_data.get("winner"):
                await interaction.response.send_message(
                    "❌ Este sorteio já foi realizado!", ephemeral=True
                )
                return

            # Buscar a mensagem original do sorteio
            try:
                # Verificar se temos o channel_id e public_message_id salvos nos dados do sorteio
                if (
                    "channel_id" not in self.lottery_data
                    or "public_message_id" not in self.lottery_data
                ):
                    await interaction.response.send_message(
                        "❌ Informações do canal ou mensagem do sorteio não encontradas!",
                        ephemeral=True,
                    )
                    return

                # Buscar o canal através do bot
                channel = self.lottery_system.bot.get_channel(
                    self.lottery_data["channel_id"]
                )
                if not channel:
                    await interaction.response.send_message(
                        "❌ Canal do sorteio não encontrado!", ephemeral=True
                    )
                    return

                # Buscar a mensagem original usando o public_message_id
                original_message = await channel.fetch_message(
                    self.lottery_data["public_message_id"]
                )
            except Exception as e:
                logger.error(f"Erro ao buscar mensagem original: {e}")
                await interaction.response.send_message(
                    "❌ Não foi possível encontrar a mensagem original do sorteio!",
                    ephemeral=True,
                )
                return

            # Criar lista de tickets
            all_tickets = []
            for user_id, tickets in self.lottery_data["participants"].items():
                all_tickets.extend([user_id] * len(tickets))

            # Sortear
            winner_id = random.choice(all_tickets)
            winner_tickets = len(self.lottery_data["participants"][winner_id])

            # Salvar vencedor
            self.lottery_data["winner"] = {
                "user_id": winner_id,
                "tickets": winner_tickets,
                "drawn_at": datetime.now(timezone.utc).timestamp(),
            }

            # Atualizar dados
            self.lottery_system.active_lotteries[self.lottery_id] = self.lottery_data
            self.lottery_system.save_data()

            # Criar embed atualizado
            embed = self.lottery_system.create_lottery_embed(self.lottery_data)

            # Tentar adicionar foto do vencedor
            try:
                winner_user = interaction.guild.get_member(int(winner_id))
                if winner_user and winner_user.avatar:
                    embed.set_thumbnail(url=winner_user.avatar.url)
            except Exception:
                pass

            # Atualizar mensagem original do sorteio (desabilitar botões) com retry
            disabled_view = LotteryView(
                self.lottery_system, self.lottery_id, self.lottery_data
            )
            for item in disabled_view.children:
                item.disabled = True

            # Tentar atualizar a mensagem com retry para problemas de conectividade
            update_success = False
            for attempt in range(3):  # Máximo 3 tentativas
                try:
                    await original_message.edit(embed=embed, view=disabled_view)
                    update_success = True
                    break
                except discord.HTTPException as e:
                    if e.status == 503:  # Service Unavailable
                        logger.warning(
                            f"Tentativa {attempt + 1}/3 falhou ao atualizar sorteio (503 Service Unavailable). Tentando novamente em 2 segundos..."
                        )
                        if attempt < 2:  # Não esperar na última tentativa
                            await asyncio.sleep(2)
                        continue
                    else:
                        logger.error(f"Erro HTTP ao atualizar mensagem do sorteio: {e}")
                        break
                except Exception as e:
                    logger.error(
                        f"Erro inesperado ao atualizar mensagem do sorteio: {e}"
                    )
                    break

            # Mention público do vencedor no canal original com embed especial
            try:
                # Criar embed especial para o anúncio do vencedor
                winner_embed = discord.Embed(
                    title="🎊 **VENCEDOR DO SORTEIO!** 🎊",
                    description=(
                        f"# 🏆 **{self.lottery_data['name'].upper()}** 🏆\n\n"
                        f"🎉 **PARABÉNS** <@{winner_id}>! 🎉\n"
                        f"✨ *Você conquistou este prêmio incrível!* ✨"
                    ),
                    color=discord.Color.gold(),
                )

                # Adicionar imagem de perfil do vencedor
                try:
                    logger.info(f"🔍 Buscando usuário vencedor: {winner_id}")
                    # Primeiro tentar pelo guild da interaction
                    winner_user = None
                    if interaction.guild:
                        winner_user = interaction.guild.get_member(int(winner_id))

                    # Se não encontrou, tentar pelo bot usando o channel_id
                    if not winner_user:
                        logger.info("� Tentando buscar através do canal do sorteio...")
                        channel = self.lottery_system.bot.get_channel(
                            self.lottery_data["channel_id"]
                        )
                        if channel and channel.guild:
                            winner_user = channel.guild.get_member(int(winner_id))

                    if winner_user:
                        logger.info(
                            f"✅ Usuário encontrado: {winner_user.display_name}"
                        )
                        if winner_user.avatar:
                            logger.info(
                                f"📸 Avatar encontrado: {winner_user.avatar.url}"
                            )
                            winner_embed.set_image(url=winner_user.avatar.url)
                            winner_embed.set_author(
                                name=f"🎯 {winner_user.display_name}",
                                icon_url=winner_user.avatar.url,
                            )
                        else:
                            logger.warning(
                                f"⚠️ Usuário {winner_user.display_name} não tem avatar"
                            )
                            winner_embed.set_author(
                                name=f"🎯 {winner_user.display_name}"
                            )
                    else:
                        logger.warning(
                            f"❌ Usuário {winner_id} não encontrado no servidor"
                        )
                        winner_embed.set_author(name=f"🎯 Vencedor: {winner_id}")
                except Exception as e:
                    logger.error(f"❌ Erro ao buscar avatar do vencedor: {e}")
                    winner_embed.set_author(name="🎯 Vencedor")

                winner_embed.add_field(
                    name="📊 Estatísticas do Sorteio",
                    value=(
                        f"👥 **{len(self.lottery_data['participants'])}** participantes\n"
                        f"🎫 **{sum(len(tickets) for tickets in self.lottery_data['participants'].values())}** tickets totais"
                    ),
                    inline=False,
                )

                winner_embed.set_footer(
                    text="🎮 ARCA Organization | Parabéns ao vencedor!"
                )

                # Tentar enviar anúncio do vencedor com retry
                announcement_success = False
                for attempt in range(3):  # Máximo 3 tentativas
                    try:
                        await channel.send(
                            content=f"🎉 <@{winner_id}> 🎉", embed=winner_embed
                        )
                        announcement_success = True
                        break
                    except discord.HTTPException as e:
                        if e.status == 503:  # Service Unavailable
                            logger.warning(
                                f"Tentativa {attempt + 1}/3 falhou ao enviar anúncio (503 Service Unavailable). Tentando novamente em 2 segundos..."
                            )
                            if attempt < 2:  # Não esperar na última tentativa
                                await asyncio.sleep(2)
                            continue
                        else:
                            logger.error(
                                f"Erro HTTP ao enviar anúncio do vencedor: {e}"
                            )
                            break
                    except Exception as e:
                        logger.error(
                            f"Erro inesperado ao enviar anúncio do vencedor: {e}"
                        )
                        break

                # Se não conseguiu enviar o embed, tenta mensagem simples
                if not announcement_success:
                    try:
                        await channel.send(
                            f"🎉 Parabéns <@{winner_id}>! Você ganhou o sorteio **{self.lottery_data['name']}**!"
                        )
                        announcement_success = True
                    except Exception as e:
                        logger.error(f"Erro ao enviar anúncio simples: {e}")
            except Exception as e:
                logger.error(f"Erro geral no anúncio do vencedor: {e}")
                announcement_success = False

            # Responder no painel admin com base no sucesso das operações
            response_message = f"🎉 **Sorteio realizado com sucesso!**\n\n🏆 **Vencedor:** <@{winner_id}>\n📊 **Total de participantes:** {len(self.lottery_data['participants'])}\n"

            if update_success and announcement_success:
                response_message += (
                    "✅ **Todas as operações foram concluídas com sucesso!**"
                )
            elif update_success:
                response_message += "⚠️ **Atenção:** Mensagem atualizada, mas houve problemas no anúncio público."
            elif announcement_success:
                response_message += "⚠️ **Atenção:** Anúncio enviado, mas houve problemas na atualização da mensagem."
            else:
                response_message += "❌ **Atenção:** Problemas de conectividade afetaram as atualizações visuais.\n💾 **O sorteio foi processado corretamente nos dados.**"

            await interaction.response.send_message(response_message, ephemeral=True)

        except Exception as e:
            logger.error(f"Erro ao sortear: {e}")
            await interaction.response.send_message(
                "❌ Erro interno ao realizar sorteio!", ephemeral=True
            )

    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.danger)
    async def cancel_lottery_admin(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Cancela o sorteio (versão admin)"""
        try:
            # Verificar se é o criador ou admin
            if interaction.user.id != self.lottery_data[
                "creator_id"
            ] and not self.lottery_system.has_admin_role(interaction.user):

                # Buscar o nome do criador para uma mensagem mais amigável
                try:
                    creator = interaction.guild.get_member(
                        self.lottery_data["creator_id"]
                    )
                    creator_name = creator.display_name if creator else "criador"
                except Exception:
                    creator_name = "criador"

                response_success = await safe_interaction_response(
                    interaction,
                    f"🔒 **Acesso Negado**\n\n"
                    f"Apenas o {creator_name} do sorteio ou administradores com o cargo `{self.lottery_system.admin_role_name}` podem cancelar!\n\n"
                    f"💡 Se você é o criador, verifique suas mensagens privadas para o painel administrativo.",
                    ephemeral=True,
                )
                if not response_success:
                    logger.warning(
                        f"Não foi possível responder à interação de acesso negado do usuário {interaction.user.id}"
                    )
                return

            # Verificar se já foi sorteado
            if self.lottery_data.get("winner"):
                response_success = await safe_interaction_response(
                    interaction,
                    "❌ Não é possível cancelar um sorteio já realizado!",
                    ephemeral=True,
                )
                if not response_success:
                    logger.warning(
                        f"Não foi possível responder à interação de sorteio já realizado do usuário {interaction.user.id}"
                    )
                return

            # Verificar se já foi cancelado
            if self.lottery_data.get("cancelled"):
                response_success = await safe_interaction_response(
                    interaction, "❌ Este sorteio já foi cancelado!", ephemeral=True
                )
                if not response_success:
                    logger.warning(
                        f"Não foi possível responder à interação de sorteio já cancelado do usuário {interaction.user.id}"
                    )
                return

            # Buscar a mensagem original do sorteio
            try:
                # Verificar se temos o channel_id e public_message_id salvos nos dados do sorteio
                if (
                    "channel_id" not in self.lottery_data
                    or "public_message_id" not in self.lottery_data
                ):
                    response_success = await safe_interaction_response(
                        interaction,
                        "❌ Informações do canal ou mensagem do sorteio não encontradas!",
                        ephemeral=True,
                    )
                    if not response_success:
                        logger.warning(
                            f"Não foi possível responder à interação de dados não encontrados do usuário {interaction.user.id}"
                        )
                    return

                # Buscar o canal através do bot
                channel = self.lottery_system.bot.get_channel(
                    self.lottery_data["channel_id"]
                )
                if not channel:
                    response_success = await safe_interaction_response(
                        interaction,
                        "❌ Canal do sorteio não encontrado!",
                        ephemeral=True,
                    )
                    if not response_success:
                        logger.warning(
                            f"Não foi possível responder à interação de canal não encontrado do usuário {interaction.user.id}"
                        )
                    return

                # Buscar a mensagem original usando o public_message_id
                original_message = await channel.fetch_message(
                    self.lottery_data["public_message_id"]
                )
            except Exception as e:
                logger.error(f"Erro ao buscar mensagem original: {e}")
                response_success = await safe_interaction_response(
                    interaction,
                    "❌ Não foi possível encontrar a mensagem original do sorteio!",
                    ephemeral=True,
                )
                if not response_success:
                    logger.warning(
                        f"Não foi possível responder à interação de erro ao buscar mensagem do usuário {interaction.user.id}"
                    )
                return

            # Reembolsar participantes
            total_refunded = 0
            for user_id, tickets in self.lottery_data["participants"].items():
                user_total = sum(ticket["price"] for ticket in tickets)
                self.lottery_system.economy.refund_coins(
                    int(user_id),
                    user_total,
                    f"Reembolso do sorteio cancelado: {self.lottery_data['name']}",
                )
                total_refunded += user_total

            # Marcar como cancelado
            self.lottery_data["cancelled"] = True
            self.lottery_data["cancelled_at"] = datetime.now(timezone.utc).timestamp()

            # Atualizar dados
            self.lottery_system.active_lotteries[self.lottery_id] = self.lottery_data
            self.lottery_system.save_data()

            # Criar embed atualizado
            embed = self.lottery_system.create_lottery_embed(self.lottery_data)

            # Atualizar mensagem original do sorteio (desabilitar botões) com retry
            disabled_view = LotteryView(
                self.lottery_system, self.lottery_id, self.lottery_data
            )
            for item in disabled_view.children:
                item.disabled = True

            # Tentar atualizar a mensagem com retry para problemas de conectividade
            update_success = False
            for attempt in range(3):  # Máximo 3 tentativas
                try:
                    await original_message.edit(embed=embed, view=disabled_view)
                    update_success = True
                    break
                except discord.HTTPException as e:
                    if e.status == 503:  # Service Unavailable
                        logger.warning(
                            f"Tentativa {attempt + 1}/3 falhou (503 Service Unavailable). Tentando novamente em 2 segundos..."
                        )
                        if attempt < 2:  # Não esperar na última tentativa
                            await asyncio.sleep(2)
                        continue
                    else:
                        logger.error(f"Erro HTTP ao atualizar mensagem: {e}")
                        break
                except Exception as e:
                    logger.error(f"Erro inesperado ao atualizar mensagem: {e}")
                    break

            # Responder no painel admin
            if update_success:
                response_success = await safe_interaction_response(
                    interaction,
                    f"✅ **Sorteio cancelado com sucesso!**\n\n"
                    f"💰 **Total reembolsado:** {total_refunded} AC\n"
                    f"👥 **Participantes reembolsados:** {len(self.lottery_data['participants'])}\n"
                    f"📢 **A mensagem pública foi atualizada.**",
                    ephemeral=True,
                )
            else:
                response_success = await safe_interaction_response(
                    interaction,
                    f"⚠️ **Sorteio cancelado (com avisos)**\n\n"
                    f"💰 **Total reembolsado:** {total_refunded} AC\n"
                    f"👥 **Participantes reembolsados:** {len(self.lottery_data['participants'])}\n\n"
                    f"⚠️ **Atenção:** Não foi possível atualizar a mensagem pública devido a problemas de conectividade.\n"
                    f"Os reembolsos foram processados corretamente.",
                    ephemeral=True,
                )

            if not response_success:
                logger.warning(
                    f"Não foi possível responder à interação final de cancelamento do usuário {interaction.user.id}"
                )

        except Exception as e:
            logger.error(f"Erro ao cancelar sorteio: {e}")
            # Tentar responder com o erro usando a função segura
            response_success = await safe_interaction_response(
                interaction, "❌ Erro interno ao cancelar sorteio!", ephemeral=True
            )
            if not response_success:
                logger.error(
                    f"Não foi possível responder ao erro de cancelamento para o usuário {interaction.user.id}"
                )
            else:
                await interaction.response.send_message(
                    f"⚠️ **Sorteio cancelado (com avisos)**\n\n"
                    f"💰 **Total reembolsado:** {total_refunded} AC\n"
                    f"👥 **Participantes reembolsados:** {len(self.lottery_data['participants'])}\n\n"
                    f"⚠️ **Atenção:** Não foi possível atualizar a mensagem pública devido a problemas de conectividade.\n"
                    f"Os reembolsos foram processados corretamente.",
                    ephemeral=True,
                )

        except Exception as e:
            logger.error(f"Erro ao cancelar sorteio: {e}")
            await interaction.response.send_message(
                "❌ Erro interno ao cancelar sorteio!", ephemeral=True
            )

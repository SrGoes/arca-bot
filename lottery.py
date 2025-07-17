#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Sorteios do ARCA Bot

Gerencia criação, participação e sorteio de eventos com 
sistema de tickets escaláveis usando Arca Coins.

Autor: ARCA Organization
Licença: MIT
"""

import json
import os
import random
from datetime import datetime
from typing import Dict, List, Optional
import discord
from discord.ext import commands
import logging

logger = logging.getLogger('ARCA-Bot')

class LotterySystem:
    """Sistema de sorteios do bot ARCA"""
    
    def __init__(self, bot, economy_system):
        self.bot = bot
        self.economy = economy_system
        self.data_file = 'lottery_data.json'
        self.admin_role_name = "SORTEIO_ADMIN"  # Será ajustado depois
        self.lottery_channel_name = "sorteios"  # Será ajustado depois
        
        # Dados em memória
        self.active_lotteries = {}  # {message_id: lottery_data}
        self.admin_panels = {}  # {lottery_id: {'message': Message, 'user_id': int}}
        
        # Carregar dados
        self.load_data()
    
    def load_data(self):
        """Carrega dados dos sorteios ativos"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.active_lotteries = json.load(f)
                logger.info(f"Dados de sorteio carregados: {len(self.active_lotteries)} sorteios ativos")
            else:
                self.active_lotteries = {}
                logger.info("Arquivo de sorteio não encontrado, criando novo")
        except Exception as e:
            logger.error(f"Erro ao carregar dados de sorteio: {e}")
            self.active_lotteries = {}
    
    def save_data(self):
        """Salva dados dos sorteios"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.active_lotteries, f, indent=2, ensure_ascii=False)
            logger.debug("Dados de sorteio salvos")
        except Exception as e:
            logger.error(f"Erro ao salvar dados de sorteio: {e}")
    
    def has_admin_role(self, member: discord.Member) -> bool:
        """Verifica se o membro pode criar sorteios"""
        return any(role.name == self.admin_role_name for role in member.roles)
    
    def calculate_next_ticket_price(self, base_price: int, user_tickets_count: int) -> int:
        """Calcula o preço do próximo ticket para um usuário específico: 1.1^(qty) * base_price"""
        return int(base_price * (1.1 ** user_tickets_count))
    
    def create_lottery_embed(self, lottery_data: Dict) -> discord.Embed:
        """Cria embed para o sorteio"""
        embed = discord.Embed(
            title="🎲 Sorteio ARCA",
            description=f"**{lottery_data['name']}**",
            color=discord.Color.gold()
        )
        
        total_tickets = sum(len(tickets) for tickets in lottery_data['participants'].values())
        
        embed.add_field(
            name="🎫 Total de Tickets",
            value=str(total_tickets),
            inline=True
        )
        
        embed.add_field(
            name="👥 Participantes",
            value=str(len(lottery_data['participants'])),
            inline=True
        )
        
        # Mostrar preço do próximo ticket (baseado no primeiro ticket do usuário)
        next_ticket_price = self.calculate_next_ticket_price(lottery_data['base_price'], 0)
        embed.add_field(
            name="💰 Valor Inicial Ticket",
            value=f"{next_ticket_price} AC",
            inline=True
        )
        
        embed.add_field(
            name="👤 Criado por",
            value=f"<@{lottery_data['creator_id']}>",
            inline=True
        )
        
        embed.add_field(
            name="📅 Criado em",
            value=f"<t:{int(lottery_data['created_at'])}:R>",
            inline=True
        )
        
        if lottery_data.get('winner'):
            embed.add_field(
                name="🏆 Vencedor",
                value=f"<@{lottery_data['winner']['user_id']}>\n{lottery_data['winner']['tickets']} ticket(s)",
                inline=False
            )
            embed.color = discord.Color.green()
        
        if lottery_data.get('cancelled'):
            embed.add_field(
                name="❌ Cancelado",
                value="Este sorteio foi cancelado e os valores foram reembolsados.",
                inline=False
            )
            embed.color = discord.Color.red()
        
        embed.set_footer(text="ARCA Bot | Star Citizen")
        
        return embed
    
    def create_lottery_view(self, lottery_id: str, lottery_data: Dict):
        """Cria view com botões para o sorteio (apenas Comprar e Cancelar)"""
        return LotteryView(self, lottery_id, lottery_data)
    
    def create_admin_panel_view(self, lottery_id: str, lottery_data: Dict):
        """Cria view administrativa com botão de sortear"""
        return AdminLotteryView(self, lottery_id, lottery_data)
    
    def register_admin_panel(self, lottery_id: str, message: discord.Message, user_id: int):
        """Registra uma mensagem de painel admin para atualizações"""
        self.admin_panels[lottery_id] = {
            'message': message,
            'user_id': user_id
        }
        logger.info(f"Painel admin registrado para sorteio {lottery_id} (usuário {user_id})")
    
    async def update_admin_panel(self, lottery_id: str, lottery_data: Dict):
        """Atualiza o painel administrativo se existir"""
        logger.info(f"Tentando atualizar painel admin para sorteio {lottery_id}")
        
        if lottery_id in self.admin_panels:
            logger.info(f"Painel admin encontrado para sorteio {lottery_id}")
            try:
                panel_data = self.admin_panels[lottery_id]
                message = panel_data['message']
                
                # Criar embed atualizado para admin
                admin_embed = discord.Embed(
                    title="🔧 Painel Administrativo - Sorteio",
                    description=f"**{lottery_data['name']}**",
                    color=discord.Color.orange()
                )
                
                total_tickets = sum(len(tickets) for tickets in lottery_data['participants'].values())
                total_value = sum(sum(ticket['price'] for ticket in tickets) for tickets in lottery_data['participants'].values())
                
                admin_embed.add_field(
                    name="🎫 Total de Tickets",
                    value=str(total_tickets),
                    inline=True
                )
                
                admin_embed.add_field(
                    name="👥 Participantes",
                    value=str(len(lottery_data['participants'])),
                    inline=True
                )
                
                admin_embed.add_field(
                    name="💰 Total Arrecadado",
                    value=f"{total_value} AC",
                    inline=True
                )
                
                admin_embed.add_field(
                    name="💰 Valor Base",
                    value=f"{lottery_data['base_price']} AC",
                    inline=True
                )
                
                # Lista de participantes com tickets
                if lottery_data['participants']:
                    participants_list = []
                    for user_id, tickets in lottery_data['participants'].items():
                        try:
                            user = self.bot.get_user(int(user_id))
                            user_name = user.display_name if user else f"Usuário {user_id}"
                        except:
                            user_name = f"Usuário {user_id}"
                        
                        ticket_count = len(tickets)
                        user_total = sum(ticket['price'] for ticket in tickets)
                        participants_list.append(f"👤 **{user_name}**: {ticket_count} ticket(s) - {user_total} AC")
                    
                    # Limitar a 10 participantes para não estourar o limite do embed
                    if len(participants_list) > 10:
                        shown_participants = participants_list[:10]
                        shown_participants.append(f"... e mais {len(participants_list) - 10} participante(s)")
                    else:
                        shown_participants = participants_list
                    
                    admin_embed.add_field(
                        name="📋 Lista de Participantes",
                        value="\n".join(shown_participants),
                        inline=False
                    )
                else:
                    admin_embed.add_field(
                        name="📋 Lista de Participantes",
                        value="Nenhum participante ainda",
                        inline=False
                    )
                
                # Criar nova view admin
                admin_view = AdminLotteryView(self, lottery_id, lottery_data)
                
                # Atualizar mensagem
                await message.edit(embed=admin_embed, view=admin_view)
                logger.info(f"Painel admin atualizado com sucesso para sorteio {lottery_id}")
                
            except (discord.NotFound, discord.HTTPException):
                # Mensagem foi deletada, remover do tracking
                logger.warning(f"Mensagem do painel admin não encontrada, removendo do tracking: {lottery_id}")
                del self.admin_panels[lottery_id]
            except Exception as e:
                logger.error(f"Erro ao atualizar painel admin: {e}")
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
    async def buy_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Compra um ticket"""
        try:
            user_id = str(interaction.user.id)
            
            # Verificar se já foi sorteado
            if self.lottery_data.get('winner') or self.lottery_data.get('cancelled'):
                await interaction.response.send_message(
                    "❌ Este sorteio já foi finalizado!",
                    ephemeral=True
                )
                return
            
            # Calcular preço do ticket baseado na quantidade individual do usuário
            user_tickets_count = len(self.lottery_data['participants'].get(user_id, []))
            ticket_price = self.lottery_system.calculate_next_ticket_price(
                self.lottery_data['base_price'], 
                user_tickets_count
            )
            
            # Verificar saldo
            user_balance = self.lottery_system.economy.get_balance(interaction.user.id)
            if user_balance < ticket_price:
                await interaction.response.send_message(
                    f"❌ Saldo insuficiente! Você tem {user_balance} AC, mas precisa de {ticket_price} AC.",
                    ephemeral=True
                )
                return
            
            # Debitar moedas
            if not self.lottery_system.economy.remove_coins(interaction.user.id, ticket_price):
                await interaction.response.send_message(
                    "❌ Erro ao debitar moedas!",
                    ephemeral=True
                )
                return
            
            # Adicionar ticket
            if user_id not in self.lottery_data['participants']:
                self.lottery_data['participants'][user_id] = []
            
            ticket_number = len(self.lottery_data['participants'][user_id]) + 1
            self.lottery_data['participants'][user_id].append({
                'number': ticket_number,
                'price': ticket_price,
                'bought_at': datetime.now().timestamp()
            })
            
            # Salvar preço do ticket
            if 'ticket_prices' not in self.lottery_data:
                self.lottery_data['ticket_prices'] = []
            self.lottery_data['ticket_prices'].append(ticket_price)
            
            # Salvar dados
            self.lottery_system.active_lotteries[self.lottery_id] = self.lottery_data
            self.lottery_system.save_data()
            
            # Calcular próximo preço para este usuário
            next_price = self.lottery_system.calculate_next_ticket_price(
                self.lottery_data['base_price'], 
                user_tickets_count + 1
            )
            
            # Atualizar embed público da mensagem principal
            embed = self.lottery_system.create_lottery_embed(self.lottery_data)
            
            # Enviar confirmação privada primeiro
            await interaction.response.send_message(
                f"✅ **Ticket #{ticket_number} comprado com sucesso!**\n"
                f"💰 Valor pago: {ticket_price} AC\n" 
                f"💸 Seu próximo ticket custará: {next_price} AC\n"
                f"💳 Saldo restante: {user_balance - ticket_price} AC",
                ephemeral=True
            )
            
            # Buscar e editar a mensagem original do sorteio
            try:
                # A mensagem original é a que contém esta view
                original_message = interaction.message
                await original_message.edit(embed=embed, view=self)
                
                # Atualizar painel admin se existir
                logger.info(f"Chamando update_admin_panel para sorteio {self.lottery_id}")
                await self.lottery_system.update_admin_panel(self.lottery_id, self.lottery_data)
                
            except Exception as e:
                logger.error(f"Erro ao atualizar mensagem do sorteio: {e}")
                # Se não conseguir editar, pelo menos loggar o erro
            
        except Exception as e:
            logger.error(f"Erro ao comprar ticket: {e}")
            await interaction.response.send_message(
                "❌ Erro interno ao comprar ticket!",
                ephemeral=True
            )

class AdminLotteryView(discord.ui.View):
    """View administrativa com botões de sortear e cancelar"""
    
    def __init__(self, lottery_system, lottery_id: str, lottery_data: Dict):
        super().__init__(timeout=None)
        self.lottery_system = lottery_system
        self.lottery_id = lottery_id
        self.lottery_data = lottery_data
    
    @discord.ui.button(label="🎲 Sortear", style=discord.ButtonStyle.success)
    async def draw_lottery(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Sorteia o vencedor"""
        try:
            # Verificar se é o criador ou admin
            if (interaction.user.id != self.lottery_data['creator_id'] and 
                not self.lottery_system.has_admin_role(interaction.user)):
                
                # Buscar o nome do criador para uma mensagem mais amigável
                try:
                    creator = interaction.guild.get_member(self.lottery_data['creator_id'])
                    creator_name = creator.display_name if creator else "criador"
                except:
                    creator_name = "criador"
                
                await interaction.response.send_message(
                    f"🔒 **Acesso Negado**\n\n"
                    f"Apenas o {creator_name} do sorteio ou administradores com o cargo `{self.lottery_system.admin_role_name}` podem sortear!\n\n"
                    f"💡 Se você é o criador, verifique suas mensagens privadas para o painel administrativo.",
                    ephemeral=True
                )
                return
            
            # Verificar se há participantes
            if not self.lottery_data['participants']:
                await interaction.response.send_message(
                    "❌ Não há participantes no sorteio!",
                    ephemeral=True
                )
                return
            
            # Verificar se já foi sorteado
            if self.lottery_data.get('winner'):
                await interaction.response.send_message(
                    "❌ Este sorteio já foi realizado!",
                    ephemeral=True
                )
                return
            
            # Buscar a mensagem original do sorteio
            try:
                # Verificar se temos o channel_id e public_message_id salvos nos dados do sorteio
                if 'channel_id' not in self.lottery_data or 'public_message_id' not in self.lottery_data:
                    await interaction.response.send_message(
                        "❌ Informações do canal ou mensagem do sorteio não encontradas!",
                        ephemeral=True
                    )
                    return
                
                # Buscar o canal através do bot
                channel = self.lottery_system.bot.get_channel(self.lottery_data['channel_id'])
                if not channel:
                    await interaction.response.send_message(
                        "❌ Canal do sorteio não encontrado!",
                        ephemeral=True
                    )
                    return
                
                # Buscar a mensagem original usando o public_message_id
                original_message = await channel.fetch_message(self.lottery_data['public_message_id'])
            except Exception as e:
                logger.error(f"Erro ao buscar mensagem original: {e}")
                await interaction.response.send_message(
                    "❌ Não foi possível encontrar a mensagem original do sorteio!",
                    ephemeral=True
                )
                return
            
            # Criar lista de tickets
            all_tickets = []
            for user_id, tickets in self.lottery_data['participants'].items():
                all_tickets.extend([user_id] * len(tickets))
            
            # Sortear
            winner_id = random.choice(all_tickets)
            winner_tickets = len(self.lottery_data['participants'][winner_id])
            
            # Salvar vencedor
            self.lottery_data['winner'] = {
                'user_id': winner_id,
                'tickets': winner_tickets,
                'drawn_at': datetime.now().timestamp()
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
            except:
                pass
            
            # Atualizar mensagem original do sorteio (desabilitar botões)
            disabled_view = LotteryView(self.lottery_system, self.lottery_id, self.lottery_data)
            for item in disabled_view.children:
                item.disabled = True
            
            await original_message.edit(embed=embed, view=disabled_view)
            
            # Responder no painel admin
            await interaction.response.send_message(
                f"🎉 **Sorteio realizado!**\n\n"
                f"🏆 Vencedor: <@{winner_id}>\n"
                f"🎫 Tickets: {winner_tickets}\n"
                f"📊 Total de participantes: {len(self.lottery_data['participants'])}",
                ephemeral=True
            )
            
            # Mention público do vencedor no canal original
            try:
                await channel.send(
                    f"🎉 Parabéns <@{winner_id}>! Você ganhou o sorteio **{self.lottery_data['name']}**!"
                )
            except Exception as e:
                logger.error(f"Erro ao enviar mention público: {e}")
                # Se não conseguir enviar no canal original, tenta via followup
                await interaction.followup.send(
                    f"🎉 Parabéns <@{winner_id}>! Você ganhou o sorteio **{self.lottery_data['name']}**!"
                )
            
        except Exception as e:
            logger.error(f"Erro ao sortear: {e}")
            await interaction.response.send_message(
                "❌ Erro interno ao realizar sorteio!",
                ephemeral=True
            )
    
    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.danger)
    async def cancel_lottery_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancela o sorteio (versão admin)"""
        try:
            # Verificar se é o criador ou admin
            if (interaction.user.id != self.lottery_data['creator_id'] and 
                not self.lottery_system.has_admin_role(interaction.user)):
                
                # Buscar o nome do criador para uma mensagem mais amigável
                try:
                    creator = interaction.guild.get_member(self.lottery_data['creator_id'])
                    creator_name = creator.display_name if creator else "criador"
                except:
                    creator_name = "criador"
                
                await interaction.response.send_message(
                    f"🔒 **Acesso Negado**\n\n"
                    f"Apenas o {creator_name} do sorteio ou administradores com o cargo `{self.lottery_system.admin_role_name}` podem cancelar!\n\n"
                    f"💡 Se você é o criador, verifique suas mensagens privadas para o painel administrativo.",
                    ephemeral=True
                )
                return
            
            # Verificar se já foi sorteado
            if self.lottery_data.get('winner'):
                await interaction.response.send_message(
                    "❌ Não é possível cancelar um sorteio já realizado!",
                    ephemeral=True
                )
                return
            
            # Verificar se já foi cancelado
            if self.lottery_data.get('cancelled'):
                await interaction.response.send_message(
                    "❌ Este sorteio já foi cancelado!",
                    ephemeral=True
                )
                return
            
            # Buscar a mensagem original do sorteio
            try:
                # Verificar se temos o channel_id e public_message_id salvos nos dados do sorteio
                if 'channel_id' not in self.lottery_data or 'public_message_id' not in self.lottery_data:
                    await interaction.response.send_message(
                        "❌ Informações do canal ou mensagem do sorteio não encontradas!",
                        ephemeral=True
                    )
                    return
                
                # Buscar o canal através do bot
                channel = self.lottery_system.bot.get_channel(self.lottery_data['channel_id'])
                if not channel:
                    await interaction.response.send_message(
                        "❌ Canal do sorteio não encontrado!",
                        ephemeral=True
                    )
                    return
                
                # Buscar a mensagem original usando o public_message_id
                original_message = await channel.fetch_message(self.lottery_data['public_message_id'])
            except Exception as e:
                logger.error(f"Erro ao buscar mensagem original: {e}")
                await interaction.response.send_message(
                    "❌ Não foi possível encontrar a mensagem original do sorteio!",
                    ephemeral=True
                )
                return
            
            # Reembolsar participantes
            total_refunded = 0
            for user_id, tickets in self.lottery_data['participants'].items():
                user_total = sum(ticket['price'] for ticket in tickets)
                self.lottery_system.economy.add_coins(
                    int(user_id), 
                    user_total, 
                    f"Reembolso do sorteio cancelado: {self.lottery_data['name']}"
                )
                total_refunded += user_total
            
            # Marcar como cancelado
            self.lottery_data['cancelled'] = True
            self.lottery_data['cancelled_at'] = datetime.now().timestamp()
            
            # Atualizar dados
            self.lottery_system.active_lotteries[self.lottery_id] = self.lottery_data
            self.lottery_system.save_data()
            
            # Criar embed atualizado
            embed = self.lottery_system.create_lottery_embed(self.lottery_data)
            
            # Atualizar mensagem original do sorteio (desabilitar botões)
            disabled_view = LotteryView(self.lottery_system, self.lottery_id, self.lottery_data)
            for item in disabled_view.children:
                item.disabled = True
            
            await original_message.edit(embed=embed, view=disabled_view)
            
            # Responder no painel admin
            await interaction.response.send_message(
                f"❌ **Sorteio cancelado!**\n\n"
                f"💰 Total reembolsado: {total_refunded} AC\n"
                f"👥 Participantes reembolsados: {len(self.lottery_data['participants'])}",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Erro ao cancelar sorteio: {e}")
            await interaction.response.send_message(
                "❌ Erro interno ao cancelar sorteio!",
                ephemeral=True
            )

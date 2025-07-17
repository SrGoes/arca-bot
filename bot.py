#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARCA Bot - Bot Discord multipropósito para a organização ARCA (Star Citizen)

Este bot monitora mudanças de cargos, sistema de economia com Arca Coins,
sistema de sorteios e está preparado para expansão futura.

Autor: ARCA Organization
Licença: MIT
"""

import discord
from discord.ext import commands
import os
import logging
from datetime import datetime
from typing import Optional
import random
import uuid

# Tentar importar python-dotenv para carregar arquivo .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Se não tiver python-dotenv instalado, apenas continua
    pass

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ARCA-Bot')

# Importar sistemas
try:
    from economy import EconomySystem
    from lottery import LotterySystem
except ImportError as e:
    logger.error(f"Erro ao importar sistemas: {e}")
    EconomySystem = None
    LotterySystem = None

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ARCA-Bot')

class ARCABot(commands.Bot):
    """
    Classe principal do bot ARCA
    Herda de commands.Bot para funcionalidade expandida
    """
    
    def __init__(self):
        # Configurar intents necessários
        intents = discord.Intents.default()
        intents.members = True  # Necessário para detectar mudanças de membros
        intents.guilds = True   # Necessário para acessar informações do servidor
        intents.message_content = True  # Para comandos futuros
        intents.voice_states = True  # Para monitorar estados de voz
        
        super().__init__(
            command_prefix='!',  # Prefixo para comandos futuros
            intents=intents,
            description='Bot multipropósito da organização ARCA para Star Citizen',
            help_command=None  # Desabilitar comando de ajuda padrão
        )
        
        # Nome do canal onde logs de cargos serão enviados
        self.LOG_CHANNEL_NAME = 'log-cargos'
        
        # Sistemas
        self.economy = None
        self.lottery = None
        
    async def setup_hook(self):
        """Configurações iniciais do bot"""
        # Inicializar sistemas se disponíveis
        if EconomySystem and LotterySystem:
            self.economy = EconomySystem(self)
            self.lottery = LotterySystem(self, self.economy)
            logger.info("Sistemas de economia e sorteio inicializados")
        else:
            logger.warning("Sistemas de economia/sorteio não disponíveis")
        
    async def on_ready(self):
        """Evento chamado quando o bot está pronto"""
        logger.info(f'{self.user} conectou-se ao Discord!')
        logger.info(f'Bot está presente em {len(self.guilds)} servidor(es)')
        
        # Log dos servidores conectados
        for guild in self.guilds:
            logger.info(f'Servidor: {guild.name} (ID: {guild.id})')
            
        # Definir status do bot
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Star Citizen | ARCA Org"
            )
        )
        
    async def on_guild_join(self, guild):
        """Evento chamado quando o bot entra em um novo servidor"""
        logger.info(f'Bot adicionado ao servidor: {guild.name} (ID: {guild.id})')
        
    async def on_guild_remove(self, guild):
        """Evento chamado quando o bot sai de um servidor"""
        logger.info(f'Bot removido do servidor: {guild.name} (ID: {guild.id})')
    
    async def on_voice_state_update(self, member, before, after):
        """Monitora mudanças de estado de voz para economia"""
        if self.economy:
            await self.economy.on_voice_state_update(member, before, after)
    
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """
        Evento chamado quando um membro é atualizado (mudança de cargos, nickname, etc.)
        Monitora especificamente adições de cargos
        """
        try:
            # Verificar se houve mudança nos cargos
            if before.roles == after.roles:
                return  # Nenhuma mudança de cargo
            
            # Encontrar cargos adicionados
            added_roles = set(after.roles) - set(before.roles)
            
            # Se não há cargos adicionados, ignorar
            if not added_roles:
                return
            
            # Buscar canal de log no servidor
            log_channel = await self.get_log_channel(after.guild)
            if not log_channel:
                logger.warning(f'Canal "{self.LOG_CHANNEL_NAME}" não encontrado no servidor {after.guild.name}')
                return
            
            # Enviar mensagem para cada cargo adicionado
            for role in added_roles:
                # Ignorar cargo @everyone
                if role.name == '@everyone':
                    continue
                    
                embed = self.create_role_log_embed(after, role)
                
                try:
                    await log_channel.send(embed=embed)
                    logger.info(f'Log enviado: {after.display_name} recebeu o cargo {role.name} em {after.guild.name}')
                except discord.Forbidden:
                    logger.error(f'Sem permissão para enviar mensagem no canal {log_channel.name} em {after.guild.name}')
                except discord.HTTPException as e:
                    logger.error(f'Erro ao enviar mensagem: {e}')
                    
        except Exception as e:
            logger.error(f'Erro em on_member_update: {e}')
    
    async def get_log_channel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """
        Busca o canal de log no servidor
        
        Args:
            guild: O servidor onde buscar o canal
            
        Returns:
            O canal de texto ou None se não encontrado
        """
        for channel in guild.text_channels:
            if channel.name.lower() == self.LOG_CHANNEL_NAME.lower():
                return channel
        return None
    
    def create_role_log_embed(self, member: discord.Member, role: discord.Role) -> discord.Embed:
        """
        Cria um embed para o log de cargo
        
        Args:
            member: O membro que recebeu o cargo
            role: O cargo que foi adicionado
            
        Returns:
            Embed formatado para o log
        """
        embed = discord.Embed(
            title="🎉 Novo Cargo Atribuído",
            description=f"**{member.display_name}** recebeu o cargo **{role.name}**!",
            color=role.color if role.color != discord.Color.default() else discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Membro",
            value=f"{member.mention}\n`{member.name}#{member.discriminator}`",
            inline=True
        )
        
        embed.add_field(
            name="Cargo",
            value=f"{role.mention}\n`{role.name}`",
            inline=True
        )
        
        embed.add_field(
            name="Servidor",
            value=member.guild.name,
            inline=True
        )
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        embed.set_footer(
            text="ARCA Bot | Star Citizen",
            icon_url=self.user.avatar.url if self.user.avatar else None
        )
        
        return embed
    
    async def on_error(self, event: str, *args, **kwargs):
        """Tratamento de erros globais"""
        logger.error(f'Erro no evento {event}', exc_info=True)
    
    async def on_command_error(self, ctx, error):
        """Tratamento de erros de comandos"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignorar comandos não encontrados
        
        logger.error(f'Erro no comando {ctx.command}: {error}')
        
        try:
            await ctx.send(f'❌ Ocorreu um erro: {error}')
        except:
            pass  # Se não conseguir enviar a mensagem, apenas log

# Instanciar o bot
bot = ARCABot()

# ================== COMANDOS DE ECONOMIA ==================

@bot.command(name='saldo', aliases=['balance', 'bal'])
async def check_balance(ctx):
    """Verifica o saldo de Arca Coins"""
    if not ctx.bot.economy:
        await ctx.send("❌ Sistema de economia não está disponível!")
        return
    
    balance = ctx.bot.economy.get_balance(ctx.author.id)
    user_data = ctx.bot.economy.get_user_data(ctx.author.id)
    
    embed = discord.Embed(
        title="💰 Seu Saldo ARCA",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="💳 Saldo Atual",
        value=f"{balance} AC",
        inline=True
    )
    
    embed.add_field(
        name="📈 Total Ganho",
        value=f"{user_data['total_earned']} AC",
        inline=True
    )
    
    embed.add_field(
        name="⏱️ Tempo em Voz",
        value=f"{user_data['voice_time']} minutos",
        inline=True
    )
    
    embed.set_author(
        name=ctx.author.display_name,
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )
    
    embed.set_footer(text="ARCA Bot | Star Citizen")
    
    await ctx.send(embed=embed)

@bot.command(name='diario', aliases=['daily'])
async def daily_reward(ctx):
    """Recompensa diária (precisa estar em canal de voz da categoria C.O.M.M.S OPS)"""
    if not ctx.bot.economy:
        await ctx.send("❌ Sistema de economia não está disponível!")
        return
    
    # Verificar se está em canal de voz válido
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ Você precisa estar em um canal de voz para receber a recompensa diária!")
        return
    
    if not ctx.bot.economy.is_in_comms_category(ctx.author.voice.channel):
        await ctx.send(f"❌ Você precisa estar em um canal de voz da categoria **{ctx.bot.economy.voice_channels_category}**!")
        return
    
    user_data = ctx.bot.economy.get_user_data(ctx.author.id)
    
    # Verificar se já recebeu hoje
    if user_data['last_daily']:
        last_daily = datetime.fromisoformat(user_data['last_daily'])
        if (datetime.now() - last_daily).days < 1:
            next_daily = last_daily.replace(hour=23, minute=59, second=59)
            await ctx.send(f"❌ Você já recebeu sua recompensa diária hoje! Próxima disponível <t:{int(next_daily.timestamp())}:R>")
            return
    
    # Dar recompensa aleatória
    reward = random.randint(ctx.bot.economy.daily_reward_min, ctx.bot.economy.daily_reward_max)
    ctx.bot.economy.add_coins(ctx.author.id, reward, "Recompensa diária")
    
    # Atualizar última recompensa diária
    user_data['last_daily'] = datetime.now().isoformat()
    ctx.bot.economy.save_data()
    
    embed = discord.Embed(
        title="🎁 Recompensa Diária!",
        description=f"Você recebeu **{reward} AC**!",
        color=discord.Color.green()
    )
    
    new_balance = ctx.bot.economy.get_balance(ctx.author.id)
    embed.add_field(
        name="💳 Novo Saldo",
        value=f"{new_balance} AC",
        inline=True
    )
    
    embed.set_footer(text="Volte amanhã para mais!")
    
    await ctx.send(embed=embed)

@bot.command(name='distribuir')
@commands.has_permissions(administrator=True)  # Temporário até criar o cargo específico
async def distribute_coins(ctx, amount: int):
    """Distribui moedas para todos na mesma call (só admins)"""
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
    members_in_voice = [member for member in voice_channel.members if not member.bot]
    
    if not members_in_voice:
        await ctx.send("❌ Não há membros no canal de voz!")
        return
    
    # Distribuir moedas
    total_distributed = 0
    for member in members_in_voice:
        ctx.bot.economy.add_coins(member.id, amount, f"Distribuição por {ctx.author.display_name}")
        total_distributed += amount
    
    embed = discord.Embed(
        title="💰 Distribuição de Moedas",
        description=f"**{amount} AC** distribuído para **{len(members_in_voice)}** membros!",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="💳 Total Distribuído",
        value=f"{total_distributed} AC",
        inline=True
    )
    
    embed.add_field(
        name="📍 Canal",
        value=voice_channel.name,
        inline=True
    )
    
    members_list = ", ".join([member.display_name for member in members_in_voice[:10]])
    if len(members_in_voice) > 10:
        members_list += f" e mais {len(members_in_voice) - 10}..."
    
    embed.add_field(
        name="👥 Membros",
        value=members_list,
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='pagar')
@commands.has_permissions(administrator=True)  # Temporário até criar o cargo específico
async def clan_pay(ctx, member: discord.Member, amount: int):
    """Paga um membro gerando novas moedas (só admins)"""
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
    ctx.bot.economy.add_coins(member.id, amount, f"Pagamento do clã por {ctx.author.display_name}")
    
    embed = discord.Embed(
        title="💰 Pagamento do Clã",
        description=f"**{amount} AC** foi pago para {member.mention}!",
        color=discord.Color.green()
    )
    
    new_balance = ctx.bot.economy.get_balance(member.id)
    embed.add_field(
        name="💳 Novo Saldo",
        value=f"{new_balance} AC",
        inline=True
    )
    
    embed.add_field(
        name="👤 Pago por",
        value=ctx.author.mention,
        inline=True
    )
    
    await ctx.send(embed=embed)

# ================== COMANDOS DE SORTEIO ==================

@bot.command(name='criarsorteio')
@commands.has_permissions(administrator=True)  # Temporário até criar o cargo específico
async def create_lottery(ctx, *, args=None):
    """Cria um novo sorteio"""
    if not ctx.bot.lottery:
        await ctx.send("❌ Sistema de sorteio não está disponível!")
        return
    
    if not args:
        embed = discord.Embed(
            title="📋 Como Criar um Sorteio",
            description="Use: `!criarsorteio Nome do Sorteio | Valor do Ticket`",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Exemplo",
            value="`!criarsorteio Nave Aurora | 50`",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    try:
        # Parse dos argumentos
        parts = args.split('|')
        if len(parts) != 2:
            raise ValueError("Formato inválido")
        
        name = parts[0].strip()
        price = int(parts[1].strip())
        
        if price <= 0:
            raise ValueError("Preço inválido")
        
        if len(name) < 3:
            raise ValueError("Nome muito curto")
        
    except ValueError:
        await ctx.send("❌ Formato inválido! Use: `!criarsorteio Nome do Sorteio | Valor do Ticket`")
        return
    
    # Gerar ID único para o sorteio
    lottery_id = str(uuid.uuid4())
    
    # Criar dados do sorteio
    lottery_data = {
        'id': lottery_id,  # ID único do sorteio
        'name': name,
        'base_price': price,
        'creator_id': ctx.author.id,
        'created_at': datetime.now().timestamp(),
        'participants': {},
        'ticket_prices': [],
        'channel_id': ctx.channel.id  # Salvar ID do canal onde o sorteio foi criado
    }
    
    # Criar embed e view públicos (sem botão sortear)
    embed = ctx.bot.lottery.create_lottery_embed(lottery_data)
    view = ctx.bot.lottery.create_lottery_view(lottery_id, lottery_data)
    
    # Enviar mensagem pública
    message = await ctx.send("@everyone", embed=embed, view=view)
    
    # Salvar ID da mensagem pública no sorteio
    lottery_data['public_message_id'] = str(message.id)
    
    # Salvar sorteio
    ctx.bot.lottery.active_lotteries[lottery_id] = lottery_data
    ctx.bot.lottery.save_data()
    
    # Criar painel administrativo (com botão sortear) - enviado apenas para o criador
    admin_embed = discord.Embed(
        title="🔧 Painel Administrativo - Sorteio",
        description=f"**{name}**",
        color=discord.Color.orange()
    )
    
    admin_embed.add_field(
        name="🎫 Total de Tickets",
        value="0",
        inline=True
    )
    
    admin_embed.add_field(
        name="👥 Participantes",
        value="0",
        inline=True
    )
    
    admin_embed.add_field(
        name="💰 Total Arrecadado",
        value="0 AC",
        inline=True
    )
    
    admin_embed.add_field(
        name="💰 Valor Base",
        value=f"{price} AC",
        inline=True
    )
    
    admin_embed.add_field(
        name="📋 Lista de Participantes",
        value="Nenhum participante ainda",
        inline=False
    )
    
    admin_view = ctx.bot.lottery.create_admin_panel_view(lottery_id, lottery_data)
    
    # Enviar painel admin como mensagem privada para o criador
    try:
        admin_msg = await ctx.author.send(f"🔧 **Painel Administrativo do Sorteio**: {name}", embed=admin_embed, view=admin_view)
        # Registrar o painel admin para atualizações
        ctx.bot.lottery.register_admin_panel(lottery_id, admin_msg, ctx.author.id)
        
        # Confirmar no canal público que o painel foi enviado
        confirmation_embed = discord.Embed(
            title="✅ Sorteio Criado!",
            description=f"O painel administrativo foi enviado para {ctx.author.mention} via mensagem privada.",
            color=discord.Color.green()
        )
        confirmation_embed.add_field(
            name="📋 Informações",
            value=f"**Nome:** {name}\n**Valor Base:** {price} AC\n**Criador:** {ctx.author.mention}",
            inline=False
        )
        confirmation_embed.add_field(
            name="🔧 Painel Admin",
            value="Verifique suas mensagens privadas para acessar os controles de sortear e cancelar.",
            inline=False
        )
        
        await ctx.send(embed=confirmation_embed, delete_after=30)  # Auto-delete após 30 segundos
        
    except discord.Forbidden:
        # Se não conseguir enviar DM, envia no canal público mas com mention apenas para o criador
        warning_embed = discord.Embed(
            title="⚠️ Aviso - Mensagem Privada Bloqueada",
            description=f"{ctx.author.mention}, suas mensagens privadas estão bloqueadas. O painel será enviado aqui mas apenas você pode usá-lo.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=warning_embed, delete_after=10)
        
        admin_msg = await ctx.send(f"🔒 **Painel Administrativo de {ctx.author.mention}**", embed=admin_embed, view=admin_view)
        # Registrar o painel admin para atualizações
        ctx.bot.lottery.register_admin_panel(lottery_id, admin_msg, ctx.author.id)
    
    logger.info(f"Sorteio criado: {name} por {ctx.author.display_name}")

# ================== COMANDOS BÁSICOS ==================
@bot.command(name='ping')
async def ping(ctx):
    """Comando simples para testar se o bot está respondendo"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latência: {latency}ms",
        color=discord.Color.green() if latency < 100 else discord.Color.orange() if latency < 200 else discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command(name='info')
async def info(ctx):
    """Mostra informações sobre o bot"""
    embed = discord.Embed(
        title="🤖 ARCA Bot",
        description="Bot multipropósito da organização ARCA para Star Citizen",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📊 Estatísticas",
        value=f"Servidores: {len(bot.guilds)}\nUsuários: {len(bot.users)}",
        inline=True
    )
    
    embed.add_field(
        name="⚡ Funcionalidades",
        value="• Sistema de Economia (AC)\n• Sistema de Sorteios\n• Log de Cargos\n• Recompensas por Voz",
        inline=True
    )
    
    embed.add_field(
        name="💰 Comandos Economia",
        value="`!saldo` `!diario` `!distribuir` `!pagar`",
        inline=False
    )
    
    embed.add_field(
        name="🎲 Comandos Sorteio", 
        value="`!criarsorteio`",
        inline=False
    )
    
    embed.set_footer(text="Desenvolvido pela ARCA Organization")
    
    await ctx.send(embed=embed)

@bot.command(name='help', aliases=['ajuda'])
async def help_command(ctx):
    """Lista todos os comandos disponíveis"""
    embed = discord.Embed(
        title="📚 Comandos ARCA Bot",
        description="Lista completa de comandos disponíveis",
        color=discord.Color.blue()
    )
    
    # Comandos Básicos
    embed.add_field(
        name="🔧 Básicos",
        value="`!ping` - Latência do bot\n`!info` - Informações do bot\n`!help` - Esta mensagem",
        inline=False
    )
    
    # Comandos de Economia
    embed.add_field(
        name="💰 Economia",
        value=(
            "`!saldo` - Ver seu saldo de AC\n"
            "`!diario` - Recompensa diária (70-100 AC)\n"
            "`!distribuir <valor>` - Distribuir AC para todos na call (Admin)\n"
            "`!pagar <@user> <valor>` - Pagar AC para usuário (Admin)"
        ),
        inline=False
    )
    
    # Comandos de Sorteio
    embed.add_field(
        name="🎲 Sorteios",
        value=(
            "`!criarsorteio Nome | Valor` - Criar sorteio (Admin)\n"
            "Botões: 🎲 Sortear, 🎫 Comprar, ❌ Cancelar"
        ),
        inline=False
    )
    
    # Sistema Automático
    embed.add_field(
        name="⚡ Sistema Automático",
        value=(
            "• **20 AC/hora** por tempo em canais da categoria C.O.M.M.S OPS\n"
            "• **Log automático** de novos cargos no canal #log-cargos\n"
            "• **Backup automático** dos dados a cada 6 horas"
        ),
        inline=False
    )
    
    embed.set_footer(text="ARCA Bot | Star Citizen - Desenvolvido pela ARCA Organization")
    
    await ctx.send(embed=embed)

def main():
    """Função principal para executar o bot"""
    
    # Tentar obter token de diferentes fontes
    token = None
    
    # 1. Tentar variável de ambiente
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    # 2. Se não encontrou, tentar carregar do arquivo .env manualmente
    if not token:
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('DISCORD_BOT_TOKEN=') and not line.startswith('#'):
                        token = line.split('=', 1)[1].strip()
                        # Remover aspas se houver
                        if token.startswith('"') and token.endswith('"'):
                            token = token[1:-1]
                        elif token.startswith("'") and token.endswith("'"):
                            token = token[1:-1]
                        break
        except FileNotFoundError:
            pass
    
    # 3. Verificar se o token foi encontrado
    if not token:
        logger.error('❌ Token do bot não encontrado!')
        logger.error('📝 Soluções possíveis:')
        logger.error('   1. Defina a variável de ambiente: DISCORD_BOT_TOKEN=seu_token')
        logger.error('   2. Configure o arquivo .env com: DISCORD_BOT_TOKEN=seu_token')
        logger.error('   3. Certifique-se de que o python-dotenv está instalado: pip install python-dotenv')
        return
    
    # 4. Verificar se o token não está vazio ou é um placeholder
    if token in ['seu_token_aqui', 'YOUR_BOT_TOKEN_HERE', '']:
        logger.error('❌ Token inválido ou placeholder!')
        logger.error('📝 Edite o arquivo .env e substitua "seu_token_aqui" pelo token real do seu bot')
        return
    
    logger.info('✅ Token encontrado! Iniciando bot...')
    
    try:
        # Executar o bot
        bot.run(token)
    except discord.LoginFailure:
        logger.error('❌ Token de bot inválido! Verifique se o token está correto.')
        logger.error('🔗 Obtenha um novo token em: https://discord.com/developers/applications')
    except Exception as e:
        logger.error(f'❌ Erro ao executar o bot: {e}')

if __name__ == '__main__':
    main()

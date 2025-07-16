#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARCA Bot - Bot Discord multipropósito para a organização ARCA (Star Citizen)

Este bot monitora mudanças de cargos e registra quando membros recebem novos cargos.
Preparado para expansão futura com comandos, gerenciamento de eventos, punições, etc.

Autor: ARCA Organization
Licença: MIT
"""

import discord
from discord.ext import commands
import os
import logging
from datetime import datetime
from typing import Optional

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
        
        super().__init__(
            command_prefix='!',  # Prefixo para comandos futuros
            intents=intents,
            description='Bot multipropósito da organização ARCA para Star Citizen'
        )
        
        # Nome do canal onde logs de cargos serão enviados
        self.LOG_CHANNEL_NAME = 'log-cargos'
        
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

# Comandos básicos para teste e administração
@bot.command(name='ping')
async def ping(ctx):
    """Comando simples para testar se o bot está respondendo"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latência: {latency}ms",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command(name='info')
async def info(ctx):
    """Mostra informações sobre o bot"""
    embed = discord.Embed(
        title="ℹ️ ARCA Bot",
        description="Bot multipropósito da organização ARCA para Star Citizen",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Servidores",
        value=len(bot.guilds),
        inline=True
    )
    
    embed.add_field(
        name="Membros",
        value=sum(guild.member_count for guild in bot.guilds),
        inline=True
    )
    
    embed.add_field(
        name="Latência",
        value=f"{round(bot.latency * 1000)}ms",
        inline=True
    )
    
    embed.set_footer(text="Desenvolvido pela ARCA Organization")
    
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

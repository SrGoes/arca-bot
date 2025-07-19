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
from datetime import datetime, timezone
from typing import Optional

# Tentar importar python-dotenv para carregar arquivo .env
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # Se não tiver python-dotenv instalado, apenas continua
    pass

# Importar sistemas centralizados
try:
    import sys

    sys.path.insert(0, ".")  # Adicionar diretório raiz ao path
    sys.path.insert(0, "..")  # Adicionar diretório pai ao path
    from config.settings import config
    from src.core.utils.cache import CacheManager
    from src.core.utils.permissions import (
        PermissionManager,
        handle_permission_error,
    )
    from src.core.utils.wallet_panel import WalletPanel
    from src.core.utils.lottery_panel import LotteryPanel
    from src.modules.economy import EconomySystem
    from src.modules.lottery import LotterySystem
    from src.commands.economy import setup_economy_commands
    from src.commands.lottery import setup_lottery_commands
    from src.commands.basic import setup_basic_commands
    from src.commands.lottery_panel import setup_lottery_panel_commands
except ImportError as e:
    print(f"❌ Erro ao importar sistemas: {e}")
    print("📝 Certifique-se de que todos os arquivos foram criados corretamente")
    exit(1)


# Configuração de logging usando config
def setup_logging():
    """Configura o sistema de logging"""
    log_config = config.logging

    # Criar diretório de logs se não existir
    import os

    log_dir = os.path.dirname(log_config.file_name)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Remover handlers existentes para evitar duplicação
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configurar path correto para logs
    log_dir = "logs"
    log_file = os.path.join(log_dir, "bot.log")

    # Criar diretório de logs se não existir
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_config.level.upper()),
        format=log_config.format,
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


setup_logging()
logger = logging.getLogger("ARCA-Bot")


class ARCABot(commands.Bot):
    """
    Classe principal do bot ARCA
    Herda de commands.Bot para funcionalidade expandida
    """

    def __init__(self):
        # Configurar intents necessários
        intents = discord.Intents.default()
        intents.members = True  # Necessário para detectar mudanças de membros
        intents.guilds = True  # Necessário para acessar informações do servidor
        intents.message_content = True  # Para comandos futuros
        intents.voice_states = True  # Para monitorar estados de voz

        super().__init__(
            command_prefix=config.general.command_prefix,
            intents=intents,
            description="Bot multipropósito da organização ARCA para Star Citizen",
            help_command=None,  # Desabilitar comando de ajuda padrão
        )

        # Configurações do bot
        self.config = config

        # Sistemas principais
        self.economy = None
        self.lottery = None
        self.cache_manager = None
        self.permission_manager = None
        self.wallet_panel = None
        self.lottery_panel = None

    async def setup_hook(self):
        """Configurações iniciais do bot"""
        logger.info("🚀 Iniciando configuração do bot...")

        # Inicializar gerenciadores
        self.cache_manager = CacheManager(self.config)
        self.permission_manager = PermissionManager(self.config)

        # Inicializar sistemas se disponíveis
        if EconomySystem and LotterySystem:
            self.economy = EconomySystem(self)
            self.lottery = LotterySystem(self, self.economy)
            self.wallet_panel = WalletPanel(self, self.economy)
            self.lottery_panel = LotteryPanel(self, self.lottery)
            logger.info("✅ Sistemas de economia e sorteio inicializados")
        else:
            logger.warning("⚠️ Sistemas de economia/sorteio não disponíveis")

        # Iniciar cache
        if self.cache_manager:
            await self.cache_manager.start()
            logger.info("✅ Sistema de cache iniciado")

        # Painel será iniciado no on_ready quando os servidores estiverem disponíveis

        # Registrar comandos
        setup_economy_commands(self)
        setup_lottery_commands(self)
        setup_basic_commands(self)
        setup_lottery_panel_commands(self)
        logger.info("✅ Comandos registrados")

        logger.info("🎉 Configuração do bot concluída!")

    async def on_ready(self):
        """Evento chamado quando o bot está pronto"""
        logger.info(f"{self.user} conectou-se ao Discord!")
        logger.info(f"Bot está presente em {len(self.guilds)} servidor(es)")

        # Iniciar painel de carteiras agora que os servidores estão disponíveis
        if self.wallet_panel and not self.wallet_panel.is_running:
            await self.wallet_panel.start()
            logger.info("✅ Painel de carteiras iniciado")

        # Iniciar painel de loterias
        if self.lottery_panel and not self.lottery_panel.is_running:
            await self.lottery_panel.start()
            logger.info("✅ Painel de loterias iniciado")

        # Definir status do bot
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=self.config.general.status_message,
            )
        )

    async def on_guild_join(self, guild):
        """Evento chamado quando o bot entra em um novo servidor"""
        logger.info(f"Bot adicionado ao servidor: {guild.name} (ID: {guild.id})")

    async def on_guild_remove(self, guild):
        """Evento chamado quando o bot sai de um servidor"""
        logger.info(f"Bot removido do servidor: {guild.name} (ID: {guild.id})")

    async def on_voice_state_update(self, member, before, after):
        """Monitora mudanças de estado de voz para economia"""
        if self.economy:
            await self.economy.on_voice_state_update(member, before, after)

    async def on_message(self, message):
        """Processa mensagens para recompensas e comandos"""
        # Processar recompensas por mensagem
        if self.economy:
            await self.economy.on_message(message)
        
        # Processar comandos normalmente
        await self.process_commands(message)

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
                logger.warning(
                    f'Canal "{self.config.general.log_channel_name}" não encontrado no servidor {after.guild.name}'
                )
                return

            # Enviar mensagem para cada cargo adicionado
            for role in added_roles:
                # Ignorar cargo @everyone
                if role.name == "@everyone":
                    continue

                embed = self.create_role_log_embed(after, role)

                try:
                    await log_channel.send(embed=embed)
                    logger.info(
                        f"Log enviado: {after.display_name} recebeu o cargo {role.name} em {after.guild.name}"
                    )
                except discord.Forbidden:
                    logger.error(
                        f"Sem permissão para enviar mensagem no canal {log_channel.name} em {after.guild.name}"
                    )
                except discord.HTTPException as e:
                    logger.error(f"Erro ao enviar mensagem: {e}")

        except Exception as e:
            logger.error(f"Erro em on_member_update: {e}")

    async def get_log_channel(
        self, guild: discord.Guild
    ) -> Optional[discord.TextChannel]:
        """
        Busca o canal de log no servidor

        Args:
            guild: O servidor onde buscar o canal

        Returns:
            O canal de texto ou None se não encontrado
        """
        for channel in guild.text_channels:
            if channel.name.lower() == self.config.general.log_channel_name.lower():
                return channel
        return None

    def create_role_log_embed(
        self, member: discord.Member, role: discord.Role
    ) -> discord.Embed:
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
            color=(
                role.color
                if role.color != discord.Color.default()
                else discord.Color.green()
            ),
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="Membro",
            value=f"{member.mention}\n`{member.display_name}`",
            inline=True,
        )

        embed.add_field(
            name="Cargo", value=f"{role.mention}\n`{role.name}`", inline=True
        )

        embed.add_field(name="Servidor", value=member.guild.name, inline=True)

        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)

        embed.set_footer(
            text="ARCA Bot | Star Citizen",
            icon_url=self.user.avatar.url if self.user.avatar else None,
        )

        return embed

    async def on_error(self, event: str, *args, **kwargs):
        """Tratamento de erros globais"""
        logger.error(f"Erro no evento {event}", exc_info=True)

    async def on_command_error(self, ctx, error):
        """Tratamento de erros de comandos"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignorar comandos não encontrados

        # Tratar erros de permissão
        if isinstance(error, commands.CheckFailure):
            await handle_permission_error(ctx, error)
            return

        # Tratar erros de argumentos
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"❌ **Argumento obrigatório faltando**: `{error.param.name}`\n💡 Use `!help` para ver como usar o comando."
            )
            return

        if isinstance(error, commands.BadArgument):
            await ctx.send(
                f"❌ **Argumento inválido**: {error}\n💡 Verifique o formato e tente novamente."
            )
            return

        # Log detalhado do erro
        logger.error(
            f"Erro no comando {ctx.command}: {type(error).__name__}: {error}",
            exc_info=True,
        )

        try:
            await ctx.send(
                f"❌ **Erro inesperado**: {type(error).__name__}\n💡 Contate um administrador se o problema persistir."
            )
        except Exception:
            pass  # Se não conseguir enviar a mensagem, apenas log


# Instanciar o bot
bot = ARCABot()


def main():
    """Função principal para executar o bot"""

    # Tentar obter token de diferentes fontes
    token = None

    # 1. Tentar variável de ambiente
    token = os.getenv("DISCORD_BOT_TOKEN")

    # 2. Se não encontrou, tentar carregar do arquivo .env manualmente
    if not token:
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DISCORD_BOT_TOKEN=") and not line.startswith(
                        "#"
                    ):
                        token = line.split("=", 1)[1].strip()
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
        logger.error("❌ Token do bot não encontrado!")
        logger.error("📝 Soluções possíveis:")
        logger.error("   1. Defina a variável de ambiente: DISCORD_BOT_TOKEN=seu_token")
        logger.error("   2. Configure o arquivo .env com: DISCORD_BOT_TOKEN=seu_token")
        logger.error(
            "   3. Certifique-se de que o python-dotenv está instalado: pip install python-dotenv"
        )
        return

    # 4. Verificar se o token não está vazio ou é um placeholder
    if token in ["seu_token_aqui", "YOUR_BOT_TOKEN_HERE", ""]:
        logger.error("❌ Token inválido ou placeholder!")
        logger.error(
            '📝 Edite o arquivo .env e substitua "seu_token_aqui" pelo token real do seu bot'
        )
        return

    logger.info("✅ Token encontrado! Iniciando bot...")

    try:
        # Executar o bot
        bot.run(token)
    except discord.LoginFailure:
        logger.error("❌ Token de bot inválido! Verifique se o token está correto.")
        logger.error(
            "🔗 Obtenha um novo token em: https://discord.com/developers/applications"
        )
    except Exception as e:
        logger.error(f"❌ Erro ao executar o bot: {e}")


if __name__ == "__main__":
    main()

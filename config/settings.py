#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Configuração Centralizado do ARCA Bot

Gerencia todas as configurações do bot de forma centralizada,
permitindo fácil manutenção e personalização.

Autor: ARCA Organization
Licença: MIT
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger("ARCA-Bot")


@dataclass
class EconomyConfig:
    """Configurações do sistema de economia"""

    voice_channels_category: str = "C.O.M.M.S OPS"
    ac_per_hour: int = 20  # 20 AC por hora = 1 AC a cada 3 minutos
    daily_reward_min: int = 70
    daily_reward_max: int = 100
    admin_role_name: str = "ECONOMIA_ADMIN"
    min_voice_time_for_reward: int = 3  # minutos (tempo mínimo para receber 1 AC)
    max_restart_time_for_recovery: int = 15  # minutos (tempo máximo offline para continuar pagando)
    rate_limit_daily: int = 1  # comandos por dia
    rate_limit_commands: int = 5  # comandos por minuto
    delete_admin_commands: bool = True  # Apagar comandos administrativos após execução
    
    # Sistema de recompensas por mensagens
    message_reward_enabled: bool = True  # Habilitar recompensas por mensagem
    messages_for_reward: int = 12  # Número de mensagens para ganhar recompensa
    message_reward_min: int = 1  # Mínimo de AC por recompensa de mensagem
    message_reward_max: int = 40  # Máximo de AC por recompensa de mensagem
    message_reward_cooldown: int = 45  # Cooldown em minutos entre recompensas
    send_voice_summary_dm: bool = True  # Enviar resumo por DM ao sair da call


@dataclass
class LotteryConfig:
    """Configurações do sistema de sorteios"""

    admin_role_name: str = "SORTEIO_ADMIN"
    channel_name: str = "sorteios"
    max_ticket_price_multiplier: float = 2.0  # Máximo 2x o preço base
    rate_limit_buy: int = 10  # tickets por minuto
    delete_command_after_creation: bool = True  # Apagar comando após criar sorteio
    
    # Painel de histórico de sorteios
    history_panel_channel: str = "painel"  # Canal para o painel
    history_panel_enabled: bool = True  # Habilitar painel de histórico
    max_history_entries: int = 10  # Máximo de sorteios no painel
    panel_update_interval: int = 300  # Intervalo de atualização em segundos (5 min)


@dataclass
class GeneralConfig:
    """Configurações gerais do bot"""

    log_channel_name: str = "log-cargos"
    wallet_panel_channel: str = "painel"
    command_prefix: str = "!"
    backup_interval_hours: int = 6
    max_backups: int = 10
    status_message: str = "Star Citizen | ARCA Org"


@dataclass
class PermissionsConfig:
    """Configurações de permissões"""

    admin_roles: list = None
    moderator_roles: list = None
    economy_roles: list = None
    lottery_roles: list = None

    def __post_init__(self):
        if self.admin_roles is None:
            self.admin_roles = ["ADMIN", "Administrador", "Administrator"]
        if self.moderator_roles is None:
            self.moderator_roles = ["MODERADOR", "Moderator", "MOD"]
        if self.economy_roles is None:
            self.economy_roles = ["ECONOMIA_ADMIN", "Economy Admin"]
        if self.lottery_roles is None:
            self.lottery_roles = ["SORTEIO_ADMIN", "Lottery Admin"]


@dataclass
class CacheConfig:
    """Configurações do sistema de cache"""

    enable_cache: bool = True
    cache_ttl: int = 300  # 5 minutos
    max_cache_size: int = 1000
    auto_cleanup_interval: int = 600  # 10 minutos


@dataclass
class LoggingConfig:
    """Configurações de logging"""

    level: str = "INFO"
    file_name: str = "bot.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class ConnectivityConfig:
    """Configurações de conectividade e robustez"""

    max_retries: int = 3  # Máximo de tentativas para operações do Discord
    retry_delay: float = 2.0  # Delay em segundos entre tentativas
    timeout: float = 30.0  # Timeout para operações em segundos
    handle_503_errors: bool = True  # Automaticamente tentar novamente em erros 503


@dataclass
class BotConfig:
    """Configuração principal que agrupa todas as outras"""

    economy: EconomyConfig
    lottery: LotteryConfig
    general: GeneralConfig
    permissions: PermissionsConfig
    cache: CacheConfig
    logging: LoggingConfig
    connectivity: ConnectivityConfig

    def __init__(self):
        self.economy = EconomyConfig()
        self.lottery = LotteryConfig()
        self.general = GeneralConfig()
        self.permissions = PermissionsConfig()
        self.cache = CacheConfig()
        self.logging = LoggingConfig()
        self.connectivity = ConnectivityConfig()


class ConfigManager:
    """Gerenciador de configurações"""

    def __init__(self, config_file: str = "config/bot_config.json"):
        self.config_file = Path(config_file)
        self.config = BotConfig()
        self._ensure_config_dir()
        self.load_config()

    def _ensure_config_dir(self):
        """Garante que o diretório de configuração existe"""
        self.config_file.parent.mkdir(exist_ok=True)

    def load_config(self) -> BotConfig:
        """Carrega configurações do arquivo JSON"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Carregar cada seção
                if "economy" in data:
                    self.config.economy = EconomyConfig(**data["economy"])
                if "lottery" in data:
                    self.config.lottery = LotteryConfig(**data["lottery"])
                if "general" in data:
                    self.config.general = GeneralConfig(**data["general"])
                if "permissions" in data:
                    self.config.permissions = PermissionsConfig(**data["permissions"])
                if "cache" in data:
                    self.config.cache = CacheConfig(**data["cache"])
                if "logging" in data:
                    self.config.logging = LoggingConfig(**data["logging"])
                if "connectivity" in data:
                    self.config.connectivity = ConnectivityConfig(
                        **data["connectivity"]
                    )

                logger.info(f"Configurações carregadas de {self.config_file}")
            else:
                # Criar arquivo padrão se não existir
                self.save_config()
                logger.info(f"Arquivo de configuração criado: {self.config_file}")

        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
            logger.info("Usando configurações padrão")

        return self.config

    def save_config(self):
        """Salva configurações no arquivo JSON"""
        try:
            config_dict = {
                "economy": asdict(self.config.economy),
                "lottery": asdict(self.config.lottery),
                "general": asdict(self.config.general),
                "permissions": asdict(self.config.permissions),
                "cache": asdict(self.config.cache),
                "logging": asdict(self.config.logging),
                "connectivity": asdict(self.config.connectivity),
            }

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"Configurações salvas em {self.config_file}")

        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração específico"""
        try:
            section_obj = getattr(self.config, section)
            return getattr(section_obj, key, default)
        except AttributeError:
            return default

    def set(self, path_or_section: str, key_or_value=None, value=None):
        """Define um valor de configuração específico

        Aceita dois formatos:
        - set("section.key", value)
        - set("section", "key", value)
        """
        if value is None and key_or_value is not None:
            # Formato: set("section.key", value)
            parts = path_or_section.split(".", 1)
            if len(parts) != 2:
                logger.error(f"Caminho inválido: {path_or_section}")
                return
            section, key = parts
            value = key_or_value
        else:
            # Formato: set("section", "key", value)
            section = path_or_section
            key = key_or_value

        try:
            section_obj = getattr(self.config, section)
            setattr(section_obj, key, value)
            self.save_config()
        except AttributeError:
            logger.error(f"Seção ou chave inválida: {section}.{key}")

    def set_legacy(self, section: str, key: str, value: Any):
        """Método legado - mantido para compatibilidade"""
        return self.set(section, key, value)


# Instância global do gerenciador de configurações
config_manager = ConfigManager()
config = config_manager.config

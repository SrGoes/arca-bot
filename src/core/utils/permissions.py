#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Permissões do ARCA Bot

Sistema robusto de verificação de permissões baseado em cargos,
com hierarquia e verificações flexíveis.

Autor: ARCA Organization
Licença: MIT
"""

import logging
from typing import List, Union, Optional, Callable
from enum import Enum
import discord
from discord.ext import commands
from functools import wraps

logger = logging.getLogger('ARCA-Bot')

class PermissionLevel(Enum):
    """Níveis de permissão hierárquicos"""
    USER = 1
    MODERATOR = 2
    ECONOMY_ADMIN = 3
    LOTTERY_ADMIN = 4
    ADMIN = 5
    OWNER = 6

class PermissionManager:
    """Gerenciador de permissões"""
    
    def __init__(self, config):
        self.config = config.permissions
        self.permission_cache = {}
    
    def has_role_by_name(self, member: discord.Member, role_names: List[str]) -> bool:
        """Verifica se o membro tem algum dos cargos especificados"""
        if not member or not member.roles:
            return False
        
        member_role_names = [role.name for role in member.roles]
        
        for role_name in role_names:
            if role_name in member_role_names:
                return True
        
        return False
    
    def has_permission_level(self, member: discord.Member, required_level: PermissionLevel) -> bool:
        """Verifica se o membro tem o nível de permissão necessário"""
        if not member:
            return False
        
        # Owner do servidor sempre tem todas as permissões
        if member.guild.owner_id == member.id:
            return True
        
        # Administradores do Discord sempre têm acesso
        if member.guild_permissions.administrator:
            return True
        
        # Verificar hierarquia de permissões
        user_level = self.get_user_permission_level(member)
        return user_level.value >= required_level.value
    
    def get_user_permission_level(self, member: discord.Member) -> PermissionLevel:
        """Obtém o nível de permissão mais alto do usuário"""
        if not member:
            return PermissionLevel.USER
        
        # Cache key
        cache_key = f"{member.guild.id}:{member.id}"
        
        # Owner do servidor
        if member.guild.owner_id == member.id:
            self.permission_cache[cache_key] = PermissionLevel.OWNER
            return PermissionLevel.OWNER
        
        # Administrador do Discord
        if member.guild_permissions.administrator:
            self.permission_cache[cache_key] = PermissionLevel.ADMIN
            return PermissionLevel.ADMIN
        
        # Verificar cargos em ordem hierárquica
        if self.has_role_by_name(member, self.config.admin_roles):
            self.permission_cache[cache_key] = PermissionLevel.ADMIN
            return PermissionLevel.ADMIN
        
        if self.has_role_by_name(member, self.config.lottery_roles):
            self.permission_cache[cache_key] = PermissionLevel.LOTTERY_ADMIN
            return PermissionLevel.LOTTERY_ADMIN
        
        if self.has_role_by_name(member, self.config.economy_roles):
            self.permission_cache[cache_key] = PermissionLevel.ECONOMY_ADMIN
            return PermissionLevel.ECONOMY_ADMIN
        
        if self.has_role_by_name(member, self.config.moderator_roles):
            self.permission_cache[cache_key] = PermissionLevel.MODERATOR
            return PermissionLevel.MODERATOR
        
        # Usuário comum
        self.permission_cache[cache_key] = PermissionLevel.USER
        return PermissionLevel.USER
    
    def can_manage_economy(self, member: discord.Member) -> bool:
        """Verifica se pode gerenciar economia"""
        return self.has_permission_level(member, PermissionLevel.ECONOMY_ADMIN)
    
    def can_manage_lottery(self, member: discord.Member) -> bool:
        """Verifica se pode gerenciar sorteios"""
        return self.has_permission_level(member, PermissionLevel.LOTTERY_ADMIN)
    
    def can_moderate(self, member: discord.Member) -> bool:
        """Verifica se pode moderar"""
        return self.has_permission_level(member, PermissionLevel.MODERATOR)
    
    def can_admin(self, member: discord.Member) -> bool:
        """Verifica se é administrador"""
        return self.has_permission_level(member, PermissionLevel.ADMIN)
    
    def clear_cache(self, member: discord.Member = None):
        """Limpa cache de permissões"""
        if member:
            cache_key = f"{member.guild.id}:{member.id}"
            self.permission_cache.pop(cache_key, None)
        else:
            self.permission_cache.clear()
    
    def get_permission_info(self, member: discord.Member) -> dict:
        """Retorna informações detalhadas sobre permissões do usuário"""
        level = self.get_user_permission_level(member)
        
        return {
            'user_id': member.id,
            'level': level.name,
            'level_value': level.value,
            'can_economy': self.can_manage_economy(member),
            'can_lottery': self.can_manage_lottery(member),
            'can_moderate': self.can_moderate(member),
            'can_admin': self.can_admin(member),
            'is_owner': member.guild.owner_id == member.id,
            'roles': [role.name for role in member.roles if role.name != '@everyone']
        }

# Decorators para verificação de permissões
def require_permission(level: PermissionLevel):
    """Decorator que requer um nível específico de permissão"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # O primeiro argumento é sempre ctx em comandos do discord.py
            ctx = args[0] if args else kwargs.get('ctx')
            if not ctx:
                logger.error("Context não encontrado no comando")
                return
            
            # Verificar permissão
            if not hasattr(ctx.bot, 'permission_manager'):
                logger.error("PermissionManager não encontrado no bot")
                await ctx.send("❌ Sistema de permissões não configurado!")
                return
            
            if not ctx.bot.permission_manager.has_permission_level(ctx.author, level):
                await ctx.send(
                    f"🔒 **Acesso Negado**\n"
                    f"Você precisa do nível de permissão: **{level.name}**\n"
                    f"Seu nível atual: **{ctx.bot.permission_manager.get_user_permission_level(ctx.author).name}**"
                )
                return
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_economy_admin():
    """Decorator que requer permissão de administrador de economia"""
    return require_permission(PermissionLevel.ECONOMY_ADMIN)

def require_lottery_admin():
    """Decorator que requer permissão de administrador de sorteios"""
    return require_permission(PermissionLevel.LOTTERY_ADMIN)

def require_moderator():
    """Decorator que requer permissão de moderador"""
    return require_permission(PermissionLevel.MODERATOR)

def require_admin():
    """Decorator que requer permissão de administrador"""
    return require_permission(PermissionLevel.ADMIN)

# Verificações customizadas para commands.check()
def is_economy_admin():
    """Check para comandos que requerem admin de economia"""
    async def predicate(ctx):
        if not hasattr(ctx.bot, 'permission_manager'):
            return False
        return ctx.bot.permission_manager.can_manage_economy(ctx.author)
    
    return commands.check(predicate)

def is_lottery_admin():
    """Check para comandos que requerem admin de sorteios"""
    async def predicate(ctx):
        if not hasattr(ctx.bot, 'permission_manager'):
            return False
        return ctx.bot.permission_manager.can_manage_lottery(ctx.author)
    
    return commands.check(predicate)

def is_moderator():
    """Check para comandos que requerem moderador"""
    async def predicate(ctx):
        if not hasattr(ctx.bot, 'permission_manager'):
            return False
        return ctx.bot.permission_manager.can_moderate(ctx.author)
    
    return commands.check(predicate)

def is_admin():
    """Check para comandos que requerem administrador"""
    async def predicate(ctx):
        if not hasattr(ctx.bot, 'permission_manager'):
            return False
        return ctx.bot.permission_manager.can_admin(ctx.author)
    
    return commands.check(predicate)

class PermissionError(commands.CheckFailure):
    """Erro customizado para falhas de permissão"""
    def __init__(self, required_level: PermissionLevel, user_level: PermissionLevel):
        self.required_level = required_level
        self.user_level = user_level
        super().__init__(f"Nível {required_level.name} necessário, usuário tem {user_level.name}")

# Handler de erro para permissões
async def handle_permission_error(ctx, error):
    """Handler para erros de permissão"""
    if isinstance(error, commands.CheckFailure):
        if "economia" in ctx.command.name.lower():
            required_roles = ctx.bot.config.permissions.economy_roles
            role_list = "`, `".join(required_roles)
            await ctx.send(
                f"🔒 **Permissão Negada**\n"
                f"Este comando requer um dos seguintes cargos: `{role_list}`\n"
                f"💡 Contate um administrador se precisar de acesso."
            )
        elif "sorteio" in ctx.command.name.lower():
            required_roles = ctx.bot.config.permissions.lottery_roles
            role_list = "`, `".join(required_roles)
            await ctx.send(
                f"🔒 **Permissão Negada**\n"
                f"Este comando requer um dos seguintes cargos: `{role_list}`\n"
                f"💡 Contate um administrador se precisar de acesso."
            )
        else:
            await ctx.send(
                f"🔒 **Permissão Negada**\n"
                f"Você não tem permissão para usar este comando.\n"
                f"💡 Contate um administrador se precisar de acesso."
            )

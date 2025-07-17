#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Rate Limiting do ARCA Bot

Controla a frequência de comandos para prevenir spam
e abuso do sistema.

Autor: ARCA Organization
Licença: MIT
"""

import time
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from collections import defaultdict, deque

logger = logging.getLogger('ARCA-Bot')

class RateLimitType(Enum):
    """Tipos de rate limiting"""
    PER_USER = "per_user"
    PER_GUILD = "per_guild"
    GLOBAL = "global"
    PER_COMMAND = "per_command"

@dataclass
class RateLimit:
    """Configuração de rate limit"""
    max_uses: int
    window: int  # segundos
    limit_type: RateLimitType
    cooldown: int = 0  # cooldown após atingir limite

@dataclass
class RateLimitBucket:
    """Bucket de rate limiting"""
    uses: deque
    last_reset: float
    is_limited: bool = False
    limit_until: float = 0.0
    
    def __post_init__(self):
        if not hasattr(self, 'uses') or self.uses is None:
            self.uses = deque()

class RateLimiter:
    """Sistema de rate limiting"""
    
    def __init__(self):
        self.buckets: Dict[str, RateLimitBucket] = {}
        self.limits: Dict[str, RateLimit] = {}
    
    def add_limit(self, name: str, rate_limit: RateLimit):
        """Adiciona um novo rate limit"""
        self.limits[name] = rate_limit
        logger.info(f"Rate limit adicionado: {name} - {rate_limit.max_uses}/{rate_limit.window}s")
    
    def _get_bucket_key(self, limit_name: str, user_id: int, guild_id: Optional[int] = None) -> str:
        """Gera chave do bucket baseada no tipo de limite"""
        rate_limit = self.limits.get(limit_name)
        if not rate_limit:
            return f"{limit_name}:unknown"
        
        if rate_limit.limit_type == RateLimitType.PER_USER:
            return f"{limit_name}:user:{user_id}"
        elif rate_limit.limit_type == RateLimitType.PER_GUILD and guild_id:
            return f"{limit_name}:guild:{guild_id}"
        elif rate_limit.limit_type == RateLimitType.GLOBAL:
            return f"{limit_name}:global"
        elif rate_limit.limit_type == RateLimitType.PER_COMMAND:
            return f"{limit_name}:command:{user_id}"
        else:
            return f"{limit_name}:user:{user_id}"
    
    def _get_or_create_bucket(self, bucket_key: str) -> RateLimitBucket:
        """Obtém ou cria um bucket"""
        if bucket_key not in self.buckets:
            self.buckets[bucket_key] = RateLimitBucket(
                uses=deque(),
                last_reset=time.time()
            )
        return self.buckets[bucket_key]
    
    def _cleanup_bucket(self, bucket: RateLimitBucket, window: int):
        """Remove usos antigos do bucket"""
        current_time = time.time()
        
        # Remove usos fora da janela de tempo
        while bucket.uses and bucket.uses[0] < (current_time - window):
            bucket.uses.popleft()
    
    def check_rate_limit(self, limit_name: str, user_id: int, guild_id: Optional[int] = None) -> Tuple[bool, Optional[float]]:
        """
        Verifica se o usuário atingiu o rate limit
        
        Returns:
            Tuple[bool, Optional[float]]: (permitido, tempo_restante_cooldown)
        """
        if limit_name not in self.limits:
            return True, None
        
        rate_limit = self.limits[limit_name]
        bucket_key = self._get_bucket_key(limit_name, user_id, guild_id)
        bucket = self._get_or_create_bucket(bucket_key)
        
        current_time = time.time()
        
        # Verificar se ainda está em cooldown
        if bucket.is_limited and current_time < bucket.limit_until:
            remaining = bucket.limit_until - current_time
            return False, remaining
        
        # Reset do cooldown se passou
        if bucket.is_limited and current_time >= bucket.limit_until:
            bucket.is_limited = False
            bucket.limit_until = 0.0
        
        # Limpar usos antigos
        self._cleanup_bucket(bucket, rate_limit.window)
        
        # Verificar se excedeu o limite
        if len(bucket.uses) >= rate_limit.max_uses:
            bucket.is_limited = True
            bucket.limit_until = current_time + rate_limit.cooldown
            return False, rate_limit.cooldown
        
        # Adicionar uso atual
        bucket.uses.append(current_time)
        return True, None
    
    def reset_user_limits(self, user_id: int, limit_name: Optional[str] = None):
        """Reset dos limites de um usuário"""
        if limit_name:
            # Reset limite específico
            for bucket_key in list(self.buckets.keys()):
                if f"user:{user_id}" in bucket_key and limit_name in bucket_key:
                    del self.buckets[bucket_key]
        else:
            # Reset todos os limites do usuário
            for bucket_key in list(self.buckets.keys()):
                if f"user:{user_id}" in bucket_key:
                    del self.buckets[bucket_key]
    
    def get_user_status(self, user_id: int, limit_name: str, guild_id: Optional[int] = None) -> Dict:
        """Obtém status do rate limit para um usuário"""
        if limit_name not in self.limits:
            return {"error": "Rate limit não encontrado"}
        
        rate_limit = self.limits[limit_name]
        bucket_key = self._get_bucket_key(limit_name, user_id, guild_id)
        bucket = self._get_or_create_bucket(bucket_key)
        
        current_time = time.time()
        self._cleanup_bucket(bucket, rate_limit.window)
        
        remaining_uses = max(0, rate_limit.max_uses - len(bucket.uses))
        is_limited = bucket.is_limited and current_time < bucket.limit_until
        cooldown_remaining = max(0, bucket.limit_until - current_time) if is_limited else 0
        
        return {
            "limit_name": limit_name,
            "max_uses": rate_limit.max_uses,
            "window": rate_limit.window,
            "remaining_uses": remaining_uses,
            "is_limited": is_limited,
            "cooldown_remaining": cooldown_remaining,
            "current_uses": len(bucket.uses)
        }
    
    def cleanup_old_buckets(self, max_age: int = 3600):
        """Remove buckets antigos"""
        current_time = time.time()
        buckets_to_remove = []
        
        for bucket_key, bucket in self.buckets.items():
            # Se o bucket não foi usado há mais de max_age segundos
            if current_time - bucket.last_reset > max_age:
                buckets_to_remove.append(bucket_key)
        
        for bucket_key in buckets_to_remove:
            del self.buckets[bucket_key]
        
        if buckets_to_remove:
            logger.debug(f"Removidos {len(buckets_to_remove)} buckets antigos")

class CommandRateLimiter:
    """Rate limiter específico para comandos"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self._setup_default_limits()
    
    def _setup_default_limits(self):
        """Configura rate limits padrão"""
        # Comando diário - 1 uso por dia por usuário
        self.rate_limiter.add_limit("daily", RateLimit(
            max_uses=1,
            window=86400,  # 24 horas
            limit_type=RateLimitType.PER_USER,
            cooldown=0
        ))
        
        # Comandos de economia - 5 por minuto por usuário
        self.rate_limiter.add_limit("economy", RateLimit(
            max_uses=5,
            window=60,
            limit_type=RateLimitType.PER_USER,
            cooldown=30
        ))
        
        # Compra de tickets - 10 por minuto por usuário
        self.rate_limiter.add_limit("lottery_buy", RateLimit(
            max_uses=10,
            window=60,
            limit_type=RateLimitType.PER_USER,
            cooldown=60
        ))
        
        # Comandos administrativos - 20 por minuto por usuário
        self.rate_limiter.add_limit("admin", RateLimit(
            max_uses=20,
            window=60,
            limit_type=RateLimitType.PER_USER,
            cooldown=120
        ))
        
        # Comandos gerais - 30 por minuto por usuário
        self.rate_limiter.add_limit("general", RateLimit(
            max_uses=30,
            window=60,
            limit_type=RateLimitType.PER_USER,
            cooldown=60
        ))
    
    async def check_command_rate_limit(self, ctx, limit_name: str = "general") -> bool:
        """
        Verifica rate limit para um comando
        
        Returns:
            bool: True se permitido, False se limitado
        """
        guild_id = ctx.guild.id if ctx.guild else None
        allowed, cooldown = self.rate_limiter.check_rate_limit(
            limit_name, ctx.author.id, guild_id
        )
        
        if not allowed:
            # Enviar mensagem de rate limit
            if cooldown and cooldown > 0:
                minutes = int(cooldown // 60)
                seconds = int(cooldown % 60)
                
                if minutes > 0:
                    time_str = f"{minutes}m {seconds}s"
                else:
                    time_str = f"{seconds}s"
                
                await ctx.send(
                    f"⏳ **Rate Limit Atingido**\n"
                    f"Você está usando comandos muito rapidamente!\n"
                    f"⏱️ Tente novamente em: **{time_str}**",
                    delete_after=10
                )
            else:
                await ctx.send(
                    f"⏳ **Rate Limit Atingido**\n"
                    f"Você atingiu o limite de uso para este comando.\n"
                    f"⏱️ Tente novamente mais tarde.",
                    delete_after=10
                )
        
        return allowed
    
    def get_user_limits_status(self, user_id: int, guild_id: Optional[int] = None) -> Dict:
        """Obtém status de todos os rate limits de um usuário"""
        status = {}
        for limit_name in self.rate_limiter.limits.keys():
            status[limit_name] = self.rate_limiter.get_user_status(user_id, limit_name, guild_id)
        return status
    
    def reset_user(self, user_id: int, limit_name: Optional[str] = None):
        """Reset dos rate limits de um usuário (apenas para admins)"""
        self.rate_limiter.reset_user_limits(user_id, limit_name)

# Instância global do rate limiter
rate_limiter = CommandRateLimiter()

# Decorator para aplicar rate limiting
def rate_limit(limit_name: str = "general"):
    """Decorator para aplicar rate limiting a comandos"""
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # O primeiro argumento é sempre ctx em comandos do discord.py
            ctx = args[0] if args else kwargs.get('ctx')
            if not ctx:
                logger.error("Context não encontrado no comando")
                return
            
            # Verificar rate limit
            if not await rate_limiter.check_command_rate_limit(ctx, limit_name):
                return  # Rate limit atingido, não executar comando
            
            # Executar comando normalmente com todos os argumentos
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

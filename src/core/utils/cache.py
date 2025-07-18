#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Cache do ARCA Bot

Sistema de cache em memória com TTL para melhorar performance
e reduzir operações de I/O desnecessárias.

Autor: ARCA Organization
Licença: MIT
"""

import time
import logging
import asyncio
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass
from threading import Lock
import json
import hashlib

logger = logging.getLogger("ARCA-Bot")


@dataclass
class CacheItem:
    """Item individual do cache"""

    value: Any
    timestamp: float
    ttl: float
    access_count: int = 0

    @property
    def is_expired(self) -> bool:
        """Verifica se o item expirou"""
        return time.time() > (self.timestamp + self.ttl)

    def touch(self):
        """Atualiza timestamp de acesso"""
        self.access_count += 1


class MemoryCache:
    """Sistema de cache em memória com TTL"""

    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        self._cache: Dict[str, CacheItem] = {}
        self._lock = Lock()
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

        # Iniciar limpeza automática
        self._cleanup_task = None

    def _generate_key(self, key: Union[str, int, tuple]) -> str:
        """Gera chave de cache normalizada"""
        if isinstance(key, (int, str)):
            return str(key)
        elif isinstance(key, (tuple, list)):
            # Para chaves compostas, criar hash
            key_str = json.dumps(key, sort_keys=True)
            return hashlib.md5(key_str.encode()).hexdigest()
        else:
            return str(key)

    def get(self, key: Union[str, int, tuple], default: Any = None) -> Any:
        """Obtém valor do cache"""
        cache_key = self._generate_key(key)

        with self._lock:
            if cache_key in self._cache:
                item = self._cache[cache_key]

                if item.is_expired:
                    del self._cache[cache_key]
                    self.misses += 1
                    return default

                item.touch()
                self.hits += 1
                return item.value

            self.misses += 1
            return default

    def set(
        self, key: Union[str, int, tuple], value: Any, ttl: Optional[int] = None
    ) -> None:
        """Define valor no cache"""
        cache_key = self._generate_key(key)
        ttl = ttl or self.default_ttl

        with self._lock:
            # Se o cache está cheio, remover itens menos usados
            if len(self._cache) >= self.max_size:
                self._evict_least_used()

            self._cache[cache_key] = CacheItem(
                value=value, timestamp=time.time(), ttl=ttl
            )

    def delete(self, key: Union[str, int, tuple]) -> bool:
        """Remove item do cache"""
        cache_key = self._generate_key(key)

        with self._lock:
            if cache_key in self._cache:
                del self._cache[cache_key]
                return True
            return False

    def clear(self) -> None:
        """Limpa todo o cache"""
        with self._lock:
            self._cache.clear()
            self.hits = 0
            self.misses = 0

    def _evict_least_used(self) -> None:
        """Remove os itens menos usados"""
        if not self._cache:
            return

        # Ordenar por contagem de acesso e remover os 10% menos usados
        items_to_remove = max(1, len(self._cache) // 10)
        sorted_items = sorted(
            self._cache.items(), key=lambda x: (x[1].access_count, x[1].timestamp)
        )

        for i in range(items_to_remove):
            if i < len(sorted_items):
                key = sorted_items[i][0]
                del self._cache[key]

    def cleanup_expired(self) -> int:
        """Remove itens expirados e retorna quantidade removida"""
        removed_count = 0

        with self._lock:
            expired_keys = [key for key, item in self._cache.items() if item.is_expired]

            for key in expired_keys:
                del self._cache[key]
                removed_count += 1

        return removed_count

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "default_ttl": self.default_ttl,
        }

    async def start_cleanup_task(self, interval: int = 600):
        """Inicia task de limpeza automática"""
        if self._cleanup_task is not None:
            return

        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(interval)
                    removed = self.cleanup_expired()
                    if removed > 0:
                        logger.debug(
                            f"Cache cleanup: {removed} itens expirados removidos"
                        )
                except Exception as e:
                    logger.error(f"Erro na limpeza do cache: {e}")

        self._cleanup_task = asyncio.create_task(cleanup_loop())
        logger.info("Task de limpeza do cache iniciada")

    async def stop_cleanup_task(self):
        """Para a task de limpeza automática"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("Task de limpeza do cache parada")


class CacheManager:
    """Gerenciador central de cache"""

    def __init__(self, config):
        self.config = config.cache
        self.enabled = self.config.enable_cache

        if self.enabled:
            self.cache = MemoryCache(
                default_ttl=self.config.cache_ttl, max_size=self.config.max_cache_size
            )
        else:
            self.cache = None

    def get(self, key: Union[str, int, tuple], default: Any = None) -> Any:
        """Obtém valor do cache se habilitado"""
        if not self.enabled or not self.cache:
            return default
        return self.cache.get(key, default)

    def set(
        self, key: Union[str, int, tuple], value: Any, ttl: Optional[int] = None
    ) -> None:
        """Define valor no cache se habilitado"""
        if self.enabled and self.cache:
            self.cache.set(key, value, ttl)

    def delete(self, key: Union[str, int, tuple]) -> bool:
        """Remove item do cache se habilitado"""
        if self.enabled and self.cache:
            return self.cache.delete(key)
        return False

    def clear(self) -> None:
        """Limpa cache se habilitado"""
        if self.enabled and self.cache:
            self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        if not self.enabled or not self.cache:
            return {"enabled": False}

        stats = self.cache.get_stats()
        stats["enabled"] = True
        return stats

    async def start(self):
        """Inicia o gerenciador de cache"""
        if self.enabled and self.cache:
            await self.cache.start_cleanup_task(self.config.auto_cleanup_interval)

    async def stop(self):
        """Para o gerenciador de cache"""
        if self.enabled and self.cache:
            await self.cache.stop_cleanup_task()


# Funções de cache específicas para o bot
def cache_user_balance(user_id: int) -> str:
    """Gera chave de cache para saldo do usuário"""
    return f"user_balance_{user_id}"


def cache_user_data(user_id: int) -> str:
    """Gera chave de cache para dados do usuário"""
    return f"user_data_{user_id}"


def cache_guild_config(guild_id: int) -> str:
    """Gera chave de cache para configuração do servidor"""
    return f"guild_config_{guild_id}"


def cache_voice_members(channel_id: int) -> str:
    """Gera chave de cache para membros em canal de voz"""
    return f"voice_members_{channel_id}"


def cache_leaderboard(guild_id: int) -> str:
    """Gera chave de cache para ranking do servidor"""
    return f"leaderboard_{guild_id}"

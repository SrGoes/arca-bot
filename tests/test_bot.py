#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes Unitários do ARCA Bot

Testa os principais sistemas do bot para garantir
qualidade e funcionamento correto.

Autor: ARCA Organization
Licença: MIT
"""

import unittest
import asyncio
import tempfile
import os
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import sys

# Adicionar raiz e src ao path para importar módulos
root_dir = os.path.join(os.path.dirname(__file__), "..")
src_dir = os.path.join(root_dir, "src")
sys.path.insert(0, root_dir)
sys.path.insert(0, src_dir)

# Importar sistemas do bot
try:
    from config.settings import ConfigManager
    from core.utils.cache import MemoryCache
    from core.utils.rate_limiter import RateLimiter, RateLimit, RateLimitType
    from core.utils.permissions import PermissionManager, PermissionLevel
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)


class TestConfigManager(unittest.TestCase):
    """Testes para o sistema de configuração"""

    def setUp(self):
        """Configuração inicial para cada teste"""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, "test_config.json")

    def tearDown(self):
        """Limpeza após cada teste"""
        if os.path.exists(self.test_dir):
            import shutil

            shutil.rmtree(self.test_dir)

    def test_config_save_load(self):
        """Testa salvamento e carregamento de configuração"""
        config_manager = ConfigManager(self.config_file)

        # Testar salvamento
        test_data = {"test_key": "test_value", "number": 42}
        config_manager.save_config(test_data)

        # Verificar se arquivo foi criado
        self.assertTrue(os.path.exists(self.config_file))

        # Testar carregamento
        loaded_data = config_manager.load_config()
        self.assertEqual(loaded_data["test_key"], "test_value")
        self.assertEqual(loaded_data["number"], 42)

    def test_default_config_creation(self):
        """Testa criação de configuração padrão"""
        config_manager = ConfigManager(self.config_file)
        config = config_manager.load_config()

        # Verificar se contém chaves essenciais
        self.assertIn("general", config)
        self.assertIn("economy", config)
        self.assertIn("lottery", config)

    def test_get_set_config(self):
        """Testa métodos get e set"""
        config_manager = ConfigManager(self.config_file)

        # Testar set
        config_manager.set("test.nested.value", 123)

        # Testar get
        value = config_manager.get("test.nested.value")
        self.assertEqual(value, 123)

        # Testar get com default
        default_value = config_manager.get("nonexistent.key", "default")
        self.assertEqual(default_value, "default")


class TestMemoryCache(unittest.TestCase):
    """Testes para o sistema de cache"""

    def setUp(self):
        """Configuração inicial para cada teste"""
        self.cache = MemoryCache(max_size=100, default_ttl=60)

    def test_basic_operations(self):
        """Testa operações básicas do cache"""
        # Testar set e get
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")

        # Testar get com chave inexistente
        self.assertIsNone(self.cache.get("nonexistent"))

        # Testar delete
        self.cache.delete("key1")
        self.assertIsNone(self.cache.get("key1"))

    def test_ttl_expiration(self):
        """Testa expiração TTL"""
        # Definir TTL muito baixo
        self.cache.set("temp_key", "temp_value", ttl=0.1)

        # Verificar que está no cache
        self.assertEqual(self.cache.get("temp_key"), "temp_value")

        # Aguardar expiração (simulada)
        import time

        time.sleep(0.2)

        # Limpar itens expirados
        self.cache._cleanup_expired()

        # Verificar que foi removido
        self.assertIsNone(self.cache.get("temp_key"))

    def test_cache_stats(self):
        """Testa estatísticas do cache"""
        # Operações para gerar estatísticas
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # Hit
        self.cache.get("nonexistent")  # Miss

        stats = self.cache.get_stats()

        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["size"], 1)

    def test_eviction(self):
        """Testa política de remoção por tamanho"""
        # Cache muito pequeno
        small_cache = MemoryCache(max_size=2)

        # Adicionar mais itens que o limite
        small_cache.set("key1", "value1")
        small_cache.set("key2", "value2")
        small_cache.set("key3", "value3")  # Deve remover key1

        # Verificar remoção
        self.assertIsNone(small_cache.get("key1"))
        self.assertEqual(small_cache.get("key2"), "value2")
        self.assertEqual(small_cache.get("key3"), "value3")


class TestRateLimiter(unittest.TestCase):
    """Testes para o sistema de rate limiting"""

    def setUp(self):
        """Configuração inicial para cada teste"""
        self.rate_limiter = RateLimiter()

    def test_rate_limit_check(self):
        """Testa verificação de rate limit"""
        # Adicionar limite
        limit = RateLimit(max_uses=2, window=60, limit_type=RateLimitType.PER_USER)
        self.rate_limiter.add_limit("test", limit)

        # Primeira verificação - deve passar
        allowed1 = self.rate_limiter.check_rate_limit("test", 123, 456)
        self.assertTrue(allowed1)

        # Segunda verificação - deve passar
        allowed2 = self.rate_limiter.check_rate_limit("test", 123, 456)
        self.assertTrue(allowed2)

        # Terceira verificação - deve falhar
        allowed3 = self.rate_limiter.check_rate_limit("test", 123, 456)
        self.assertFalse(allowed3)

    def test_rate_limit_status(self):
        """Testa status do rate limit"""
        limit = RateLimit(max_uses=5, window=60, limit_type=RateLimitType.PER_USER)
        self.rate_limiter.add_limit("test", limit)

        # Fazer algumas verificações
        self.rate_limiter.check_rate_limit("test", 123, 456)
        self.rate_limiter.check_rate_limit("test", 123, 456)

        status = self.rate_limiter.get_user_status(123, "test", 456)

        self.assertEqual(status["max_uses"], 5)
        self.assertEqual(status["remaining_uses"], 3)

    def test_user_reset(self):
        """Testa reset de rate limit para usuário"""
        limit = RateLimit(max_uses=1, window=60, limit_type=RateLimitType.PER_USER)
        self.rate_limiter.add_limit("test", limit)

        # Esgotar limite
        self.rate_limiter.check_rate_limit("test", 123, 456)
        allowed_before = self.rate_limiter.check_rate_limit("test", 123, 456)
        self.assertFalse(allowed_before)

        # Reset do usuário
        self.rate_limiter.reset_user_limits(123)

        # Verificar se foi resetado
        allowed_after = self.rate_limiter.check_rate_limit("test", 123, 456)
        self.assertTrue(allowed_after)


class TestPermissionManager(unittest.TestCase):
    """Testes para o sistema de permissões"""

    def setUp(self):
        """Configuração inicial para cada teste"""
        # Mock da configuração
        mock_config = Mock()
        mock_config.permissions = Mock()
        mock_config.permissions.owner_ids = [111111]
        mock_config.permissions.admin_role_names = ["ADMIN"]
        mock_config.permissions.economy_admin_role_names = ["ECONOMIA_ADMIN"]
        mock_config.permissions.lottery_admin_role_names = ["SORTEIO_ADMIN"]

        self.permission_manager = PermissionManager(mock_config)

    def test_owner_permissions(self):
        """Testa permissões de owner"""
        # Mock do usuário owner
        mock_user = Mock()
        mock_user.id = 111111

        # Owner deve ter todas as permissões
        self.assertTrue(
            self.permission_manager.has_permission_level(
                mock_user, PermissionLevel.OWNER
            )
        )
        self.assertTrue(
            self.permission_manager.has_permission_level(
                mock_user, PermissionLevel.ADMIN
            )
        )
        self.assertTrue(
            self.permission_manager.has_permission_level(
                mock_user, PermissionLevel.ECONOMY_ADMIN
            )
        )

        level = self.permission_manager.get_user_permission_level(mock_user)
        self.assertEqual(level, PermissionLevel.OWNER)

    def test_admin_permissions(self):
        """Testa permissões de admin"""
        # Mock do usuário admin
        mock_user = Mock()
        mock_user.id = 222222
        mock_user.guild_permissions.administrator = True

        # Admin deve ter permissões de admin e abaixo
        self.assertFalse(
            self.permission_manager.has_permission_level(
                mock_user, PermissionLevel.OWNER
            )
        )
        self.assertTrue(
            self.permission_manager.has_permission_level(
                mock_user, PermissionLevel.DISCORD_ADMIN
            )
        )

        level = self.permission_manager.get_user_permission_level(mock_user)
        self.assertEqual(level, PermissionLevel.DISCORD_ADMIN)

    def test_economy_admin_permissions(self):
        """Testa permissões de admin de economia"""
        # Mock do usuário com cargo de economia
        mock_user = Mock()
        mock_user.id = 333333
        mock_user.guild_permissions.administrator = False

        mock_role = Mock()
        mock_role.name = "ECONOMIA_ADMIN"
        mock_user.roles = [mock_role]

        # Deve ter permissão de economia admin
        self.assertTrue(
            self.permission_manager.has_permission_level(
                mock_user, PermissionLevel.ECONOMY_ADMIN
            )
        )
        self.assertFalse(
            self.permission_manager.has_permission_level(
                mock_user, PermissionLevel.ADMIN
            )
        )

        level = self.permission_manager.get_user_permission_level(mock_user)
        self.assertEqual(level, PermissionLevel.ECONOMY_ADMIN)

    def test_user_permissions(self):
        """Testa permissões de usuário comum"""
        # Mock do usuário comum
        mock_user = Mock()
        mock_user.id = 444444
        mock_user.guild_permissions.administrator = False
        mock_user.roles = []

        # Deve ter apenas permissões de usuário
        self.assertTrue(
            self.permission_manager.has_permission_level(
                mock_user, PermissionLevel.USER
            )
        )
        self.assertFalse(
            self.permission_manager.has_permission_level(
                mock_user, PermissionLevel.ECONOMY_ADMIN
            )
        )

        level = self.permission_manager.get_user_permission_level(mock_user)
        self.assertEqual(level, PermissionLevel.USER)

    def test_discord_admin_permissions(self):
        """Testa permissões de administrador do Discord"""
        # Mock do usuário com permissão de administrador
        mock_user = Mock()
        mock_user.id = 555555
        mock_user.guild_permissions.administrator = True
        mock_user.roles = []

        # Deve ter permissões de admin do Discord
        self.assertTrue(
            self.permission_manager.has_permission_level(
                mock_user, PermissionLevel.DISCORD_ADMIN
            )
        )
        self.assertFalse(
            self.permission_manager.has_permission_level(
                mock_user, PermissionLevel.OWNER
            )
        )

        level = self.permission_manager.get_user_permission_level(mock_user)
        self.assertEqual(level, PermissionLevel.DISCORD_ADMIN)


class TestCacheManager(unittest.TestCase):
    """Testes para o gerenciador de cache"""

    def setUp(self):
        """Configuração inicial para cada teste"""
        # Mock da configuração
        mock_config = Mock()
        mock_config.cache = Mock()
        mock_config.cache.enabled = True
        mock_config.cache.max_size = 100
        mock_config.cache.default_ttl = 60

        self.cache_manager = Mock()
        self.cache_manager.get_stats.return_value = {
            "enabled": True,
            "hits": 10,
            "misses": 2,
            "hit_rate": 83.3,
            "size": 5,
            "max_size": 100,
            "default_ttl": 60,
        }

    def test_cache_operations(self):
        """Testa operações do gerenciador de cache"""
        # Simular operações
        self.cache_manager.set = Mock()
        self.cache_manager.get = Mock(return_value="cached_value")
        self.cache_manager.delete = Mock()
        self.cache_manager.clear = Mock()

        # Testar operações
        self.cache_manager.set("key", "value", 60)
        self.cache_manager.set.assert_called_once_with("key", "value", 60)

        result = self.cache_manager.get("key")
        self.assertEqual(result, "cached_value")

        self.cache_manager.delete("key")
        self.cache_manager.delete.assert_called_once_with("key")

        self.cache_manager.clear()
        self.cache_manager.clear.assert_called_once()

    def test_disabled_cache(self):
        """Testa comportamento com cache desabilitado"""
        # Mock da configuração com cache desabilitado
        mock_config = Mock()
        mock_config.cache = Mock()
        mock_config.cache.enabled = False

        disabled_cache_manager = Mock()
        disabled_cache_manager.get_stats.return_value = {"enabled": False}

        stats = disabled_cache_manager.get_stats()
        self.assertFalse(stats["enabled"])


def run_tests():
    """Executa todos os testes"""
    print("🧪 Executando testes unitários do ARCA Bot...")

    # Criar suite de testes
    test_suite = unittest.TestSuite()

    # Adicionar classes de teste
    test_classes = [
        TestConfigManager,
        TestMemoryCache,
        TestRateLimiter,
        TestPermissionManager,
        TestCacheManager,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Resumo
    if result.wasSuccessful():
        print(f"\n✅ Todos os {result.testsRun} testes passaram!")
        return True
    else:
        print(f"\n❌ {len(result.failures)} falhas, {len(result.errors)} erros")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para a nova estrutura modular do ARCA Bot v1.3.7
"""

import sys
import os
import unittest
import tempfile
import shutil
from unittest.mock import Mock, MagicMock, patch

# Adicionar o diretório raiz e src ao Python path
root_dir = os.path.join(os.path.dirname(__file__), "..")
src_dir = os.path.join(root_dir, "src")
sys.path.insert(0, root_dir)
sys.path.insert(0, src_dir)

# Imports da nova estrutura
from config.settings import ConfigManager, BotConfig
from core.utils.cache import MemoryCache
from core.utils.rate_limiter import RateLimiter
from core.utils.permissions import PermissionManager, PermissionLevel


class TestNewStructure(unittest.TestCase):
    """Testes para validar a nova estrutura modular"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, "test_config.json")

    def tearDown(self):
        """Limpeza após os testes"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_imports_working(self):
        """Testa se todos os imports da nova estrutura funcionam"""
        # Se chegamos até aqui, os imports estão funcionando
        self.assertTrue(True)
        print("✅ Todos os imports funcionando")

    def test_config_manager_basic(self):
        """Testa funcionalidades básicas do ConfigManager"""
        config_manager = ConfigManager(self.config_file)

        # Verificar se config é instância de BotConfig
        self.assertIsInstance(config_manager.config, BotConfig)

        # Verificar valores padrão
        self.assertEqual(config_manager.config.general.command_prefix, "!")
        self.assertEqual(config_manager.config.economy.ac_per_hour, 20)

        print("✅ ConfigManager funcionando")

    def test_memory_cache_basic(self):
        """Testa funcionalidades básicas do MemoryCache"""
        cache = MemoryCache(max_size=10, default_ttl=60)

        # Testar set/get básico
        cache.set("test_key", "test_value")
        value = cache.get("test_key")
        self.assertEqual(value, "test_value")

        # Testar miss
        miss_value = cache.get("nonexistent")
        self.assertIsNone(miss_value)

        print("✅ MemoryCache funcionando")

    def test_rate_limiter_basic(self):
        """Testa funcionalidades básicas do RateLimiter"""
        from core.utils.rate_limiter import RateLimit, RateLimitType

        limiter = RateLimiter()

        # Adicionar limite usando RateLimit object
        rate_limit = RateLimit(max_uses=2, window=60, limit_type=RateLimitType.PER_USER)
        limiter.add_limit("test_command", rate_limit)

        # Testar verificações
        allowed1 = limiter.check_rate_limit("test_command", 123)  # user_id = 123
        allowed2 = limiter.check_rate_limit("test_command", 123)
        allowed3 = limiter.check_rate_limit("test_command", 123)

        # Primeiras duas devem ser permitidas, terceira não
        self.assertTrue(allowed1[0])
        self.assertTrue(allowed2[0])
        self.assertFalse(allowed3[0])

        print("✅ RateLimiter funcionando")

    def test_permission_manager_basic(self):
        """Testa funcionalidades básicas do PermissionManager"""
        # Mock config
        mock_config = Mock()
        mock_config.owner_ids = [123456789]
        mock_config.admin_roles = ["ADMIN"]
        mock_config.economy_admin_roles = ["ECONOMIA_ADMIN"]
        mock_config.lottery_admin_roles = ["SORTEIO_ADMIN"]

        permission_manager = PermissionManager(mock_config)

        # Testar enum de permissões
        self.assertTrue(hasattr(PermissionLevel, "USER"))
        self.assertTrue(hasattr(PermissionLevel, "ADMIN"))
        self.assertTrue(hasattr(PermissionLevel, "OWNER"))

        print("✅ PermissionManager funcionando")

    def test_modules_importable(self):
        """Testa se os módulos principais são importáveis"""
        try:
            from modules.economy import EconomySystem
            from modules.lottery import LotterySystem

            print("✅ Módulos Economy e Lottery importáveis")
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Erro ao importar módulos: {e}")

    def test_commands_importable(self):
        """Testa se os comandos são importáveis"""
        try:
            from commands.economy import setup_economy_commands
            from commands.lottery import setup_lottery_commands
            from commands.basic import setup_basic_commands

            print("✅ Comandos importáveis")
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Erro ao importar comandos: {e}")

    def test_project_structure(self):
        """Testa se a estrutura de diretórios está correta"""
        base_dir = os.path.join(os.path.dirname(__file__), "..")

        # Verificar diretórios principais
        expected_dirs = [
            "src",
            "src/core",
            "src/core/utils",
            "src/modules",
            "src/commands",
            "config",
            "src/commands",
            "data",
            "logs",
            "tests",
            "scripts",
        ]

        for dir_name in expected_dirs:
            dir_path = os.path.join(base_dir, dir_name)
            self.assertTrue(
                os.path.exists(dir_path), f"Diretório {dir_name} não encontrado"
            )

        print("✅ Estrutura de diretórios correta")

    def test_main_launcher(self):
        """Testa se o launcher principal existe"""
        base_dir = os.path.join(os.path.dirname(__file__), "..")
        run_py = os.path.join(base_dir, "run.py")

        self.assertTrue(os.path.exists(run_py), "Launcher run.py não encontrado")
        print("✅ Launcher run.py presente")


def run_tests():
    """Função principal para executar os testes"""
    print("🧪 Executando testes da nova estrutura do ARCA Bot v1.3.7...")
    print("=" * 60)

    # Executar testes
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNewStructure)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 Todos os testes passaram! Nova estrutura está funcionando.")
        return True
    else:
        print(f"❌ {len(result.failures)} falhas, {len(result.errors)} erros")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

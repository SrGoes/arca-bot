# Configurações do ARCA Bot
# Copie este arquivo para config.py e ajuste conforme necessário

# ================== CONFIGURAÇÕES DE ECONOMIA ==================

# Categoria de canais de voz onde usuários ganham AC por tempo
VOICE_CHANNELS_CATEGORY = "C.O.M.M.S OPS"

# Quantidade de Arca Coins ganhos por hora em canais de voz
AC_PER_HOUR = 20

# Recompensa diária mínima e máxima
DAILY_REWARD_MIN = 70
DAILY_REWARD_MAX = 100

# Nome do cargo que pode usar comandos de administração de economia
ECONOMY_ADMIN_ROLE = "ECONOMIA_ADMIN"

# ================== CONFIGURAÇÕES DE SORTEIO ==================

# Nome do cargo que pode criar sorteios
LOTTERY_ADMIN_ROLE = "SORTEIO_ADMIN"

# Nome do canal onde ficará o painel de sorteios
LOTTERY_CHANNEL_NAME = "sorteios"

# ================== CONFIGURAÇÕES GERAIS ==================

# Nome do canal onde logs de cargos serão enviados
LOG_CHANNEL_NAME = "log-cargos"

# Intervalo de backup (em horas)
BACKUP_INTERVAL_HOURS = 6

# Quantidade máxima de backups mantidos
MAX_BACKUPS = 10

# Tempo mínimo em canal de voz para ganhar AC (em minutos)
MIN_VOICE_TIME_FOR_REWARD = 5

# ================== INSTRUÇÕES ==================

"""
Para usar essas configurações:

1. Copie este arquivo para config.py
2. Ajuste os valores conforme necessário
3. Importe no bot.py:
   from config import *

4. Crie os cargos necessários no Discord:
   - ECONOMIA_ADMIN
   - SORTEIO_ADMIN

5. Crie os canais necessários:
   - Categoria "C.O.M.M.S OPS" com canais de voz
   - Canal de texto "log-cargos"
   - Canal de texto "sorteios"

6. Configure as permissões adequadas para o bot
"""

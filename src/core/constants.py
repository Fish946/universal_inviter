from enum import Enum

class AccountStatus(Enum):
    ACTIVE = "active"
    BANNED = "banned"
    LIMITED = "limited"
    INACTIVE = "inactive"

class InviteStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    IN_PROGRESS = "in_progress"

# Задержки по умолчанию (в секундах)
DEFAULT_DELAYS = {
    'BETWEEN_ADDS': 180,      # 3 минуты между добавлениями
    'ERROR_DELAY': 60,        # 1 минута при ошибке
    'CHECK_DELAY': 5,         # 5 секунд между проверками
    'FLOOD_MULTIPLIER': 1.5   # Множитель для увеличения задержки при FloodWait
}

# Лимиты
LIMITS = {
    'MAX_ACCOUNTS': 10,       # Максимальное количество аккаунтов
    'MAX_RETRIES': 3,        # Максимальное количество попыток
    'MAX_DAILY_INVITES': 50  # Максимальное количество приглашений в день
}

# Пути к файлам
PATHS = {
    'DATABASE': 'data/accounts.db',
    'LOGS': 'data/logs',
    'CONFIG': 'data/config.json',
    'SESSIONS': 'data/sessions'
}
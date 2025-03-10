from telethon.errors import (
    FloodWaitError,
    UserBannedInChannelError,
    UserBlockedError,
    UserPrivacyRestrictedError,
    ChatWriteForbiddenError,
    ChatAdminRequiredError,
    UserNotMutualContactError,
    PeerFloodError
)

class TelethonErrorHandler:
    def get_retry_time(self, error: Exception) -> int:
        """Возвращает время ожидания в секундах перед следующей попыткой"""
        if isinstance(error, FloodWaitError):
            return error.seconds
        elif isinstance(error, PeerFloodError):
            return 3600  # 1 час
        return 60  # стандартная задержка 1 минута

    def get_user_friendly_message(self, error: Exception) -> str:
        """Возвращает понятное пользователю описание ошибки"""
        if isinstance(error, FloodWaitError):
            return f"Слишком много запросов. Нужно подождать {error.seconds} секунд"
        elif isinstance(error, UserBannedInChannelError):
            return "Пользователь заблокирован в канале"
        elif isinstance(error, UserBlockedError):
            return "Пользователь заблокировал бота"
        elif isinstance(error, UserPrivacyRestrictedError):
            return "Настройки приватности пользователя запрещают добавление"
        elif isinstance(error, ChatWriteForbiddenError):
            return "Нет прав для записи в чат"
        elif isinstance(error, ChatAdminRequiredError):
            return "Требуются права администратора"
        elif isinstance(error, UserNotMutualContactError):
            return "Пользователь должен быть в контактах"
        elif isinstance(error, PeerFloodError):
            return "Достигнут лимит на добавление пользователей"
        return f"Неизвестная ошибка: {str(error)}"

    def is_permanent_error(self, error: Exception) -> bool:
        """Проверяет, является ли ошибка постоянной (не временной)"""
        permanent_errors = (
            UserBannedInChannelError,
            UserBlockedError,
            UserPrivacyRestrictedError,
            ChatWriteForbiddenError,
            ChatAdminRequiredError
        )
        return isinstance(error, permanent_errors)
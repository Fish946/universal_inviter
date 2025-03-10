import os
from typing import Optional
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession

class SessionManager:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger('UniversalInviter')
        self.active_sessions = {}

    async def create_session(self, phone: str, api_id: str, api_hash: str) -> Optional[str]:
        """Создание новой сессии"""
        try:
            # Используем StringSession для хранения сессии в базе данных
            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.connect()
            
            if not await client.is_user_authorized():
                return None

            # Получаем строку сессии
            session_string = client.session.save()
            self.active_sessions[phone] = client
            
            return session_string

        except Exception as e:
            self.logger.error(f"Ошибка при создании сессии: {str(e)}")
            return None

    async def load_session(self, phone: str, api_id: str, api_hash: str, session_string: str) -> bool:
        """Загрузка существующей сессии"""
        try:
            client = TelegramClient(StringSession(session_string), api_id, api_hash)
            await client.connect()
            
            if not await client.is_user_authorized():
                self.logger.warning(f"Сессия для номера {phone} недействительна")
                return False

            self.active_sessions[phone] = client
            return True

        except Exception as e:
            self.logger.error(f"Ошибка при загрузке сессии: {str(e)}")
            return False

    async def close_session(self, phone: str):
        """Закрытие сессии"""
        if phone in self.active_sessions:
            try:
                await self.active_sessions[phone].disconnect()
                del self.active_sessions[phone]
            except Exception as e:
                self.logger.error(f"Ошибка при закрытии сессии: {str(e)}")

    async def close_all_sessions(self):
        """Закрытие всех активных сессий"""
        for phone in list(self.active_sessions.keys()):
            await self.close_session(phone)

    def cleanup_session_files(self):
        """Очистка временных файлов сессий"""
        try:
            for file in os.listdir():
                if file.endswith('.session'):
                    os.remove(file)
        except Exception as e:
            self.logger.error(f"Ошибка при очистке файлов сессий: {str(e)}") 
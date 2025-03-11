from PyQt6.QtCore import QThread, pyqtSignal
import asyncio
from core.services.invite_service import InviteService

class InviteThread(QThread):
    """Поток для выполнения приглашений"""
    progress_updated = pyqtSignal(dict)

    def __init__(self, account_manager, logger, account, channel, users, task_id):
        super().__init__()
        self.account_manager = account_manager
        self.logger = logger
        self.account = account
        self.channel = channel
        self.users = users
        self.task_id = task_id
        self.invite_service = InviteService(account_manager, logger)

    def run(self):
        """Запуск процесса приглашения"""
        try:
            # Создаем новый event loop для этого потока
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Запускаем приглашение
            self.loop.run_until_complete(self._run_inviting())
            
        except Exception as e:
            self.logger.error(f"Критическая ошибка в потоке приглашения: {str(e)}")
        finally:
            if self.loop:
                self.loop.close()

    async def _run_inviting(self):
        """Асинхронная часть процесса приглашения"""
        try:
            # Запускаем процесс приглашения через сервис
            await self.invite_service.start_inviting(
                self.account,
                self.channel,
                self.users,
                self.task_id,
                self.progress_updated.emit
            )
        except Exception as e:
            self.logger.error(f"Ошибка в процессе инвайтинга: {str(e)}") 
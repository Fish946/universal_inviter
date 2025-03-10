from typing import List, Dict, Optional, Set
import asyncio
import logging
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest, GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.errors import *
from .error_handler import TelethonErrorHandler

class Inviter:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger('UniversalInviter')
        self.error_handler = TelethonErrorHandler()
        self.active_tasks = {}
        self.stop_flags = {}
        
        # Задержки
        self.delays = {
            'between_adds': 180,  # 3 минуты между добавлениями
            'error_delay': 60,    # 1 минута при ошибке
            'check_delay': 5      # 5 секунд между проверками
        }

    async def get_channel_participants(self, client: TelegramClient, channel) -> Set[int]:
        """Получение списка участников канала"""
        try:
            participants = set()
            offset = 0
            limit = 100

            while True:
                result = await client(GetParticipantsRequest(
                    channel=channel,
                    filter=ChannelParticipantsSearch(''),
                    offset=offset,
                    limit=limit,
                    hash=0
                ))

                if not result.users:
                    break

                participants.update(user.id for user in result.users)
                offset += len(result.users)

            return participants

        except Exception as e:
            self.logger.error(f"Ошибка при получении списка участников: {str(e)}")
            return set()

    async def start_inviting(self, client: TelegramClient, channel_username: str, 
                           users_to_invite: List[str], task_id: str):
        """Начало процесса приглашения пользователей"""
        self.stop_flags[task_id] = False
        self.active_tasks[task_id] = {
            'total': len(users_to_invite),
            'invited': 0,
            'failed': 0,
            'skipped': 0
        }

        try:
            # Получаем информацию о канале
            channel = await client.get_entity(channel_username)
            
            # Получаем текущих участников
            existing_participants = await self.get_channel_participants(client, channel)
            
            for user in users_to_invite:
                if self.stop_flags[task_id]:
                    self.logger.info("Процесс приглашения остановлен пользователем")
                    break

                try:
                    # Получаем информацию о пользователе
                    user_entity = await client.get_entity(user)
                    
                    # Проверяем, не является ли пользователь уже участником
                    if user_entity.id in existing_participants:
                        self.active_tasks[task_id]['skipped'] += 1
                        self.logger.info(f"Пользователь {user} уже в канале")
                        continue

                    # Приглашаем пользователя
                    await client(InviteToChannelRequest(
                        channel=channel,
                        users=[user_entity]
                    ))

                    self.active_tasks[task_id]['invited'] += 1
                    self.logger.info(f"Пользователь {user} успешно приглашен")

                    # Ждем перед следующим приглашением
                    await asyncio.sleep(self.delays['between_adds'])

                except Exception as e:
                    self.active_tasks[task_id]['failed'] += 1
                    wait_time = self.error_handler.get_retry_time(e)
                    message = self.error_handler.get_user_friendly_message(e)
                    self.logger.error(f"Ошибка при приглашении {user}: {message}")
                    await asyncio.sleep(wait_time)

        except Exception as e:
            wait_time = self.error_handler.get_retry_time(e)
            message = self.error_handler.get_user_friendly_message(e)
            self.logger.error(f"Ошибка: {message}. Ожидание: {wait_time} секунд")
            if self.error_handler.is_permanent_error(e):
                self.logger.error("Обнаружена критическая ошибка. Процесс остановлен.")
                return
            await asyncio.sleep(wait_time)
        finally:
            del self.stop_flags[task_id]

    def stop_inviting(self, task_id: str):
        """Остановка процесса приглашения"""
        if task_id in self.stop_flags:
            self.stop_flags[task_id] = True

    def get_progress(self, task_id: str) -> Dict:
        """Получение прогресса приглашения"""
        return self.active_tasks.get(task_id, {})

    def set_delays(self, delays: Dict[str, int]):
        """Установка задержек"""
        self.delays.update(delays) 
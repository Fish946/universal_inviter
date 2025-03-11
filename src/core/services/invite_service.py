from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
from datetime import datetime
import asyncio

class InviteService:
    def __init__(self, account_manager, logger):
        self.account_manager = account_manager
        self.logger = logger
        self.stop_flags = {}
        self.delays = {
            'between_adds': 30,  # Задержка между добавлениями
            'error_delay': 60,   # Задержка при ошибке
            'check_delay': 300   # Задержка между проверками
        }

    def set_delays(self, delays: dict):
        """Установка задержек"""
        self.delays.update(delays)

    def stop_inviting(self, task_id: str):
        """Остановка процесса приглашения"""
        self.stop_flags[task_id] = True

    async def start_inviting(self, account, channel: str, users: list, task_id: str, progress_callback=None):
        """Запуск процесса приглашения пользователей"""
        try:
            # Создаем и подключаем клиент
            client = TelegramClient(
                f'sessions/{account.phone}',
                int(account.api_id),
                account.api_hash
            )
            
            await client.connect()
            
            # Проверяем авторизацию
            if not await client.is_user_authorized():
                self.logger.error("Аккаунт не авторизован. Пожалуйста, проверьте данные аккаунта.")
                return False

            # Получаем информацию о канале
            try:
                if not channel.startswith('@'):
                    channel = '@' + channel
                    
                channel_entity = await client.get_entity(channel)
                self.logger.info(f"Канал найден: {channel_entity.title}")
                
                # Проверяем права администратора
                participant = await client.get_permissions(channel_entity)
                if not participant.add_admins and not participant.invite_users:
                    self.logger.error("У вас нет прав для приглашения пользователей в этот канал")
                    return False
                    
            except ValueError:
                self.logger.error("Канал не найден. Проверьте правильность указанного юзернейма канала.")
                return False
            except Exception as e:
                self.logger.error(f"Ошибка при получении информации о канале: {self._get_error_message(e)}")
                return False

            total_users = len(users)
            invited = 0
            failed = 0
            skipped = 0

            self.logger.info(f"Начинаем приглашение пользователей. Всего в списке: {total_users}")

            for user in users:
                if self.stop_flags.get(task_id):
                    self.logger.info("Процесс приглашения остановлен пользователем")
                    break

                try:
                    # Проверяем формат пользователя
                    if not user.startswith('@'):
                        user = '@' + user
                        
                    # Получаем информацию о пользователе
                    self.logger.info(f"Получаем информацию о пользователе {user}")
                    user_entity = await client.get_entity(user)
                    
                    try:
                        # Проверяем, не является ли пользователь уже участником
                        participant = await client.get_permissions(channel_entity, user_entity)
                        if participant:
                            skipped += 1
                            self.logger.warning(f"⚠️ Пользователь {user} уже является участником канала")
                            continue
                            
                        # Приглашаем пользователя
                        await client(InviteToChannelRequest(
                            channel=channel_entity,
                            users=[user_entity]
                        ))
                        invited += 1
                        self.logger.info(f"✅ Пользователь {user} успешно приглашен в канал")
                        
                    except Exception as e:
                        failed += 1
                        error_msg = self._get_error_message(e)
                        self.logger.error(f"❌ Ошибка при приглашении {user}: {error_msg}")

                    # Обновляем прогресс через callback
                    if progress_callback:
                        progress_callback({
                            'invited': invited,
                            'failed': failed,
                            'skipped': skipped,
                            'total': total_users,
                            'current_user': user
                        })

                    # Ждем перед следующим приглашением
                    await asyncio.sleep(self.delays['between_adds'])

                except ValueError:
                    skipped += 1
                    self.logger.error(f"⚠️ Пользователь {user} не найден")
                    await asyncio.sleep(self.delays['error_delay'])
                except Exception as e:
                    skipped += 1
                    error_msg = self._get_error_message(e)
                    self.logger.error(f"⚠️ Ошибка при обработке пользователя {user}: {error_msg}")
                    await asyncio.sleep(self.delays['error_delay'])

            self.logger.info(
                f"Процесс завершен:\n"
                f"✅ Успешно приглашено: {invited}\n"
                f"❌ Ошибок: {failed}\n"
                f"⚠️ Пропущено: {skipped}"
            )

            return True

        except Exception as e:
            self.logger.error(f"Критическая ошибка в процессе инвайтинга: {self._get_error_message(e)}")
            return False
        finally:
            if client:
                try:
                    await client.disconnect()
                except:
                    pass

    def _get_error_message(self, error: Exception) -> str:
        """Преобразование ошибок Telegram в понятные русские сообщения"""
        error_str = str(error)
        
        error_messages = {
            'Too many requests': 'Слишком много запросов. Подождите некоторое время.',
            'The provided user ID is invalid': 'Указанный пользователь не существует',
            'USER_PRIVACY_RESTRICTED': 'Пользователь ограничил возможность приглашения в группы',
            'USER_NOT_MUTUAL_CONTACT': 'Пользователь должен быть в контактах',
            'USER_ALREADY_PARTICIPANT': 'Пользователь уже участник канала',
            'CHAT_ADMIN_REQUIRED': 'Требуются права администратора',
            'PEER_FLOOD': 'Достигнут лимит на приглашения. Подождите некоторое время.',
            'USERS_TOO_MUCH': 'Достигнут лимит участников в канале',
            'USER_BLOCKED': 'Пользователь заблокировал бота или аккаунт',
            'FLOOD_WAIT': 'Слишком много действий. Нужно подождать',
            'USERNAME_INVALID': 'Неверный формат имени пользователя',
            'USERNAME_NOT_OCCUPIED': 'Пользователь не существует',
            'CHANNEL_INVALID': 'Неверный канал',
            'CHANNEL_PRIVATE': 'Канал является приватным',
            'AUTH_KEY_UNREGISTERED': 'Сессия недействительна, требуется повторная авторизация',
            'SESSION_REVOKED': 'Сессия отозвана, требуется повторная авторизация',
            'USER_DEACTIVATED': 'Аккаунт деактивирован',
            'PHONE_NUMBER_INVALID': 'Неверный номер телефона',
            'API_ID_INVALID': 'Неверный API ID',
            'PHONE_CODE_INVALID': 'Неверный код подтверждения',
            'PHONE_CODE_EXPIRED': 'Код подтверждения истек',
            'PASSWORD_HASH_INVALID': 'Неверный пароль 2FA'
        }

        for key, value in error_messages.items():
            if key.lower() in error_str.lower():
                return value

        return f"Неизвестная ошибка: {error_str}" 
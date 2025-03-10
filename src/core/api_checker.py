import asyncio
from typing import Dict, Optional, Tuple
from telethon import TelegramClient, errors
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import GetDialogsRequest
from datetime import datetime
import logging

class APIChecker:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger('UniversalInviter')
        self._client: Optional[TelegramClient] = None
        
    async def check_api(self, api_id: str, api_hash: str, phone: str) -> Dict[str, bool]:
        """Проверка API на наличие ограничений"""
        try:
            # Создаем временную сессию для проверки
            session_name = f"checker_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            client = TelegramClient(session_name, api_id, api_hash)
            
            self.logger.info(f"Начинаем проверку API для номера {phone}")
            await client.connect()
            
            # Проверяем авторизацию
            if not await client.is_user_authorized():
                self.logger.info("Требуется авторизация")
                return {
                    "authorized": False,
                    "can_join_channels": False,
                    "can_invite_users": False,
                    "error": "Требуется авторизация"
                }

            results = {
                "authorized": True,
                "can_join_channels": False,
                "can_invite_users": False,
                "error": None
            }

            # Проверяем возможность получения диалогов
            try:
                await client(GetDialogsRequest(
                    offset_date=None,
                    offset_id=0,
                    offset_peer=None,
                    limit=1,
                    hash=0
                ))
                results["can_join_channels"] = True
            except errors.UserDeactivatedBanError:
                results["error"] = "Аккаунт заблокирован"
                self.logger.error("Аккаунт заблокирован")
            except Exception as e:
                results["error"] = f"Ошибка при проверке диалогов: {str(e)}"
                self.logger.error(f"Ошибка при проверке диалогов: {str(e)}")

            # Проверяем возможность приглашения пользователей
            if results["can_join_channels"]:
                try:
                    # Здесь можно добавить проверку на возможность приглашения
                    # Например, попытаться получить список участников канала
                    results["can_invite_users"] = True
                except Exception as e:
                    results["error"] = f"Ошибка при проверке прав на приглашение: {str(e)}"
                    self.logger.error(f"Ошибка при проверке прав на приглашение: {str(e)}")

            return results

        except errors.ApiIdInvalidError:
            self.logger.error("Неверный API ID")
            return {"error": "Неверный API ID", "authorized": False}
        except errors.PhoneNumberBannedError:
            self.logger.error("Номер телефона заблокирован")
            return {"error": "Номер телефона заблокирован", "authorized": False}
        except Exception as e:
            self.logger.error(f"Неизвестная ошибка при проверке API: {str(e)}")
            return {"error": f"Неизвестная ошибка: {str(e)}", "authorized": False}
        finally:
            if client and client.is_connected():
                await client.disconnect()

    async def authorize_client(self, api_id: str, api_hash: str, phone: str) -> Tuple[bool, Optional[str]]:
        """Авторизация клиента"""
        try:
            session_name = f"session_{phone}"
            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()

            if not await client.is_user_authorized():
                # Отправляем код подтверждения
                await client.send_code_request(phone)
                self.logger.info(f"Код подтверждения отправлен на номер {phone}")
                return False, "Требуется код подтверждения"

            return True, None

        except errors.FloodWaitError as e:
            wait_time = str(e).split('Wait ')[1].split(' seconds')[0]
            error_msg = f"Слишком много попыток. Подождите {wait_time} секунд"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Ошибка при авторизации: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    async def submit_code(self, phone: str, code: str) -> Tuple[bool, Optional[str]]:
        """Подтверждение кода авторизации"""
        try:
            if not self._client:
                return False, "Клиент не инициализирован"

            await self._client.sign_in(phone, code)
            return True, None

        except errors.SessionPasswordNeededError:
            return False, "Требуется пароль двухфакторной аутентификации"
        except errors.PhoneCodeInvalidError:
            return False, "Неверный код подтверждения"
        except Exception as e:
            return False, f"Ошибка при подтверждении кода: {str(e)}"

    async def submit_2fa_password(self, password: str) -> Tuple[bool, Optional[str]]:
        """Подтверждение пароля двухфакторной аутентификации"""
        try:
            if not self._client:
                return False, "Клиент не инициализирован"

            await self._client.sign_in(password=password)
            return True, None

        except errors.PasswordHashInvalidError:
            return False, "Неверный пароль 2FA"
        except Exception as e:
            return False, f"Ошибка при вводе пароля 2FA: {str(e)}"
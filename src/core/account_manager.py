from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
from telethon.errors import *
from telethon import TelegramClient
import asyncio

from utils.database import Database, Account
from core.session_manager import SessionManager
from core.api_checker import APIChecker
from utils.logger import Logger

class AccountManager:
    def __init__(self, db: Database, logger: Logger):
        self.db = db
        self.logger = logger
        self.clients: Dict[str, TelegramClient] = {}
        self._lock = asyncio.Lock()
        self.session_manager = SessionManager(logger)
        self.api_checker = APIChecker(logger)
        self.active_accounts: Dict[str, Dict[str, Any]] = {}

    async def add_account(self, phone: str, api_id: str, api_hash: str, 
                         code_callback=None, password_callback=None) -> tuple:
        try:
            client = TelegramClient(
                f'sessions/{phone}',
                int(api_id),
                api_hash
            )

            await client.connect()

            if not await client.is_user_authorized():
                # Отправляем код
                await client.send_code_request(phone)
                
                # Получаем код через колбэк
                if code_callback:
                    code = await asyncio.get_event_loop().run_in_executor(None, code_callback)
                    if not code:
                        return False, "Отменено пользователем"
                    
                    try:
                        # Пытаемся войти с полученным кодом
                        await client.sign_in(phone, code)
                    except SessionPasswordNeededError:
                        # Если требуется 2FA
                        if password_callback:
                            password = await asyncio.get_event_loop().run_in_executor(None, password_callback)
                            if not password:
                                return False, "Отменено пользователем"
                            await client.sign_in(password=password)
                        else:
                            return False, "Требуется пароль двухфакторной аутентификации"

            # Сохраняем данные аккаунта
            await self.db.add_account(phone, api_id, api_hash)
            return True, "Аккаунт успешно добавлен"

        except Exception as e:
            return False, str(e)

    async def load_accounts(self) -> None:
        """Загрузка всех аккаунтов из базы данных"""
        try:
            accounts = self.db.get_all_accounts()
            for account in accounts:
                try:
                    await self.open_connection(account)
                except Exception as e:
                    self.logger.error(f"Ошибка при загрузке аккаунта {account.phone}: {str(e)}")
    
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке аккаунтов: {str(e)}")

    async def open_connection(self, account: Account) -> Optional[TelegramClient]:
        """Открытие соединения для аккаунта"""
        try:
            async with self._lock:
                if account.phone in self.clients:
                    client = self.clients[account.phone]
                    if client.is_connected():
                        return client

                client = TelegramClient(
                    f"sessions/{account.phone}",
                    account.api_id,
                    account.api_hash
                )
                
                await client.connect()
                
                if not await client.is_user_authorized():
                    await client.sign_in(account.phone, code_callback=None)
                    self.logger.warning(f"Аккаунт {account.phone} требует повторной авторизации")
                    return None
                
                self.clients[account.phone] = client
                return client

        except (PhoneNumberBannedError, UserDeactivatedBanError) as e:
            self.logger.error(f"Аккаунт {account.phone} заблокирован: {str(e)}")
            account.is_active = False
            account.restrictions = str(e)
            self.db.update_account(account)
            return None
            
        except SessionPasswordNeededError:
            self.logger.warning(f"Аккаунт {account.phone} требует ввода пароля 2FA")
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка при подключении аккаунта {account.phone}: {str(e)}")
            return None

    async def get_client(self, phone: str) -> Optional[TelegramClient]:
        """Получение клиента для аккаунта по номеру телефона"""
        try:
            if phone in self.clients:
                client = self.clients[phone]
                if client.is_connected():
                    return client
                    
            account = next((acc for acc in self.db.get_all_accounts() if acc.phone == phone), None)
            if not account:
                self.logger.error(f"Аккаунт {phone} не найден в базе данных")
                return None
                
            return await self.open_connection(account)
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении клиента для {phone}: {str(e)}")
            return None

    async def check_all_accounts(self) -> Dict[str, dict]:
        """Проверка всех аккаунтов"""
        results = {}
        try:
            accounts = self.db.get_all_accounts()
            for account in accounts:
                try:
                    client = await self.get_client(account.phone)
                    if not client:
                        results[account.phone] = {
                            "error": "Не удалось подключиться к аккаунту"
                        }
                        continue

                    if not await client.is_user_authorized():
                        results[account.phone] = {
                            "error": "Требуется повторная авторизация"
                        }
                        continue

                    me = await client.get_me()
                    if me:
                        results[account.phone] = {
                            "success": True,
                            "username": me.username
                        }
                        account.is_active = True
                        account.restrictions = None
                    else:
                        results[account.phone] = {
                            "error": "Не удалось получить информацию о пользователе"
                        }
                        
                    self.db.update_account(account)

                except Exception as e:
                    results[account.phone] = {"error": str(e)}
                    self.logger.error(f"Ошибка при проверке аккаунта {account.phone}: {str(e)}")

        except Exception as e:
            self.logger.error(f"Ошибка при проверке аккаунтов: {str(e)}")
            
        return results

    async def cleanup(self) -> None:
        """Закрытие всех соединений"""
        try:
            async with self._lock:
                for client in self.clients.values():
                    try:
                        if client and client.is_connected():
                            await client.disconnect()
                    except Exception as e:
                        self.logger.error(f"Ошибка при отключении клиента: {str(e)}")
                self.clients.clear()
        except Exception as e:
            self.logger.error(f"Ошибка при очистке менеджера аккаунтов: {str(e)}")

    def get_client_by_phone(self, phone: str) -> Optional[TelegramClient]:
        """Получение клиента по номеру телефона"""
        if phone in self.active_accounts:
            return self.active_accounts[phone]['client']
        return None

    async def check_account_restrictions(self, phone: str) -> Dict[str, bool]:
        """Проверка ограничений конкретного аккаунта"""
        try:
            if phone not in self.active_accounts:
                return {"error": "Аккаунт не найден или не активен"}

            account_data = self.active_accounts[phone]
            client = account_data['client']
            account = account_data['account']

            if not await client.is_user_authorized():
                return {"error": "Аккаунт не авторизован"}

            restrictions = await self.api_checker.check_api(
                account.api_id,
                account.api_hash,
                account.phone
            )

            # Обновляем информацию в базе
            account.restrictions = restrictions
            self.db.update_account(account)

            return restrictions

        except Exception as e:
            error_msg = f"Ошибка при проверке ограничений: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

    async def deactivate_account(self, phone: str) -> bool:
        """Деактивация аккаунта"""
        try:
            if phone in self.active_accounts:
                account = self.active_accounts[phone]['account']
                account.is_active = False
                self.db.update_account(account)
                await self.session_manager.close_session(phone)
                del self.active_accounts[phone]
                self.logger.info(f"Аккаунт {phone} деактивирован")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при деактивации аккаунта {phone}: {str(e)}")
            return False 
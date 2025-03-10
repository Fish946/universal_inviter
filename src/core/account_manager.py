from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
from telethon.errors import *

from ..utils.database import Database, Account
from .session_manager import SessionManager
from .api_checker import APIChecker

class AccountManager:
    def __init__(self, db_path: str, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger('UniversalInviter')
        self.db = Database(db_path)
        self.session_manager = SessionManager(logger)
        self.api_checker = APIChecker(logger)
        self.active_accounts: Dict[str, Account] = {}

    async def add_account(self, phone: str, api_id: str, api_hash: str) -> Tuple[bool, str]:
        """Добавление нового аккаунта"""
        try:
            # Проверяем, не существует ли уже такой аккаунт
            existing_accounts = self.db.get_all_accounts()
            if any(acc.phone == phone for acc in existing_accounts):
                return False, "Аккаунт с таким номером уже существует"

            # Проверяем API и ограничения
            check_results = await self.api_checker.check_api(api_id, api_hash, phone)
            
            if check_results.get("error"):
                return False, check_results["error"]

            # Создаем сессию
            session_string = await self.session_manager.create_session(phone, api_id, api_hash)
            if not session_string:
                return False, "Не удалось создать сессию"

            # Создаем новый аккаунт
            account = Account(
                id=None,  # ID будет назначен базой данных
                phone=phone,
                api_id=api_id,
                api_hash=api_hash,
                session_string=session_string,
                is_active=True,
                restrictions=check_results
            )

            # Сохраняем в базу
            account_id = self.db.add_account(account)
            account.id = account_id
            self.active_accounts[phone] = account

            self.logger.info(f"Аккаунт {phone} успешно добавлен")
            return True, "Аккаунт успешно добавлен"

        except Exception as e:
            error_msg = f"Ошибка при добавлении аккаунта: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    async def load_accounts(self) -> Tuple[int, int]:
        """Загрузка всех аккаунтов из базы и проверка их состояния"""
        try:
            accounts = self.db.get_all_accounts()
            loaded_count = 0
            failed_count = 0

            for account in accounts:
                try:
                    # Пробуем загрузить сессию
                    session_loaded = await self.session_manager.load_session(
                        account.phone,
                        account.api_id,
                        account.api_hash,
                        account.session_string
                    )

                    if session_loaded:
                        self.active_accounts[account.phone] = account
                        loaded_count += 1
                        self.logger.info(f"Аккаунт {account.phone} успешно загружен")
                    else:
                        failed_count += 1
                        self.logger.warning(f"Не удалось загрузить аккаунт {account.phone}")

                except Exception as e:
                    failed_count += 1
                    self.logger.error(f"Ошибка при загрузке аккаунта {account.phone}: {str(e)}")

            return loaded_count, failed_count

        except Exception as e:
            self.logger.error(f"Ошибка при загрузке аккаунтов: {str(e)}")
            return 0, 0

    async def check_account_restrictions(self, phone: str) -> Dict[str, bool]:
        """Проверка ограничений конкретного аккаунта"""
        try:
            account = self.active_accounts.get(phone)
            if not account:
                return {"error": "Аккаунт не найден"}

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

    async def check_all_accounts(self) -> Dict[str, Dict[str, bool]]:
        """Проверка ограничений всех аккаунтов"""
        results = {}
        for phone in self.active_accounts:
            results[phone] = await self.check_account_restrictions(phone)
        return results

    async def deactivate_account(self, phone: str) -> bool:
        """Деактивация аккаунта"""
        try:
            if phone in self.active_accounts:
                account = self.active_accounts[phone]
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

    async def cleanup(self):
        """Очистка ресурсов при завершении работы"""
        try:
            await self.session_manager.close_all_sessions()
            self.session_manager.cleanup_session_files()
        except Exception as e:
            self.logger.error(f"Ошибка при очистке ресурсов: {str(e)}") 
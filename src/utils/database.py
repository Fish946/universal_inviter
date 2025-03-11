import sqlite3
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
import json

@dataclass
class Account:
    id: Optional[int]
    phone: str
    api_id: str
    api_hash: str
    session_string: Optional[str] = None
    is_active: bool = True
    restrictions: Optional[str] = None

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger('UniversalInviter')
        self.init_db()

    def init_db(self):
        """Инициализация базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS accounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        phone TEXT UNIQUE NOT NULL,
                        api_id TEXT NOT NULL,
                        api_hash TEXT NOT NULL,
                        session_string TEXT,
                        is_active BOOLEAN NOT NULL DEFAULT 1,
                        restrictions TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                self.logger.info("База данных успешно инициализирована")
        except Exception as e:
            self.logger.error(f"Ошибка при инициализации базы данных: {str(e)}")
            raise

    def add_account(self, account: Account) -> int:
        """Добавление или обновление аккаунта в базе данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Проверяем существование аккаунта
                cursor.execute('SELECT id FROM accounts WHERE phone = ?', (account.phone,))
                existing = cursor.fetchone()
                
                if existing:
                    # Обновляем существующий аккаунт
                    cursor.execute('''
                        UPDATE accounts 
                        SET api_id = ?, api_hash = ?, session_string = ?, is_active = ?, restrictions = ?
                        WHERE phone = ?
                    ''', (account.api_id, account.api_hash, account.session_string,
                          account.is_active, json.dumps(account.restrictions) if account.restrictions else None,
                          account.phone))
                    conn.commit()
                    self.logger.info(f"Аккаунт {account.phone} успешно обновлен")
                    return existing[0]
                else:
                    # Добавляем новый аккаунт
                    cursor.execute('''
                        INSERT INTO accounts (phone, api_id, api_hash, session_string, is_active, restrictions)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (account.phone, account.api_id, account.api_hash, 
                          account.session_string, account.is_active,
                          json.dumps(account.restrictions) if account.restrictions else None))
                    conn.commit()
                    account_id = cursor.lastrowid
                    self.logger.info(f"Аккаунт {account.phone} успешно добавлен")
                    return account_id
                
        except sqlite3.IntegrityError as e:
            self.logger.error(f"Ошибка уникальности данных: {str(e)}")
            raise Exception(f"Аккаунт с номером {account.phone} уже существует")
        except Exception as e:
            self.logger.error(f"Ошибка при работе с базой данных: {str(e)}")
            raise

    def get_all_accounts(self) -> List[Account]:
        """Получение всех аккаунтов из базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM accounts ORDER BY created_at DESC')
                rows = cursor.fetchall()
                
                if not rows:
                    self.logger.info("В базе данных нет аккаунтов")
                    return []
                
                accounts = []
                for row in rows:
                    try:
                        restrictions = None
                        if row['restrictions']:
                            try:
                                restrictions = json.loads(row['restrictions'])
                            except json.JSONDecodeError:
                                self.logger.warning(f"Некорректный формат ограничений для аккаунта {row['phone']}")
                        
                        account = Account(
                            id=row['id'],
                            phone=row['phone'],
                            api_id=row['api_id'],
                            api_hash=row['api_hash'],
                            session_string=row['session_string'],
                            is_active=bool(row['is_active']),
                            restrictions=restrictions
                        )
                        accounts.append(account)
                    except Exception as e:
                        self.logger.error(f"Ошибка при обработке аккаунта {row['phone']}: {str(e)}")
                
                self.logger.info(f"Получено {len(accounts)} аккаунтов из базы данных")
                return accounts
                
        except sqlite3.Error as e:
            error_msg = f"Ошибка SQLite при получении списка аккаунтов: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Неожиданная ошибка при получении списка аккаунтов: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def update_account(self, account: Account) -> bool:
        """Обновление данных аккаунта"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE accounts 
                    SET session_string = ?, is_active = ?, restrictions = ?
                    WHERE id = ?
                ''', (account.session_string, account.is_active,
                      json.dumps(account.restrictions) if account.restrictions else None,
                      account.id))
                conn.commit()
                self.logger.info(f"Аккаунт {account.phone} успешно обновлен")
                return True
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении аккаунта {account.phone}: {str(e)}")
            return False

    def delete_account(self, account_id: int) -> bool:
        """Удаление аккаунта"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
                conn.commit()
                self.logger.info(f"Аккаунт с ID {account_id} успешно удален")
                return True
        except Exception as e:
            self.logger.error(f"Ошибка при удалении аккаунта {account_id}: {str(e)}")
            return False 
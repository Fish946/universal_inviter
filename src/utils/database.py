import sqlite3
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
        self.init_db()

    def init_db(self):
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

    def add_account(self, account: Account) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO accounts (phone, api_id, api_hash, session_string, is_active, restrictions)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (account.phone, account.api_id, account.api_hash, 
                 account.session_string, account.is_active,
                 json.dumps(account.restrictions) if account.restrictions else None))
            conn.commit()
            return cursor.lastrowid

    def get_all_accounts(self) -> List[Account]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM accounts')
            rows = cursor.fetchall()
            return [Account(
                id=row['id'],
                phone=row['phone'],
                api_id=row['api_id'],
                api_hash=row['api_hash'],
                session_string=row['session_string'],
                is_active=bool(row['is_active']),
                restrictions=json.loads(row['restrictions']) if row['restrictions'] else None
            ) for row in rows]

    def update_account(self, account: Account):
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
import json
import os
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Config:
    db_path: str
    logs_path: str
    default_delays: Dict[str, int]
    language: str = "ru"

    @classmethod
    def load(cls, config_path: str = "config.json") -> 'Config':
        if not os.path.exists(config_path):
            # Создаем конфиг по умолчанию
            config = {
                "db_path": "data/accounts.db",
                "logs_path": "data/logs",
                "language": "ru",
                "default_delays": {
                    "between_adds": 180,  # 3 минуты между добавлениями
                    "error_delay": 60,    # 1 минута при ошибке
                    "check_delay": 5      # 5 секунд между проверками
                }
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return cls(**data)

    def save(self, config_path: str = "config.json"):
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, indent=4, ensure_ascii=False)
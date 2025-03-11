import json
import os
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Config:
    """Конфигурация приложения"""
    
    def __init__(self):
        self.db_path = "inviter.db"
        self.sessions_dir = "sessions"
        self.logs_dir = "logs"
        
        # Создаем необходимые директории
        for directory in [self.sessions_dir, self.logs_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    @classmethod
    def load(cls, config_path: str = "config.json") -> 'Config':
        """Загрузка конфигурации из файла"""
        config = cls()
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                config.db_path = data.get('db_path', config.db_path)
                config.sessions_dir = data.get('sessions_dir', config.sessions_dir)
                config.logs_dir = data.get('logs_dir', config.logs_dir)
                    
            except Exception as e:
                print(f"Ошибка при загрузке конфигурации: {str(e)}")
                
        return config
        
    def save(self, config_path: str = "config.json") -> None:
        """Сохранение конфигурации в файл"""
        try:
            data = {
                'db_path': self.db_path,
                'sessions_dir': self.sessions_dir,
                'logs_dir': self.logs_dir
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            print(f"Ошибка при сохранении конфигурации: {str(e)}")
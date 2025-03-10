import os
import json
import csv
from typing import List, Dict, Optional
import logging

class FileHandler:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger('UniversalInviter')

    def read_user_list(self, file_path: str) -> List[str]:
        """Чтение списка пользователей из файла"""
        users = []
        try:
            extension = os.path.splitext(file_path)[1].lower()
            
            if extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    users = [line.strip() for line in f if line.strip()]
                    
            elif extension == '.csv':
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    users = [row[0].strip() for row in reader if row and row[0].strip()]
                    
            elif extension == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        users = [str(user).strip() for user in data if user]
                    elif isinstance(data, dict) and 'users' in data:
                        users = [str(user).strip() for user in data['users'] if user]
            
            # Удаляем дубликаты и пустые строки
            users = list(set(filter(None, users)))
            
            return users
            
        except Exception as e:
            self.logger.error(f"Ошибка при чтении файла {file_path}: {str(e)}")
            return []

    def save_progress(self, task_id: str, progress: Dict) -> bool:
        """Сохранение прогресса в файл"""
        try:
            os.makedirs('data/progress', exist_ok=True)
            file_path = f'data/progress/{task_id}.json'
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=4)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении прогресса: {str(e)}")
            return False

    def load_progress(self, task_id: str) -> Optional[Dict]:
        """Загрузка прогресса из файла"""
        try:
            file_path = f'data/progress/{task_id}.json'
            if not os.path.exists(file_path):
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке прогресса: {str(e)}")
            return None

    def cleanup_old_files(self, days: int = 7):
        """Очистка старых файлов прогресса"""
        try:
            current_time = time.time()
            progress_dir = 'data/progress'
            
            if not os.path.exists(progress_dir):
                return
                
            for file_name in os.listdir(progress_dir):
                file_path = os.path.join(progress_dir, file_name)
                if os.path.getmtime(file_path) < current_time - (days * 86400):
                    os.remove(file_path)
                    self.logger.info(f"Удален старый файл прогресса: {file_name}")
                    
        except Exception as e:
            self.logger.error(f"Ошибка при очистке старых файлов: {str(e)}")
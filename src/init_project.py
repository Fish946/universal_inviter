import os
import sys
from pathlib import Path

def init_project():
    """Инициализация структуры проекта"""
    # Создаем необходимые директории
    directories = [
        'data',
        'data/logs',
        'data/sessions',
        'data/progress'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Структура проекта создана")

if __name__ == "__main__":
    init_project() 
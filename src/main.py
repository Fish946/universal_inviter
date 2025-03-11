import sys
import asyncio
import qasync
from PyQt6.QtWidgets import QApplication

from core.di.container import Container
from ui.main_window import MainWindow
from utils.config import Config

def main():
    """Точка входа в приложение"""
    try:
        # Инициализация конфигурации
        config = Config()
        
        # Инициализация контейнера зависимостей
        container = Container(config)
        
        # Создание и настройка приложения
        app = qasync.QApplication(sys.argv)
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        # Создание главного окна
        window = MainWindow(container)
        window.show()
        
        # Запуск приложения
        with loop:
            sys.exit(loop.run_forever())
            
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
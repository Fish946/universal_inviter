import sys
import asyncio
import qasync
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.config import Config
from src.utils.logger import setup_logger

def main():
    # Загружаем конфигурацию
    config = Config.load()

    # Инициализируем логгер
    logger = setup_logger()

    # Создаем приложение
    app = QApplication(sys.argv)
    
    # Создаем главное окно
    window = MainWindow(config, logger)
    window.show()

    # Создаем и запускаем event loop
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Запускаем приложение
    with loop:
        loop.run_forever()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        sys.exit(1)
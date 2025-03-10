import sys
import asyncio
import qasync
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.config import Config
from utils.logger import setup_logger

async def main():
    # Загружаем конфигурацию
    config = Config.load()

    # Инициализируем логгер
    logger = setup_logger()

    # Создаем приложение
    app = QApplication(sys.argv)
    
    # Создаем главное окно
    window = MainWindow(config, logger)
    window.show()

    # Запускаем event loop
    await qasync.QEventLoop(app).exec_()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        sys.exit(1) 
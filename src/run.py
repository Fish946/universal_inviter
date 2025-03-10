import os
import sys
import logging
from pathlib import Path

def setup_environment():
    """Настройка окружения для production"""
    # Устанавливаем корректные пути
    base_dir = Path(__file__).parent.parent
    os.chdir(base_dir)
    
    # Добавляем путь к модулям в PYTHONPATH
    sys.path.insert(0, str(base_dir))
    
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data/logs/production.log'),
            logging.StreamHandler()
        ]
    )

if __name__ == "__main__":
    try:
        setup_environment()
        from src.main import main
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        logging.exception("Критическая ошибка при запуске")
        sys.exit(1) 
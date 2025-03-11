import sys
import asyncio
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
import qasync

from core.di.container import Container
from ui.widgets.account_tab import AccountTab
from ui.widgets.inviter_tab import InviterTab
from ui.widgets.settings_tab import SettingsTab

class MainWindow(QMainWindow):
    def __init__(self, container: Container):
        super().__init__()
        
        self.container = container
        self.logger = container.logger
        
        # Настройка главного окна
        self.setWindowTitle("Universal Inviter")
        self.setMinimumSize(800, 600)
        
        # Создание и настройка центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создание вертикального layout
        layout = QVBoxLayout(central_widget)
        
        # Создание и настройка вкладок
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                background: #2b2b2b;
            }
            QTabBar::tab {
                background: #1e1e1e;
                color: #fff;
                padding: 8px 12px;
                border: 1px solid #444;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #2b2b2b;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background: #333;
            }
        """)
        
        # Создание вкладок
        self.account_tab = AccountTab(container)
        self.inviter_tab = InviterTab(container)
        self.settings_tab = SettingsTab(container)
        
        # Добавление вкладок
        self.tabs.addTab(self.account_tab, "Аккаунты")
        self.tabs.addTab(self.inviter_tab, "Инвайтинг")
        self.tabs.addTab(self.settings_tab, "Настройки")
        
        # Добавление вкладок в layout
        layout.addWidget(self.tabs)
        
        # Подключение сигналов
        self.account_tab.account_added.connect(self.on_account_added)
        
        # Запуск асинхронной загрузки аккаунтов
        asyncio.create_task(self.load_accounts())

    async def load_accounts(self):
        """Загрузка аккаунтов при старте приложения"""
        try:
            await self.container.account_manager.load_accounts()
            await self.account_tab.update_accounts_list()
            self.logger.info("Аккаунты успешно загружены")
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке аккаунтов: {str(e)}")
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить аккаунты: {str(e)}"
            )

    def on_account_added(self):
        """Обработчик добавления нового аккаунта"""
        asyncio.create_task(self.account_tab.update_accounts_list())
        self.logger.info("Список аккаунтов обновлен")

    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        try:
            asyncio.create_task(self.container.account_manager.cleanup())
            self.logger.info("Приложение успешно завершено")
            event.accept()
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии приложения: {str(e)}")
            event.accept()

def main():
    """Точка входа в приложение"""
    try:
        app = qasync.QApplication(sys.argv)
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        container = Container()
        window = MainWindow(container)
        window.show()
        
        with loop:
            sys.exit(loop.run_forever())
            
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
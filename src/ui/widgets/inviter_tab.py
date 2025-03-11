from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QLineEdit, QTextEdit,
                           QProgressBar, QFileDialog, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt
import qasync
from datetime import datetime

from ui.styles import Styles, Colors
from ui.threads.invite_thread import InviteThread
from utils.file_handler import FileHandler

class InviterTab(QWidget):
    def __init__(self, account_manager, logger, config):
        super().__init__()
        self.account_manager = account_manager
        self.logger = logger
        self.config = config
        self.file_handler = FileHandler(logger)
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса вкладки инвайтинга"""
        layout = QVBoxLayout(self)

        # Выбор аккаунта
        account_group = QWidget()
        account_layout = QHBoxLayout(account_group)
        
        self.account_combo = QComboBox()
        self.account_combo.setStyleSheet(Styles.INPUT)
        
        account_layout.addWidget(QLabel("Аккаунт:"))
        account_layout.addWidget(self.account_combo)

        # Выбор канала
        channel_group = QWidget()
        channel_layout = QHBoxLayout(channel_group)
        
        self.channel_input = QLineEdit()
        self.channel_input.setPlaceholderText("Username канала (@channel)")
        self.channel_input.setStyleSheet(Styles.INPUT)
        
        channel_layout.addWidget(QLabel("Канал:"))
        channel_layout.addWidget(self.channel_input)

        # Настройки инвайтинга
        invite_settings_group = QWidget()
        invite_settings_layout = QHBoxLayout(invite_settings_group)
        
        self.invite_count_input = QLineEdit()
        self.invite_count_input.setPlaceholderText("Количество приглашений (0 - все)")
        self.invite_count_input.setStyleSheet(Styles.INPUT)
        
        invite_settings_layout.addWidget(QLabel("Количество приглашений:"))
        invite_settings_layout.addWidget(self.invite_count_input)

        # Выбор файла со списком пользователей
        file_group = QWidget()
        file_layout = QHBoxLayout(file_group)
        
        self.file_path_label = QLineEdit()
        self.file_path_label.setReadOnly(True)
        self.file_path_label.setStyleSheet(Styles.INPUT)
        
        select_file_btn = QPushButton("Выбрать файл")
        select_file_btn.setStyleSheet(Styles.BUTTON)
        select_file_btn.clicked.connect(self.select_user_file)
        
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(select_file_btn)

        # Прогресс
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)

        # Кнопки управления
        control_group = QWidget()
        control_layout = QHBoxLayout(control_group)
        
        self.start_btn = QPushButton("Начать")
        self.start_btn.setStyleSheet(Styles.BUTTON)
        self.start_btn.clicked.connect(self.start_inviting)
        
        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.setStyleSheet(Styles.BUTTON)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_inviting)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)

        # Лог операций
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet(Styles.LOG_VIEW)

        # Добавление всех элементов на вкладку
        layout.addWidget(account_group)
        layout.addWidget(channel_group)
        layout.addWidget(invite_settings_group)
        layout.addWidget(file_group)
        layout.addWidget(self.progress_bar)
        layout.addWidget(control_group)
        layout.addWidget(QLabel("Лог операций:"))
        layout.addWidget(self.log_view)

    def select_user_file(self):
        """Выбор файла со списком пользователей"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл со списком пользователей",
            "",
            "Text files (*.txt);;CSV files (*.csv);;JSON files (*.json)"
        )

        if file_path:
            self.file_path_label.setText(file_path)
            users = self.file_handler.read_user_list(file_path)
            self.log_message(f"Загружено {len(users)} пользователей из файла", Colors.INFO)

    @qasync.asyncSlot()
    async def start_inviting(self):
        """Начало процесса приглашения пользователей"""
        try:
            # Получаем выбранный аккаунт
            current_index = self.account_combo.currentIndex()
            if current_index == -1:
                QMessageBox.warning(self, "Ошибка", "Выберите аккаунт для работы")
                return

            selected_account = self.account_combo.itemData(current_index)
            if not selected_account:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить данные аккаунта")
                return
            
            channel = self.channel_input.text().strip()
            file_path = self.file_path_label.text().strip()
            invite_count = self.invite_count_input.text().strip()

            # Валидация
            if not channel:
                QMessageBox.warning(self, "Ошибка", "Укажите канал")
                return

            if not file_path:
                QMessageBox.warning(self, "Ошибка", "Выберите файл со списком пользователей")
                return

            # Загружаем список пользователей
            users = self.file_handler.read_user_list(file_path)
            if not users:
                QMessageBox.warning(self, "Ошибка", "Список пользователей пуст")
                return

            # Ограничиваем количество пользователей если указано
            if invite_count and invite_count.isdigit():
                count = int(invite_count)
                if count > 0:
                    users = users[:count]

            # Создаем задачу
            task_id = f"invite_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.current_task_id = task_id

            # Обновляем UI
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.progress_bar.setMaximum(len(users))
            self.progress_bar.setValue(0)

            # Запускаем в отдельном потоке
            self.invite_thread = InviteThread(
                self.account_manager,
                self.logger,
                selected_account,
                channel,
                users,
                task_id
            )
            self.invite_thread.progress_updated.connect(self.update_invite_progress)
            self.invite_thread.finished.connect(self.on_invite_finished)
            self.invite_thread.start()

            self.log_message(f"Начат процесс приглашения пользователей в канал {channel}", Colors.INFO)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при запуске: {str(e)}")
            self.reset_invite_ui()

    def stop_inviting(self):
        """Остановка процесса приглашения"""
        if hasattr(self, 'current_task_id'):
            if hasattr(self, 'invite_thread') and self.invite_thread:
                self.invite_thread.invite_service.stop_inviting(self.current_task_id)
            self.log_message("Останавливаем процесс приглашения...", Colors.WARNING)
            self.stop_btn.setEnabled(False)

    def update_invite_progress(self, progress_data):
        """Обновление прогресса приглашения"""
        invited = progress_data.get('invited', 0)
        failed = progress_data.get('failed', 0)
        skipped = progress_data.get('skipped', 0)
        total = progress_data.get('total', 0)
        current_user = progress_data.get('current_user', '')

        self.progress_bar.setValue(invited + failed + skipped)
        
        # Формируем подробный отчет
        status_text = (
            f"📊 Прогресс: {invited + failed + skipped}/{total}\n"
            f"✅ Успешно приглашено: {invited}\n"
            f"❌ Ошибок: {failed}\n"
            f"⚠️ Пропущено: {skipped}\n"
        )
        
        if current_user:
            status_text += f"👤 Текущий пользователь: {current_user}"
        
        self.log_message(status_text, Colors.INFO)

    def on_invite_finished(self):
        """Обработка завершения процесса приглашения"""
        self.reset_invite_ui()
        self.log_message("Процесс приглашения завершен", Colors.SUCCESS)

    def reset_invite_ui(self):
        """Сброс UI после завершения приглашения"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(0)

    def log_message(self, message: str, color: str):
        """Добавление сообщения в лог"""
        self.log_view.append(f'<span style="color: {color}">{message}</span>')

    async def update_accounts_combo(self):
        """Обновление списка аккаунтов в комбобоксе"""
        try:
            accounts = self.account_manager.db.get_all_accounts()
            self.account_combo.clear()
            
            for account in accounts:
                self.account_combo.addItem(f"{account.phone} (API ID: {account.api_id})", account)
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении списка аккаунтов: {str(e)}") 
from PyQt6.QtWidgets import QDialog
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QLineEdit, QTextEdit, QTabWidget,
                           QFileDialog, QMessageBox, QProgressBar, QScrollArea,
                           QGridLayout, QDialog)  # добавили QGridLayout и QDialog
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QIcon

from src.ui.styles import Colors, Styles, Fonts
from src.core.account_manager import AccountManager
from src.core.inviter import Inviter
from src.utils.validators import Validators
from src.utils.file_handler import FileHandler

class MainWindow(QMainWindow):
    def __init__(self, config, logger):
        super().__init__()
        self.config = config
        self.logger = logger
        self.account_manager = AccountManager(config.db_path, logger)
        self.file_handler = FileHandler(logger)
        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle('Universal Inviter')
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(Styles.MAIN_WINDOW)

        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Создание вкладок
        tabs = QTabWidget()
        tabs.addTab(self.create_accounts_tab(), "Аккаунты")
        tabs.addTab(self.create_inviter_tab(), "Инвайтинг")
        tabs.addTab(self.create_settings_tab(), "Настройки")
        
        main_layout.addWidget(tabs)

    def create_accounts_tab(self):
        """Создание вкладки управления аккаунтами"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Форма добавления аккаунта
        form_group = QWidget()
        form_layout = QGridLayout(form_group)

        # Поля ввода
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Номер телефона (+7...)")
        self.phone_input.setStyleSheet(Styles.INPUT)

        self.api_id_input = QLineEdit()
        self.api_id_input.setPlaceholderText("API ID")
        self.api_id_input.setStyleSheet(Styles.INPUT)

        self.api_hash_input = QLineEdit()
        self.api_hash_input.setPlaceholderText("API Hash")
        self.api_hash_input.setStyleSheet(Styles.INPUT)

        # Кнопки
        add_account_btn = QPushButton("Добавить аккаунт")
        add_account_btn.setStyleSheet(Styles.BUTTON)
        add_account_btn.clicked.connect(self.add_account)

        check_accounts_btn = QPushButton("Проверить все аккаунты")
        check_accounts_btn.setStyleSheet(Styles.BUTTON)
        check_accounts_btn.clicked.connect(self.check_all_accounts)

        # Добавление элементов в форму
        form_layout.addWidget(QLabel("Номер телефона:"), 0, 0)
        form_layout.addWidget(self.phone_input, 0, 1)
        form_layout.addWidget(QLabel("API ID:"), 1, 0)
        form_layout.addWidget(self.api_id_input, 1, 1)
        form_layout.addWidget(QLabel("API Hash:"), 2, 0)
        form_layout.addWidget(self.api_hash_input, 2, 1)
        form_layout.addWidget(add_account_btn, 3, 0, 1, 2)
        form_layout.addWidget(check_accounts_btn, 4, 0, 1, 2)

        # Список аккаунтов
        self.accounts_list = QTextEdit()
        self.accounts_list.setReadOnly(True)
        self.accounts_list.setStyleSheet(Styles.LOG_VIEW)

        # Добавление всех элементов на вкладку
        layout.addWidget(form_group)
        layout.addWidget(QLabel("Список аккаунтов:"))
        layout.addWidget(self.accounts_list)

        return tab

    def create_inviter_tab(self):
        """Создание вкладки инвайтинга"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Выбор канала
        channel_group = QWidget()
        channel_layout = QHBoxLayout(channel_group)
        
        self.channel_input = QLineEdit()
        self.channel_input.setPlaceholderText("Username канала (@channel)")
        self.channel_input.setStyleSheet(Styles.INPUT)
        
        channel_layout.addWidget(QLabel("Канал:"))
        channel_layout.addWidget(self.channel_input)

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
        layout.addWidget(channel_group)
        layout.addWidget(file_group)
        layout.addWidget(self.progress_bar)
        layout.addWidget(control_group)
        layout.addWidget(QLabel("Лог операций:"))
        layout.addWidget(self.log_view)

        return tab

    def create_settings_tab(self):
        """Создание вкладки настроек"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Настройки задержек
        delays_group = QWidget()
        delays_layout = QGridLayout(delays_group)
        
        self.between_adds_input = QLineEdit(str(self.config.default_delays['between_adds']))
        self.error_delay_input = QLineEdit(str(self.config.default_delays['error_delay']))
        self.check_delay_input = QLineEdit(str(self.config.default_delays['check_delay']))
        
        delays_layout.addWidget(QLabel("Задержка между добавлениями (сек):"), 0, 0)
        delays_layout.addWidget(self.between_adds_input, 0, 1)
        delays_layout.addWidget(QLabel("Задержка при ошибке (сек):"), 1, 0)
        delays_layout.addWidget(self.error_delay_input, 1, 1)
        delays_layout.addWidget(QLabel("Задержка между проверками (сек):"), 2, 0)
        delays_layout.addWidget(self.check_delay_input, 2, 1)

        # Кнопка сохранения настроек
        save_settings_btn = QPushButton("Сохранить настройки")
        save_settings_btn.setStyleSheet(Styles.BUTTON)
        save_settings_btn.clicked.connect(self.save_settings)

        # Добавление всех элементов на вкладку
        layout.addWidget(delays_group)
        layout.addWidget(save_settings_btn)
        layout.addStretch()

        return tab

    async def add_account(self):
        """Добавление нового аккаунта"""
        phone = self.phone_input.text().strip()
        api_id = self.api_id_input.text().strip()
        api_hash = self.api_hash_input.text().strip()

        # Валидация входных данных
        validators = Validators()
        validations = [
            validators.validate_phone(phone),
            validators.validate_api_id(api_id),
            validators.validate_api_hash(api_hash)
        ]

        for is_valid, error_msg in validations:
            if not is_valid:
                QMessageBox.warning(self, "Ошибка", error_msg)
                return

        try:
            # Передаем колбэки для обработки кодов
            success, message = await self.account_manager.add_account(
                phone, 
                api_id, 
                api_hash,
                code_callback=self.show_code_dialog,
                password_callback=self.show_2fa_dialog
            )
            
            if success:
                QMessageBox.information(self, "Успех", "Аккаунт успешно добавлен")
                self.clear_account_inputs()
                await self.update_accounts_list()
            else:
                QMessageBox.warning(self, "Ошибка", message)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    async def check_all_accounts(self):
        """Проверка всех аккаунтов"""
        try:
            self.log_message("Начинаем проверку всех аккаунтов...", Colors.INFO)
            results = await self.account_manager.check_all_accounts()
            
            for phone, status in results.items():
                if status.get("error"):
                    self.log_message(f"Аккаунт {phone}: {status['error']}", Colors.ERROR)
                else:
                    self.log_message(
                        f"Аккаунт {phone}: Активен, может приглашать пользователей", 
                        Colors.SUCCESS
                    )

            await self.update_accounts_list()

        except Exception as e:
            self.log_message(f"Ошибка при проверке аккаунтов: {str(e)}", Colors.ERROR)

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

    async def start_inviting(self):
        """Начало процесса приглашения пользователей"""
        channel = self.channel_input.text().strip()
        file_path = self.file_path_label.text().strip()

        # Валидация
        if not channel:
            QMessageBox.warning(self, "Ошибка", "Укажите канал")
            return

        if not file_path:
            QMessageBox.warning(self, "Ошибка", "Выберите файл со списком пользователей")
            return

        try:
            # Загружаем список пользователей
            users = self.file_handler.read_user_list(file_path)
            if not users:
                QMessageBox.warning(self, "Ошибка", "Список пользователей пуст")
                return

            # Создаем задачу
            task_id = f"invite_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.current_task_id = task_id

            # Обновляем UI
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.progress_bar.setMaximum(len(users))
            self.progress_bar.setValue(0)

            # Запускаем процесс приглашения
            self.inviter = Inviter(self.logger)
            self.inviter.set_delays(self.get_current_delays())

            # Запускаем в отдельном потоке
            self.invite_thread = InviteThread(
                self.inviter,
                self.account_manager.get_active_client(),
                channel,
                users,
                task_id
            )
            self.invite_thread.progress_updated.connect(self.update_invite_progress)
            self.invite_thread.finished.connect(self.on_invite_finished)
            self.invite_thread.start()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при запуске: {str(e)}")
            self.reset_invite_ui()

    def stop_inviting(self):
        """Остановка процесса приглашения"""
        if hasattr(self, 'current_task_id'):
            self.inviter.stop_inviting(self.current_task_id)
            self.log_message("Останавливаем процесс приглашения...", Colors.WARNING)
            self.stop_btn.setEnabled(False)

    def update_invite_progress(self, progress_data):
        """Обновление прогресса приглашения"""
        invited = progress_data.get('invited', 0)
        failed = progress_data.get('failed', 0)
        skipped = progress_data.get('skipped', 0)
        total = progress_data.get('total', 0)

        self.progress_bar.setValue(invited + failed + skipped)
        self.log_message(
            f"Прогресс: {invited} приглашено, {failed} ошибок, {skipped} пропущено",
            Colors.INFO
        )

    def on_invite_finished(self):
        """Обработка завершения процесса приглашения"""
        self.reset_invite_ui()
        self.log_message("Процесс приглашения завершен", Colors.SUCCESS)

    def reset_invite_ui(self):
        """Сброс UI после завершения приглашения"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(0)

    def save_settings(self):
        """Сохранение настроек"""
        try:
            new_delays = self.get_current_delays()
            self.config.default_delays.update(new_delays)
            self.config.save()
            QMessageBox.information(self, "Успех", "Настройки успешно сохранены")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении настроек: {str(e)}")

    def get_current_delays(self) -> dict:
        """Получение текущих значений задержек"""
        return {
            'between_adds': int(self.between_adds_input.text()),
            'error_delay': int(self.error_delay_input.text()),
            'check_delay': int(self.check_delay_input.text())
        }

    def log_message(self, message: str, color: str):
        """Добавление сообщения в лог с цветом"""
        self.log_view.append(f'<span style="color: {color}">{message}</span>')

    def clear_account_inputs(self):
        """Очистка полей ввода аккаунта"""
        self.phone_input.clear()
        self.api_id_input.clear()
        self.api_hash_input.clear()

    async def update_accounts_list(self):
        """Обновление списка аккаунтов"""
        accounts = await self.account_manager.get_all_accounts()
        self.accounts_list.clear()
        
        for account in accounts:
            status = "🟢 Активен" if account.is_active else "🔴 Неактивен"
            self.accounts_list.append(
                f"📱 {account.phone} | {status}\n"
                f"API ID: {account.api_id}\n"
                f"Ограничения: {account.restrictions or 'нет'}\n"
                f"{'─' * 40}"
            )

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        try:
            # Останавливаем все активные процессы
            if hasattr(self, 'current_task_id'):
                self.inviter.stop_inviting(self.current_task_id)

            # Закрываем все сессии
            asyncio.run(self.account_manager.cleanup())
            
            # Очищаем временные файлы
            self.file_handler.cleanup_old_files()
            
            event.accept()
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии приложения: {str(e)}")
            event.accept()

    def show_code_dialog(self):
        """Показывает диалог для ввода кода подтверждения"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Подтверждение")
        layout = QVBoxLayout()

        # Поле для ввода кода
        code_input = QLineEdit()
        code_input.setPlaceholderText("Введите код из сообщения")
        code_input.setStyleSheet(Styles.INPUT)

        # Кнопки
        buttons = QHBoxLayout()
        ok_button = QPushButton("Подтвердить")
        cancel_button = QPushButton("Отмена")
        ok_button.setStyleSheet(Styles.BUTTON)
        cancel_button.setStyleSheet(Styles.BUTTON)

        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)

        layout.addWidget(QLabel("Введите код, отправленный в Telegram:"))
        layout.addWidget(code_input)
        layout.addLayout(buttons)

        dialog.setLayout(layout)

        # Подключаем обработчики
        ok_button.clicked.connect(lambda: dialog.done(1))
        cancel_button.clicked.connect(lambda: dialog.done(0))

        if dialog.exec():
            return code_input.text()
        return None

    def show_2fa_dialog(self):
        """Показывает диалог для ввода пароля двухфакторной аутентификации"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Двухфакторная аутентификация")
        layout = QVBoxLayout()

        # Поле для ввода пароля
        password_input = QLineEdit()
        password_input.setPlaceholderText("Введите пароль двухфакторной аутентификации")
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_input.setStyleSheet(Styles.INPUT)

        # Кнопки
        buttons = QHBoxLayout()
        ok_button = QPushButton("Подтвердить")
        cancel_button = QPushButton("Отмена")
        ok_button.setStyleSheet(Styles.BUTTON)
        cancel_button.setStyleSheet(Styles.BUTTON)

        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)

        layout.addWidget(QLabel("Введите пароль двухфакторной аутентификации:"))
        layout.addWidget(password_input)
        layout.addLayout(buttons)

        dialog.setLayout(layout)

        # Подключаем обработчики
        ok_button.clicked.connect(lambda: dialog.done(1))
        cancel_button.clicked.connect(lambda: dialog.done(0))

        if dialog.exec():
            return password_input.text()
        return None

class InviteThread(QThread):
    """Поток для выполнения приглашений"""
    progress_updated = pyqtSignal(dict)

    def __init__(self, inviter, client, channel, users, task_id):
        super().__init__()
        self.inviter = inviter
        self.client = client
        self.channel = channel
        self.users = users
        self.task_id = task_id

    def run(self):
        """Запуск процесса приглашения"""
        asyncio.run(self.inviter.start_inviting(
            self.client,
            self.channel,
            self.users,
            self.task_id
        )) 
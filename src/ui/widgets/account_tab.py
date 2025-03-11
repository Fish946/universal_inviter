from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QLineEdit, QTextEdit,
                           QGridLayout, QMessageBox, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal
import qasync

from core.di.container import Container
from ui.dialogs.auth_dialogs import CodeVerificationDialog, TwoFactorAuthDialog
from ui.styles import Styles, Colors

class AccountTab(QWidget):
    account_added = pyqtSignal()  # Сигнал для оповещения о добавлении аккаунта
    
    def __init__(self, container: Container):
        super().__init__()
        self.container = container
        self.logger = container.logger
        self.auth_service = container.auth_service
        self.account_manager = container.account_manager
        self.init_ui()
        
        # Загружаем список аккаунтов при создании вкладки
        qasync.create_task(self.update_accounts_list())

    def init_ui(self):
        """Инициализация интерфейса вкладки аккаунтов"""
        layout = QVBoxLayout(self)

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

    @qasync.asyncSlot()
    async def add_account(self):
        """Добавление нового аккаунта"""
        try:
            phone = self.phone_input.text().strip()
            api_id = self.api_id_input.text().strip()
            api_hash = self.api_hash_input.text().strip()

            if not all([phone, api_id, api_hash]):
                QMessageBox.warning(self, "Ошибка", "Заполните все поля")
                return

            self.logger.info(f"Начало добавления аккаунта {phone}")
            
            # Добавляем аккаунт через сервис авторизации
            result = await self.auth_service.start_auth(phone, api_id, api_hash)
            
            if result.get('need_code'):
                code = self.show_code_dialog()
                if code:
                    result = await self.auth_service.verify_code(code)
                    if result.get('need_2fa'):
                        password = self.show_2fa_dialog()
                        if password:
                            result = await self.auth_service.verify_2fa(password)
            
            if result.get('success'):
                QMessageBox.information(self, "Успех", "Аккаунт успешно добавлен")
                self.clear_inputs()
                await self.update_accounts_list()
                self.account_added.emit()  # Оповещаем о добавлении аккаунта
            else:
                error_msg = result.get('error', 'Неизвестная ошибка')
                self.logger.error(f"Ошибка при добавлении аккаунта: {error_msg}")
                QMessageBox.critical(self, "Ошибка", error_msg)

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Критическая ошибка при добавлении аккаунта: {error_msg}")
            QMessageBox.critical(self, "Ошибка", error_msg)
            await self.auth_service.reset_auth()

    @qasync.asyncSlot()
    async def check_all_accounts(self):
        """Проверка всех аккаунтов"""
        try:
            self.log_message("Начинаем проверку всех аккаунтов...", Colors.INFO)
            results = await self.account_manager.check_all_accounts()
            
            if not results:
                self.log_message("Нет аккаунтов для проверки", Colors.WARNING)
                return
                
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
            error_msg = str(e)
            self.logger.error(f"Ошибка при проверке аккаунтов: {error_msg}")
            self.log_message(f"Ошибка при проверке аккаунтов: {error_msg}", Colors.ERROR)

    async def update_accounts_list(self):
        """Обновление списка аккаунтов"""
        try:
            accounts = self.account_manager.db.get_all_accounts()
            
            html_content = []
            for account in accounts:
                status = "🟢 Активен" if account.is_active else "🔴 Неактивен"
                restrictions = account.restrictions if account.restrictions else "нет"
                
                account_html = (
                    f'<div style="margin-bottom: 10px;">'
                    f'<span style="color: #2196F3;">📱 {account.phone}</span> | {status}<br>'
                    f'<span style="color: #666;">API ID:</span> {account.api_id}<br>'
                    f'<span style="color: #666;">Ограничения:</span> {restrictions}<br>'
                    f'{"─" * 40}'
                    f'</div>'
                )
                html_content.append(account_html)
            
            if not accounts:
                html_content = ['<span style="color: #FFA500;">Нет добавленных аккаунтов</span>']
            
            self.accounts_list.clear()
            self.accounts_list.setHtml(''.join(html_content))
            
        except Exception as e:
            error_msg = f"Ошибка при обновлении списка аккаунтов: {str(e)}"
            self.logger.error(error_msg)
            QMessageBox.critical(self, "Ошибка", error_msg)

    def show_code_dialog(self):
        """Показать диалог для ввода кода подтверждения"""
        dialog = CodeVerificationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_code()
        return None

    def show_2fa_dialog(self):
        """Показать диалог для ввода пароля двухфакторной аутентификации"""
        dialog = TwoFactorAuthDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_password()
        return None

    def clear_inputs(self):
        """Очистка полей ввода"""
        self.phone_input.clear()
        self.api_id_input.clear()
        self.api_hash_input.clear()

    def log_message(self, message: str, color: str):
        """Добавление сообщения в лог"""
        current_html = self.accounts_list.toHtml()
        new_message = f'<div style="color: {color};">{message}</div>'
        self.accounts_list.setHtml(current_html + new_message) 
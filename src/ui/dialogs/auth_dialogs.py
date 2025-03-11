from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt

from ui.styles import Styles

class CodeVerificationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса диалога"""
        self.setWindowTitle('Подтверждение кода')
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout(self)
        
        # Метка с инструкцией
        info_label = QLabel('Введите код, отправленный в Telegram:')
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Поле ввода кода
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText('Код подтверждения')
        self.code_input.setStyleSheet(Styles.INPUT)
        layout.addWidget(self.code_input)
        
        # Кнопка подтверждения
        confirm_button = QPushButton('Подтвердить')
        confirm_button.setStyleSheet(Styles.BUTTON)
        confirm_button.clicked.connect(self.accept)
        layout.addWidget(confirm_button)

    def get_code(self):
        """Получение введенного кода"""
        return self.code_input.text().strip()

class TwoFactorAuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса диалога"""
        self.setWindowTitle('Двухфакторная аутентификация')
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout(self)
        
        # Метка с инструкцией
        info_label = QLabel('Введите пароль двухфакторной аутентификации:')
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Поле ввода пароля
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Пароль 2FA')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(Styles.INPUT)
        layout.addWidget(self.password_input)
        
        # Кнопка подтверждения
        confirm_button = QPushButton('Подтвердить')
        confirm_button.setStyleSheet(Styles.BUTTON)
        confirm_button.clicked.connect(self.accept)
        layout.addWidget(confirm_button)

    def get_password(self):
        """Получение введенного пароля"""
        return self.password_input.text().strip() 
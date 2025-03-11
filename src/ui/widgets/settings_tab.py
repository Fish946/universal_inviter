from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout,
                           QPushButton, QLabel, QLineEdit, QMessageBox)
from ui.styles import Styles

class SettingsTab(QWidget):
    def __init__(self, config, logger):
        super().__init__()
        self.config = config
        self.logger = logger
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса вкладки настроек"""
        layout = QVBoxLayout(self)

        # Настройки задержек
        delays_group = QWidget()
        delays_layout = QGridLayout(delays_group)
        
        self.between_adds_input = QLineEdit(str(self.config.default_delays['between_adds']))
        self.between_adds_input.setStyleSheet(Styles.INPUT)
        
        self.error_delay_input = QLineEdit(str(self.config.default_delays['error_delay']))
        self.error_delay_input.setStyleSheet(Styles.INPUT)
        
        self.check_delay_input = QLineEdit(str(self.config.default_delays['check_delay']))
        self.check_delay_input.setStyleSheet(Styles.INPUT)
        
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
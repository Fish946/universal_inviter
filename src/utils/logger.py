import logging
import os
from datetime import datetime
from typing import Optional
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QColor, QTextCharFormat, QBrush

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'ERROR': QColor(255, 0, 0),      # Красный
        'WARNING': QColor(255, 165, 0),   # Оранжевый
        'INFO': QColor(0, 128, 0),        # Зеленый
        'DEBUG': QColor(128, 128, 128)    # Серый
    }

    def format(self, record):
        formatted = super().format(record)
        return {
            'text': formatted,
            'color': self.COLORS.get(record.levelname, QColor(0, 0, 0))
        }

class QTextEditLogger(logging.Handler):
    def __init__(self, widget: QTextEdit):
        super().__init__()
        self.widget = widget
        self.formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s')

    def emit(self, record):
        formatted = self.formatter.format(record)
        text = formatted['text']
        color = formatted['color']

        # Создаем формат для текста
        text_format = QTextCharFormat()
        text_format.setForeground(QBrush(color))

        # Добавляем текст с форматированием
        cursor = self.widget.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(f"{text}\n", text_format)
        self.widget.setTextCursor(cursor)
        self.widget.ensureCursorVisible()

def setup_logger(log_widget: Optional[QTextEdit] = None) -> logging.Logger:
    logger = logging.getLogger('UniversalInviter')
    logger.setLevel(logging.DEBUG)

    # Создаем форматтер для файла
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Создаем директорию для логов если её нет
    os.makedirs('data/logs', exist_ok=True)

    # Хендлер для файла
    file_handler = logging.FileHandler(
        f'data/logs/inviter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Добавляем хендлер для виджета если он предоставлен
    if log_widget is not None:
        widget_handler = QTextEditLogger(log_widget)
        logger.addHandler(widget_handler)

    return logger 
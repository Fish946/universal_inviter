from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt

class Colors:
    PRIMARY = "#2196F3"
    BACKGROUND = "#E0E0E0"
    TEXT = "#000000"
    ERROR = "#F44336"
    SUCCESS = "#4CAF50"
    WARNING = "#FFC107"
    INFO = "#2196F3"

class Fonts:
    DEFAULT = "Arial"
    SIZE_NORMAL = "12px"
    SIZE_LARGE = "14px"
    SIZE_SMALL = "10px"

class Styles:
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {Colors.BACKGROUND};
        }}
        QLabel {{
            color: {Colors.TEXT};
            font-family: {Fonts.DEFAULT};
            font-size: {Fonts.SIZE_NORMAL};
        }}
    """
    # ... остальные стили ...

class Styles:
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {Colors.BACKGROUND};
        }}
        QLabel {{
            color: {Colors.TEXT};
        }}
    """

    INPUT = f"""
        QLineEdit {{
            padding: 8px;
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            background-color: white;
            color: {Colors.TEXT};
        }}
    """

    BUTTON = f"""
        QPushButton {{
            padding: 8px 16px;
            background-color: {Colors.PRIMARY};
            color: white;
            border: none;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: #1976D2;
        }}
        QPushButton:disabled {{
            background-color: #BDBDBD;
        }}
    """

    LOG_VIEW = f"""
        QTextEdit {{
            background-color: white;
            color: {Colors.TEXT};
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            padding: 8px;
        }}
    """
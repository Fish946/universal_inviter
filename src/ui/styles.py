from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt

class Colors:
    PRIMARY = "#2196F3"
    SECONDARY = "#FFC107"
    SUCCESS = "#4CAF50"
    ERROR = "#F44336"
    WARNING = "#FF9800"
    INFO = "#2196F3"
    BACKGROUND = "#FFFFFF"
    TEXT = "#000000"
    DISABLED = "#BDBDBD"

class Styles:
    MAIN_WINDOW = """
        QMainWindow {
            background-color: #F5F5F5;
        }
    """
    
    BUTTON = f"""
        QPushButton {{
            background-color: {Colors.PRIMARY};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #1976D2;
        }}
        QPushButton:disabled {{
            background-color: {Colors.DISABLED};
        }}
    """
    
    INPUT = """
        QLineEdit {
            padding: 8px;
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            background-color: white;
        }
        QLineEdit:focus {
            border: 2px solid #2196F3;
        }
    """
    
    LOG_VIEW = """
        QTextEdit {
            background-color: white;
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            padding: 8px;
            font-family: monospace;
        }
    """

class Fonts:
    NORMAL = QFont("Segoe UI", 10)
    BOLD = QFont("Segoe UI", 10, QFont.Weight.Bold)
    LARGE = QFont("Segoe UI", 12)
    SMALL = QFont("Segoe UI", 9) 
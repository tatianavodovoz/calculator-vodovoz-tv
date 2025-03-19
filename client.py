import sys
import re
import json
import requests
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QTextEdit,
    QMessageBox,
)
from PySide6.QtCore import Qt,QTimer, QRunnable, Slot, QThreadPool, QObject, Signal
from PySide6.QtGui import QValidator, QPalette

# ================================================
# Валидатор математических выражений
# ================================================
class MathExpressionValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.last_valid_state = False

    def validate(self, text, pos):
        is_float_mode = self.parent_window.mode_selector.currentIndex() == 1
        allowed_chars = r'[\d+\-*/\(\)\.\s]' if is_float_mode else r'[\d+\-*/\(\)\s]'
        
        # Проверка базовых символов
        if not re.fullmatch(f'^{allowed_chars}*$', text):
            self.last_valid_state = False
            return (QValidator.Invalid, text, pos)
        
        # Проверка продвинутых правил
        is_valid = self._advanced_validation(text, is_float_mode)
        self.last_valid_state = is_valid
        
        return (QValidator.Acceptable if is_valid else QValidator.Intermediate, text, pos)
        
    def _advanced_validation(self, text, is_float_mode):
        # 1. Проверка баланса скобок
        open_brackets = text.count('(') - text.count(')')
        if open_brackets != 0:
            return False

        # 2. Запрет двойных операторов
        if re.search(r'[\+\-\*/]{2,}', text):
            return False

        # 4. Запрет пустых скобок
        if re.search(r'\(\)', text):
            return False

        if re.search(r'\d+\s+\d+', text):
            return False


        return True  

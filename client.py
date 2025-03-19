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
# ================================================
# Класс для обработки вычислений в отдельном потоке
# ================================================
class WorkerSignals(QObject):
    result = Signal(dict)
    error = Signal(dict)

class CalculationWorker(QRunnable):
    def __init__(self, url, expression, float_mode):
        super().__init__()
        self.url = url
        self.expression = expression
        self.float_mode = float_mode
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            response = requests.post(self.url,
                params={'float': str(self.float_mode).lower()},
                headers={'Content-Type': 'application/json'},
                data=json.dumps(self.expression),
                timeout=5)
            raw_response = response.text.strip()

            # Пытаемся распарсить JSON
            try:
                response_data = json.loads(raw_response)
                is_json = True
            except json.JSONDecodeError:
                response_data = raw_response
                is_json = False

            if response.status_code == 200:
                # Обработка успешного ответа
                if is_json:
                    result = response_data.get('result') if isinstance(response_data, dict) else response_data
                else:
                    result = response_data

                # Конвертация результата
                try:
                    parsed_result = float(result) if '.' in str(result) else int(result)
                    self.signals.result.emit({'result': parsed_result})
                except ValueError:
                    raise ValueError(f"Invalid numeric result: {result}")

            else:
                # Обработка ошибки
                error_msg = response_data.get('error') if (is_json and isinstance(response_data, dict)) else response_data
                self.signals.error.emit({
                    'error': error_msg or "Unknown error",
                    'status': response.status_code
                })

        except Exception as e:
            self.signals.error.emit({
                'error': str(e),
                'status': 500
            })

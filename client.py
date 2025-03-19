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

# ================================================
# Основное окно приложения
# ================================================
class CalculatorClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server_url = "http://localhost:8000/calc"
        self.thread_pool = QThreadPool()
        self.current_worker = None
        self.init_ui()
        self.setWindowTitle("Calculator Client")
        self.check_server_status()
        self._init_ui_state()
        
    def _init_ui_state(self):
        """Инициализация состояния UI"""
        self.calculate_btn.setEnabled(False)
        self.expression_input.textChanged.connect(self._update_ui_state)
        
    def _update_ui_state(self):
        """Обновление состояния кнопки на основе валидации"""
        validator = self.expression_input.validator()
        text = self.expression_input.text()
        
        # Проверка через валидатор
        state, _, _ = validator.validate(text, 0)
        is_valid = (state == QValidator.Acceptable) and bool(text.strip())
        
        self.calculate_btn.setEnabled(is_valid)
        self.error_label.setText("" if is_valid else "Некорректное выражение")


    def init_ui(self):
        # Создание виджетов
        self.expression_input = QLineEdit()
        self.result_display = QTextEdit(readOnly=True)
        self.calculate_btn = QPushButton("Calculate")
        self.cancel_btn = QPushButton("Cancel", enabled=False)
        self.mode_selector = QComboBox()
        self.server_status = QLabel("Server status: Checking...")
        self.error_label = QLabel()
        
        # Настройка валидатора
        self.expression_input.setValidator(MathExpressionValidator(self))
        
        # Настройка выпадающего списка
        self.mode_selector.addItems(["Integer", "Float"])
        
        # Цветовая схема
        self.result_display.setStyleSheet("font-size: 14pt;")
        self.error_label.setStyleSheet("color: red;")

        # Расположение элементов
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Mode:"))
        control_layout.addWidget(self.mode_selector)
        control_layout.addWidget(self.calculate_btn)
        control_layout.addWidget(self.cancel_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Enter expression:"))
        main_layout.addWidget(self.expression_input)
        main_layout.addLayout(control_layout)
        main_layout.addWidget(QLabel("Result:"))
        main_layout.addWidget(self.result_display)
        main_layout.addWidget(self.server_status)
        main_layout.addWidget(self.error_label)

        # Контейнер
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Соединение сигналов
        self.calculate_btn.clicked.connect(self.start_calculation)
        self.cancel_btn.clicked.connect(self.cancel_calculation)
        self.mode_selector.currentIndexChanged.connect(self.clear_error)

        # Таймер проверки сервера
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_server_status)
        self.status_timer.start(5000)

    def start_calculation(self):
        expression = self.expression_input.text().strip()
         
        if not self.expression_input.validator().last_valid_state:
            self.show_error("Ошибка", "Исправьте выражение перед отправкой")
            return
        
        # Дополнительная проверка перед отправкой
        if not self.expression_input.validator().validate(expression, 0)[0] == QValidator.Acceptable:
            self.show_error("Ошибка", "Некорректные символы в выражении")
            return
        if self.current_worker:
            self.cancel_calculation()

        expression = self.expression_input.text().strip()
        if not expression:
            self.show_error("Empty input", "Please enter an expression")
            return

        self.result_display.clear()
        self.set_controls_enabled(False)
        self.cancel_btn.setEnabled(True)

        worker = CalculationWorker(
            url=self.server_url,
            expression=expression,
            float_mode=self.mode_selector.currentIndex() == 1
        )
        
        worker.signals.result.connect(self.handle_result)
        worker.signals.error.connect(self.handle_error)
        self.thread_pool.start(worker)
        self.current_worker = worker

    def cancel_calculation(self):
        if self.current_worker:
            self.current_worker = None
            self.set_controls_enabled(True)
            self.cancel_btn.setEnabled(False)
            self.result_display.setPlainText("Calculation canceled")

    def handle_result(self, result_data):
        """Отображение успешного результата"""
        try:
            result = result_data['result']
            display_text = f"{result:.4f}" if isinstance(result, float) else f"{result}"
            self.result_display.setPlainText(display_text)
            self.error_label.clear()
        except KeyError:
            self.handle_error({'error': 'Некорректный формат результата', 'status': 500})

    def handle_error(self, error_data):
        """Отображение ошибки"""
        error_msg = error_data.get('error', 'Неизвестная ошибка')
        status_code = error_data.get('status', 500)
        
        # Не показывать технические детали для пользователя
        user_friendly_error = {
            "invalid numeric format": "Некорректный формат числа",
            "division by zero": "Деление на ноль запрещено"
        }.get(error_msg.lower(), error_msg)

        self.error_label.setText(f"Ошибка {status_code}: {user_friendly_error}")
        self.result_display.clear()

    def check_server_status(self):
        try:
            response = requests.get("http://localhost:8000/", timeout=2)
            self.update_server_status(response.status_code == 200)
        except:
            self.update_server_status(False)

    def update_server_status(self, is_online):
        status_text = "🟢 Online" if is_online else "🔴 Offline"
        color = "green" if is_online else "red"
        self.server_status.setText(f"Server status: <b>{status_text}</b>")
        self.server_status.setStyleSheet(f"color: {color};")

    def check_brackets_balance(self, text):
        open_count = text.count("(")
        close_count = text.count(")")
        if open_count > close_count:
            self.error_label.setText(f"Missing {open_count - close_count} closing brackets")
        elif close_count > open_count:
            self.error_label.setText(f"Extra {close_count - open_count} closing brackets")
        else:
            self.error_label.clear()

    def clear_error(self):
        self.error_label.clear()

    def set_controls_enabled(self, enabled):
        self.expression_input.setEnabled(enabled)
        self.mode_selector.setEnabled(enabled)
        self.calculate_btn.setEnabled(enabled)

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event):
        self.cancel_calculation()
        self.thread_pool.waitForDone(1000)
        self.status_timer.stop()
        event.accept()

# ================================================# Запуск приложения
# ================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalculatorClient()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())

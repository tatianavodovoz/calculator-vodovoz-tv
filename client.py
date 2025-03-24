import sys
import re
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox,QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QValidator
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtNetwork import QAbstractSocket

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
        if text.count('(') != text.count(')'):
            return False

        # 2. Запрет двойных операторов
        if re.search(r'[\+\-*/]{2,}', text):
            return False

        # 3. Запрет пустых скобок
        if re.search(r'\(\)', text):
            return False

        # 4. Проверка чисел с пробелами
        if re.search(r'\d+\s+\d+', text):
            return False

        return True

class HistoryModel:
    def __init__(self):
        self.history = []
        self.last_id = 0

    def update(self, new_history):
        new_items = [item for item in new_history if item['id'] > self.last_id]
        self.history.extend(new_items)
        if new_items:
            self.last_id = max(item['id'] for item in new_items)

class CalculatorClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ws_url = "ws://localhost:8000/ws"
        self.history_model = HistoryModel()
        self.init_ui()
        self.init_websocket()
        self.setWindowTitle("Calculator Client")
        self.resize(1200, 800)

    def init_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        # Input Section
        self.expression_input = QLineEdit()
        self.expression_input.setValidator(MathExpressionValidator(self))
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Integer", "Float"])
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setEnabled(False)

        # Подключение сигналов валидации
        self.expression_input.textChanged.connect(self.update_ui_state)
        self.mode_selector.currentIndexChanged.connect(self.update_ui_state)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Expression:"))
        input_layout.addWidget(self.expression_input)
        input_layout.addWidget(QLabel("Mode:"))
        input_layout.addWidget(self.mode_selector)
        input_layout.addWidget(self.submit_btn)

        # History Table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "Expression", "Mode", "Result", "Error"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Status
        self.status_label = QLabel("Connecting...")

        layout.addLayout(input_layout)
        layout.addWidget(QLabel("Calculation History:"))
        layout.addWidget(self.history_table)
        layout.addWidget(self.status_label)

        central.setLayout(layout)
        self.setCentralWidget(central)

        self.submit_btn.clicked.connect(self.submit_expression)

    def update_ui_state(self):
        """Обновление состояния UI на основе валидации"""
        validator = self.expression_input.validator()
        text = self.expression_input.text()
        
        # Проверка валидности
        state = validator.validate(text, 0)[0]
        is_valid = (state == QValidator.Acceptable) and bool(text.strip())
        
        # Блокировка кнопки
        self.submit_btn.setEnabled(is_valid)
        
        # Визуальная индикация
        if state == QValidator.Invalid:
            self.expression_input.setStyleSheet("border: 2px solid red;")
        elif state == QValidator.Intermediate:
            self.expression_input.setStyleSheet("border: 2px solid orange;")
        else:
            self.expression_input.setStyleSheet("")

    def init_websocket(self):
        self.ws = QWebSocket()
        self.ws.connected.connect(self.on_connected)
        self.ws.disconnected.connect(self.on_disconnected)
        self.ws.textMessageReceived.connect(self.on_message)
        self.ws.open(self.ws_url)

        self.reconnect_timer = QTimer()
        self.reconnect_timer.timeout.connect(self.reconnect)
        self.reconnect_timer.start(5000)

    def submit_expression(self):
        expression = self.expression_input.text()
        mode = 'float' if self.mode_selector.currentIndex() == 1 else 'int'
        if self.ws.state() == QAbstractSocket.ConnectedState:
            self.ws.sendTextMessage(json.dumps({
                'type': 'new_expression',
                'expression': expression,
                'mode': mode
            }))
            self.expression_input.clear()

    def on_connected(self):
        self.status_label.setText("Connected")

    def on_disconnected(self):
        self.status_label.setText("Disconnected")

    def on_message(self, message):
        data = json.loads(message)
        if data['type'] == 'history_update':
            self.history_model.update(data['data'])
            self.update_history_table()

    def update_history_table(self):
        self.history_table.setRowCount(len(self.history_model.history))
        for row, item in enumerate(self.history_model.history):
            self.history_table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.history_table.setItem(row, 1, QTableWidgetItem(item['expression']))
            self.history_table.setItem(row, 2, QTableWidgetItem(item['mode']))
            self.history_table.setItem(row, 3, QTableWidgetItem(item.get('result', '')))
            self.history_table.setItem(row, 4, QTableWidgetItem(item.get('error', '')))

    def reconnect(self):
        if self.ws.state() != QAbstractSocket.ConnectedState:
            self.ws.open(self.ws_url)

    def closeEvent(self, event):
        self.ws.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalculatorClient()
    window.show()
    sys.exit(app.exec())

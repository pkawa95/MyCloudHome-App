from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from selenium_logic import login_to_mycloud, driver
from gui import WDExplorer
import sys

class LoginWorker(QThread):
    login_success = pyqtSignal()
    login_failed = pyqtSignal(str)
    log_update = pyqtSignal(str)
    progress_update = pyqtSignal(int)

    def __init__(self, email, password):
        super().__init__()
        self.email = email
        self.password = password
        self.progress = 0  # Zmienna przechowująca stan progress bar

    def run(self):
        try:
            self.log_update.emit("🔐 Rozpoczynam logowanie...")
            self.update_progress(10)  # Wzrost progressu o 10%

            login_to_mycloud(self.email, self.password)

            self.update_progress(100)  # Pełny progress bar
            self.log_update.emit("✅ Zalogowano! Trwa uruchamianie GUI proszę czekać...")
            self.login_success.emit()

        except Exception as e:
            self.log_update.emit(f"❌ Błąd podczas logowania: {str(e)}")
            self.login_failed.emit(str(e))

    def update_progress(self, value):
        self.progress += value
        # Sprawdzamy, żeby nie przekroczyć 100%
        if self.progress > 100:
            self.progress = 100
        self.progress_update.emit(self.progress)

class PrintLogger:
    def __init__(self, callback):
        self.callback = callback

    def write(self, message):
        if message.strip():
            self.callback(message.strip())

    def flush(self):
        pass

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logowanie do WD My Cloud Home")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout(self)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Adres email")
        layout.addWidget(self.email_input)
        sys.stdout = PrintLogger(self.update_log)
        sys.stderr = PrintLogger(self.update_log)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Hasło")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Zaloguj się")
        self.login_button.clicked.connect(self.start_login)
        layout.addWidget(self.login_button)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Nowa etykieta na stopce
        self.status_label = QLabel("Zaloguj się by rozpocząć pracę")  # status początkowy
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: grey;")
        layout.addWidget(self.status_label)

        self.progress_value = 0

        sys.stdout = PrintLogger(self.update_log)
        sys.stderr = PrintLogger(self.update_log)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

    def start_login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        if not email or not password:
            self.log_box.append("⚠️ Proszę wprowadzić email i hasło.")
            return

        self.worker = LoginWorker(email, password)
        self.worker.log_update.connect(self.update_log)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.login_success.connect(self.login_successful)
        self.worker.login_failed.connect(self.login_failed)
        self.worker.start()

        self.login_button.setEnabled(False)
        self.status_label.setText("Logowanie...")  # zmiana statusu na "Logowanie..."

    def update_log(self, message):
        self.log_box.append(message)
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())

        # Sprawdzamy, czy w logach pojawił się komunikat o zalogowaniu
        if "Zalogowano!" in message:
            self.status_label.setText("✅ Zalogowano! Trwa uruchamianie GUI proszę czekać...")

    def update_progress(self, value):
        # Aktualizujemy progress bar w zależności od wartości
        self.progress.setValue(value)

    def login_successful(self):
        self.update_log("✅ Przechodzę do eksploratora plików...")
        self.explorer = WDExplorer()
        self.explorer.show()
        self.close()

    def login_failed(self, error):
        self.update_log(f"❌ Logowanie nieudane: {error}")
        self.login_button.setEnabled(True)
        self.status_label.setText("Zaloguj się by rozpocząć pracę")  # wróć do statusu początkowego

from PyQt6.QtWidgets import QApplication
import sys

from login_window import LoginWindow  # Import nowego okna logowania
from gui import WDExplorer

def main():
    app = QApplication(sys.argv)

    # 🔐 Otwieramy nowe okienko logowania
    login_window = LoginWindow()
    login_window.show()

    app.exec()

if __name__ == "__main__":
    main()

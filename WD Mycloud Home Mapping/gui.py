from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QMenu, QMessageBox, QFileDialog, QSplitter, QListView
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QSize
import sys
from selenium_logic import list_files_selenium, driver  # zakładamy że mamy selenium uruchomione

class WDExplorer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WD My Cloud Home - Explorer")
        self.setMinimumSize(1000, 600)

        # Layout główny
        main_layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Lista plików/folderów
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(self.list_dark_style())
        self.list_widget.setViewMode(QListView.ViewMode.ListMode)
        self.list_widget.setIconSize(QSize(64, 64))
        self.list_widget.setGridSize(QSize(100, 100))
        self.list_widget.setSpacing(10)
        self.list_widget.setMovement(QListView.Movement.Static)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.open_context_menu)
        self.list_widget.itemDoubleClicked.connect(self.open_item)

        self.splitter.addWidget(self.list_widget)
        main_layout.addWidget(self.splitter)

        # Wczytaj pliki/foldery z My Cloud Home
        self.populate_from_selenium()

    def populate_from_selenium(self, path=""):
        print("⚙️ Wywołano populate_from_selenium")
        self.list_widget.clear()
        items = list_files_selenium(driver, path)
        print(f"📦 Odebrano z Selenium: {len(items)} elementów")

        for entry in items:
            print(f"🧩 Tworzę element GUI: {entry}")

            name = entry.get("name", "Brak Nazwy")
            type_ = entry.get("type", "folder")
            path_ = entry.get("path", "")

            if type_ == "folder":
                item = QListWidgetItem(QIcon("assets/folder_icon.png"), name)
            else:
                item = QListWidgetItem(QIcon("assets/file_icon.png"), name)

            item.setData(Qt.ItemDataRole.UserRole, {"type": type_, "path": path_})
            self.list_widget.addItem(item)
        print("✅ GUI odświeżone.")

    def open_context_menu(self, position):
        item = self.list_widget.itemAt(position)
        if item:
            menu = QMenu()
            action_open = QAction("Otwórz", self)
            action_download = QAction("Pobierz", self)
            action_rename = QAction("Zmień nazwę", self)
            action_delete = QAction("Usuń", self)

            action_open.triggered.connect(lambda: self.open_item(item))
            action_download.triggered.connect(lambda: self.download_item(item))
            action_rename.triggered.connect(lambda: self.rename_item(item))
            action_delete.triggered.connect(lambda: self.delete_item(item))

            menu.addAction(action_open)
            menu.addAction(action_download)
            menu.addSeparator()
            menu.addAction(action_rename)
            menu.addAction(action_delete)

            menu.exec(self.list_widget.viewport().mapToGlobal(position))

    def open_item(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data["type"] == "folder":
            self.populate_from_selenium(data["path"])
        else:
            QMessageBox.information(self, "Info", f"Podgląd pliku: {item.text()}")

    def download_item(self, item):
        QMessageBox.information(self, "Info", f"Pobieranie: {item.text()}")

    def rename_item(self, item):
        QMessageBox.information(self, "Info", f"Zmiana nazwy: {item.text()}")

    def delete_item(self, item):
        QMessageBox.information(self, "Info", f"Usuwanie: {item.text()}")

    def list_dark_style(self):
        return """
            QListWidget {
                background-color: #121212;
                color: #E0E0E0;
                border: none;
            }
            QListWidget::item:selected {
                background-color: #333333;
            }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WDExplorer()
    window.show()
    sys.exit(app.exec())

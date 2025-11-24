import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import BackupApp
from src.ui.styles import DARK_THEME

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)
    
    window = BackupApp()
    window.show()
    
    sys.exit(app.exec())
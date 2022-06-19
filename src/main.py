import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from window import MainWindow

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
    except RuntimeError as err:
        QMessageBox.critical(window, "Error", err)
    finally:
        sys.exit(app.exec())
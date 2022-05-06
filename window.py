import gui, time
from PySide6.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = gui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.startButton.clicked.connect(self.record)

    def record(self):
        self.ui.startButton.setEnabled(False)
        time.sleep(5)
        self.ui.startButton.setEnabled(True)
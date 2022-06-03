# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
    QMenuBar, QProgressBar, QPushButton, QSizePolicy,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.songLabel = QLabel(self.centralwidget)
        self.songLabel.setObjectName(u"songLabel")
        self.songLabel.setGeometry(QRect(20, 180, 23, 16))
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(30, 250, 252, 46))
        self.audioLayout = QVBoxLayout(self.widget)
        self.audioLayout.setObjectName(u"audioLayout")
        self.audioLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonsLayout = QHBoxLayout()
        self.buttonsLayout.setObjectName(u"buttonsLayout")
        self.startButton = QPushButton(self.widget)
        self.startButton.setObjectName(u"startButton")

        self.buttonsLayout.addWidget(self.startButton)

        self.playButton = QPushButton(self.widget)
        self.playButton.setObjectName(u"playButton")

        self.buttonsLayout.addWidget(self.playButton)

        self.loadButton = QPushButton(self.widget)
        self.loadButton.setObjectName(u"loadButton")

        self.buttonsLayout.addWidget(self.loadButton)


        self.audioLayout.addLayout(self.buttonsLayout)

        self.audioProgress = QProgressBar(self.widget)
        self.audioProgress.setObjectName(u"audioProgress")
        self.audioProgress.setValue(0)
        self.audioProgress.setTextVisible(False)

        self.audioLayout.addWidget(self.audioProgress)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 17))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.songLabel.setText(QCoreApplication.translate("MainWindow", u"Song:", None))
        self.startButton.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.playButton.setText(QCoreApplication.translate("MainWindow", u"Play recording", None))
        self.loadButton.setText(QCoreApplication.translate("MainWindow", u"Load music", None))
    # retranslateUi


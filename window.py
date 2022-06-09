import enum, sounddevice as sd, os, pickle, json
from recording import Recording
from PlotWidget import PlotWidget
from PySide6.QtWidgets import (QMainWindow, QGridLayout, QPushButton, QProgressBar, 
                               QVBoxLayout, QHBoxLayout, QLabel, QWidget, QFileDialog,
                               QListWidget, QListWidgetItem, QStackedWidget, QCheckBox)
from PySide6.QtCore import QObject, Signal, QThread, QSize
from PySide6.QtGui import QPalette

#Classes for pararel task execution
class RecordingWorker(QObject):
    finished = Signal(None)
    def __init__(self, w):
        super(RecordingWorker, self).__init__()
        self._parent = w
    def run(self) -> None:
        self._parent.rec.record()
        sd.wait()
        self._parent.rec.prepareRecording()
        self.finished.emit()
        
class PlayWorker(RecordingWorker):
    progress = Signal(int)
    def __init__(self, w):
        super(PlayWorker, self).__init__(w)
    
    def run(self) -> None:
        self._parent.rec.play()
        sd.wait()
        self.finished.emit()
        
class LoadWorker(RecordingWorker):
    def __init__(self, w):
        super(LoadWorker, self).__init__(w)
    
    def run(self) -> None:
        self._parent.loadFile()
        self.finished.emit()
        
class DataLoadWorker(RecordingWorker):
    def __init__(self, w):
        super(DataLoadWorker, self).__init__(w)
    
    def run(self) -> None:
        self._parent.songLabel.setText("Loading database...")
        self._parent.songsHashes = pickle.load(open("db.pickle", "rb"))
        self._parent.songsIndecies = pickle.load(open("songs.pickle", "rb"))
        self.finished.emit()
        

class WorkerType(enum.Enum):
    RECORD = enum.auto()
    PLAY = enum.auto()
    LOAD = enum.auto()
    LOAD_DB = enum.auto()

#GUI class
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.resize(1200, 600)
        
        
        widget = QWidget()
        self.songLabel = QLabel()
        
        self.resultsList = QListWidget()

        audioLayout = QVBoxLayout()
        audioLayout.setContentsMargins(0, 0, 0, 0)
        buttonsLayout = QHBoxLayout()
        plotButtonsLayout = QHBoxLayout()

        self.startButton = QPushButton()

        buttonsLayout.addWidget(self.startButton)

        self.playButton = QPushButton()

        buttonsLayout.addWidget(self.playButton)

        self.loadButton = QPushButton()

        buttonsLayout.addWidget(self.loadButton)

        self.inputButton = QPushButton()
        plotButtonsLayout.addWidget(self.inputButton)        
        self.fftButton = QPushButton()
        plotButtonsLayout.addWidget(self.fftButton)        
        self.fingerprintButton = QPushButton()
        plotButtonsLayout.addWidget(self.fingerprintButton)
        
        self.exportButton = QPushButton()
        self.exportButton.setText(u"Export results")
        
        self.correctCheck = QCheckBox()
        self.correctCheck.setText(u"Correct")
        self.correctCheck.setEnabled(False)
        
        audioLayout.addLayout(buttonsLayout)

        
        self.inputWidget = PlotWidget()
        self.ftWidget = PlotWidget()
        self.fingerprintWidget = PlotWidget()
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.inputWidget)
        self.stackedWidget.addWidget(self.ftWidget)
        self.stackedWidget.addWidget(self.fingerprintWidget)
        
        layout = QGridLayout()
        
        layout.addWidget(self.stackedWidget, 1, 0, 1, 1)
        layout.addWidget(self.songLabel, 2, 0)
        layout.addLayout(audioLayout, 3, 0)
        layout.addLayout(plotButtonsLayout, 0, 0, 1, 1)
        layout.addWidget(self.resultsList, 0, 1, 2, 1)
        layout.addWidget(self.correctCheck, 2, 1, 1, 1)
        layout.addWidget(self.exportButton, 3, 1, 1, 1)
        
        
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        self.setWindowTitle("Music recognizer")
        self.songLabel.setText(u"Loading database...")
        self.startButton.setText(u"Start recording")
        self.playButton.setText(u"Play recording")
        self.loadButton.setText(u"Load music")
        self.inputButton.setText(u"Input")
        self.fftButton.setText(u"Fourier transform")
        self.fingerprintButton.setText(u"Fingerprint")
                
        self.startButton.setEnabled(False)
        self.playButton.setEnabled(False)
        self.loadButton.setEnabled(False)
        
        #signals
        
        self.startButton.clicked.connect(self.record)
        self.playButton.clicked.connect(self.play)
        self.loadButton.clicked.connect(self.loadFile)        
        self.inputButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.fftButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.fingerprintButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.correctCheck.stateChanged.connect(self.correctnessChanged)
        self.exportButton.clicked.connect(self.export)
        self.resultsList.currentRowChanged.connect(self.resultSelected)
        
        self.rec = Recording()
        self.results = {}
        self.currentIndex = 0
        
        self.createThread(WorkerType.LOAD_DB, self.dataLoadingFinished)
        self.thread.start()
        
        

    def createThread(self, workerType: WorkerType, finishCallback):
        match workerType:
            case WorkerType.RECORD:
                self.worker = RecordingWorker(self)
            case WorkerType.PLAY:
                self.worker = PlayWorker(self)
            case WorkerType.LOAD:
                self.worker = LoadWorker(self)            
            case WorkerType.LOAD_DB:
                self.worker = DataLoadWorker(self)
                
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        if finishCallback is not None:
            self.thread.finished.connect(finishCallback)

    def record(self):
        devices = sd.query_devices(kind="input")
        if not devices: 
            raise RuntimeError("Failed to find input devices")
        self.createThread(WorkerType.RECORD, self.endRecording)
        self.startButton.setEnabled(False)
        self.thread.start()
        
    def play(self):
        if self.rec.data is None: 
            return
        self.createThread(WorkerType.PLAY, self.endPlaying)
        self.playButton.setEnabled(False)
        self.thread.start()
    
    def endRecording(self):
        self.startButton.setEnabled(True)
        self.rec.generateHash(self.fingerprintWidget.axes)
        self.recognizeSong()
        self.__updatePlots()
        
    def __updatePlots(self):
        self.inputWidget.axes.cla()
        self.inputWidget.axes.plot(self.rec.data)
        self.ftWidget.axes.cla()
        self.rec.plotFFT(self.ftWidget.axes)
        self.inputWidget.draw()
        self.ftWidget.draw()
        self.fingerprintWidget.draw()
        
    def endPlaying(self):
        self.playButton.setEnabled(True)
    
    def dataLoadingFinished(self):
        self.startButton.setEnabled(True)
        self.playButton.setEnabled(True)
        self.loadButton.setEnabled(True)
        self.songLabel.setText("Database loading finished!")
    
    def load(self):
        self.createThread(WorkerType.LOAD, None)
        self.thread.start()
    
    def loadFile(self):
        path, _ = QFileDialog.getOpenFileName(self, u"Open file", os.getcwd(), "Audio file (*.wav *.wave *.flac *.mp3 *.aac *.m4a *.ogg *.oga);;WAV(*.wav *.wave);;FLAC(*.flac);;MP3(*.mp3);;AAC(*.aac *.m4a);;OGG Vorbis(*.ogg *.oga)")
        if path != "":
            self.rec.load(path)
            self.rec.generateHash(self.fingerprintWidget.axes)
            self.recognizeSong()
            self.__updatePlots()
    
    def recognizeSong(self):

        self.songLabel.setText("Recognizing song...")
        
        matchesPerSong = {}
        for hash, (sampleTime, _) in self.rec.fingerprint.items():
            if hash in self.songsHashes:
                matchingOccur = self.songsHashes[hash]
                for srcTime, songIndex in matchingOccur:
                    if songIndex not in matchesPerSong:
                        matchesPerSong[songIndex] = []
                    matchesPerSong[songIndex].append((hash, sampleTime, srcTime))
        scores = {}
        for songIndex, matches in matchesPerSong.items():
            songScoresByOffset = {}
            for hash, sampleTime, srcTime in matches:
                delta = srcTime - sampleTime
                if delta not in songScoresByOffset:
                    songScoresByOffset[delta] = 0
                songScoresByOffset[delta] += 1
            max = (0, 0)
            for offset, score in songScoresByOffset.items():
                if score > max[1]:
                    max = (offset, score)
                    
            scores[songIndex] = max
        
        scores = list(sorted(scores.items(), key=lambda x: x[1][1], reverse=True))
        
        songId, _ = scores[0]
        
        artist, title, album = self.songsIndecies[songId]
        
        self.songLabel.setText(f"Song: {artist} - {title} [Album: {album}]")
        
        item = QListWidgetItem()
        item.setText(f"{artist} - {title} [Album: {album}]")
        self.resultsList.addItem(item)
        if not self.results:
            self.correctCheck.setEnabled(True)
        self.results[self.currentIndex] = True
        self.correctCheck.setChecked(True)
        self.currentIndex += 1
            
        
    def export(self):
        print(self.results)
        path, _ = QFileDialog.getSaveFileName(self, "Save results", os.getcwd(), "JSON(*.json)")
        if path != "":
            with open(path, "w") as output:
                json.dump(self.results, output)
    
    def resultSelected(self, item):
        if self.currentIndex is None:
            self.correctCheck.setEnabled(True)
        self.correctCheck.setChecked(self.results[item])
        self.currentIndex = item
        
    def correctnessChanged(self, state):
         self.results[self.resultsList.currentRow()] = bool(state)
        
        
        
        
        
        
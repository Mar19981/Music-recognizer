import enum, sounddevice as sd, os, pickle, json
from recording import Recording
from PlotWidget import PlotWidget
from PySide6.QtWidgets import (QMainWindow, QGridLayout, QPushButton, QProgressBar, 
                               QVBoxLayout, QHBoxLayout, QLabel, QWidget, QFileDialog,
                               QListWidget, QListWidgetItem, QStackedWidget, QCheckBox
                               )
from PySide6.QtCore import QObject, Signal, QThread, QSize

#Classes for pararel task execution
class RecordingWorker(QObject):
    finished = Signal(None)
    def __init__(self, w) -> None:
        super(RecordingWorker, self).__init__()
        self._parent = w
    def run(self) -> None:
        self._parent.rec.record()
        sd.wait()
        self._parent.rec.prepareRecording()
        self.finished.emit()
        
class PlayWorker(RecordingWorker):
    progress = Signal(int)
    def __init__(self, w) -> None:
        super(PlayWorker, self).__init__(w)
    
    def run(self) -> None:
        self._parent.rec.play()
        sd.wait()
        self.finished.emit()
        
class LoadWorker(RecordingWorker):
    def __init__(self, w) -> None:
        super(LoadWorker, self).__init__(w)
    
    def run(self) -> None:
        self._parent.loadFile()
        self.finished.emit()
        
class DataLoadWorker(RecordingWorker):
    def __init__(self, w) -> None:
        super(DataLoadWorker, self).__init__(w)
    
    def run(self) -> None:
        self._parent.songLabel.setText(u"Loading database...")
        self._parent.songsHashes = pickle.load(open("data/db.pickle", "rb"))
        self._parent.songsIndecies = pickle.load(open("data/songs.pickle", "rb"))
        self.finished.emit()
        

class WorkerType(enum.Enum):
    RECORD = enum.auto()
    PLAY = enum.auto()
    LOAD = enum.auto()
    LOAD_DB = enum.auto()

#GUI class
class MainWindow(QMainWindow):
    def __init__(self) -> None:
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
        self.correctCheck.setChecked(True)
        
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
        
        self.setWindowTitle(u"Music recognizer")
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
        self.currentIndex = None
        
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

    def record(self) -> None:
        devices = sd.query_devices(kind="input")
        if not devices: 
            raise RuntimeError("Failed to find input devices")
        self.createThread(WorkerType.RECORD, self.endRecording)
        self.startButton.setEnabled(False)
        self.thread.start()
        
    def play(self) -> None:
        if self.rec.data is None: 
            return
        self.createThread(WorkerType.PLAY, self.endPlaying)
        self.playButton.setEnabled(False)
        self.thread.start()
    
    def endRecording(self) -> None:
        self.startButton.setEnabled(True)
        self.rec.generateHash(self.fingerprintWidget.axes)
        self.recognizeSong()
        self.__updatePlots()
        
    def __updatePlots(self) -> None:
        self.inputWidget.axes.cla()
        self.inputWidget.axes.plot(self.rec.data)
        self.ftWidget.axes.cla()
        self.rec.plotFFT(self.ftWidget.axes)
        self.inputWidget.draw()
        self.ftWidget.draw()
        self.fingerprintWidget.draw()
        
    def endPlaying(self) -> None:
        self.playButton.setEnabled(True)
    
    def dataLoadingFinished(self) -> None:
        self.startButton.setEnabled(True)
        self.playButton.setEnabled(True)
        self.loadButton.setEnabled(True)
        self.songLabel.setText("Database loading finished!")
    
    def load(self) -> None:
        self.createThread(WorkerType.LOAD, None)
        self.thread.start()
    
    def loadFile(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, u"Open file", os.getcwd(), "Audio file (*.wav *.wave *.flac *.mp3 *.aac *.m4a *.ogg *.oga);;WAV(*.wav *.wave);;FLAC(*.flac);;MP3(*.mp3);;AAC(*.aac *.m4a);;OGG Vorbis(*.ogg *.oga)")
        if path != "":
            self.rec.load(path)
            self.rec.generateHash(self.fingerprintWidget.axes)
            self.recognizeSong()
            self.__updatePlots()
    
    def recognizeSong(self) -> None:

        self.songLabel.setText(u"Recognizing song...")
        
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
        
        songId, score = scores[0]
        
        artist, title, album = self.songsIndecies[songId]
        
        self.songLabel.setText(f"Song: {artist} - {title} [Album: {album}]")
        
        item = QListWidgetItem()
        item.setText(f"{artist} - {title} [Album: {album}]")
        if not self.results:
            self.correctCheck.setEnabled(True)
            
        result = {
            "correct" : True,
            "matches" : [{
                "artist": artist,
                "title": title,
                "album": album,
                "score": score[1],
                "offset": score[0]
            }]
        }
        for i in range(1, 5):
            songId, score = scores[i]
            artist, title, album = self.songsIndecies[songId]
            match = {
                "artist": artist,
                "title": title,
                "album": album,
                "score": score[1],
                "offset": score[0]
            }
            result["matches"].append(match)
            
            
            
        self.results[self.resultsList.count()] = result
        self.resultsList.addItem(item)
            
        
    def export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save results", os.getcwd(), "JSON(*.json)")
        if path != "":
            with open(path, "w") as output:
                json.dump(self.results, output)
    
    def resultSelected(self, item: int) -> None:
        self.correctCheck.setChecked(self.results[item]["correct"])
        self.currentIndex = item
        
    def correctnessChanged(self, state) -> None:
        if self.results and self.currentIndex is not None:
            self.results[self.resultsList.currentRow() if self.resultsList.currentRow() >= 0 else 0]["correct"] = self.correctCheck.isChecked()
        
        
        
        
        
        
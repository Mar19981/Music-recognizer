import enum, sounddevice as sd, os, pickle
from recording import Recording
from PlotWidget import PlotWidget
from PySide6.QtWidgets import QMainWindow, QGridLayout, QPushButton, QProgressBar, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QFileDialog
from PySide6.QtCore import QObject, Signal, QThread, QSize

#Classes for pararel task execution
class RecordingWorker(QObject):
    finished = Signal(None)
    def __init__(self, recording: Recording):
        super(RecordingWorker, self).__init__()
        self._recording = recording
    def run(self) -> None:
        self._recording.record()
        sd.wait()
        self._recording.prepareRecording()
        self.finished.emit()
        
class PlayWorker(RecordingWorker):
    progress = Signal(int)
    def __init__(self, recording: Recording):
        super(PlayWorker, self).__init__(recording)
    
    def run(self) -> None:
        self._recording.play()
        sd.wait()
        self.finished.emit()
        

class WorkerType(enum.Enum):
    RECORD = enum.auto()
    PLAY = enum.auto()

#GUI class
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.resize(1200, 600)
        
        widget = QWidget()
        self.songLabel = QLabel()
        self.inputLabel = QLabel()
        self.fftLabel = QLabel()
        self.fingerprintLabel = QLabel()

        audioLayout = QVBoxLayout()
        audioLayout.setContentsMargins(0, 0, 0, 0)
        buttonsLayout = QHBoxLayout()

        self.startButton = QPushButton()

        buttonsLayout.addWidget(self.startButton)

        self.playButton = QPushButton()

        buttonsLayout.addWidget(self.playButton)

        self.loadButton = QPushButton()

        buttonsLayout.addWidget(self.loadButton)


        audioLayout.addLayout(buttonsLayout)

        
        self.inputWidget = PlotWidget()
        self.ftWidget = PlotWidget()
        self.fingerprintWidget = PlotWidget()
        
        
        layout = QGridLayout()
        
        layout.addWidget(self.inputWidget, 1, 0, 1, 1)
        layout.addWidget(self.ftWidget, 1, 1, 1, 1)
        layout.addWidget(self.fingerprintWidget, 1, 2, 1, 1)
        layout.addWidget(self.songLabel, 2, 0)
        layout.addWidget(self.inputLabel, 0, 0, 1, 1)
        layout.addWidget(self.fftLabel, 0, 1, 1, 1)
        layout.addWidget(self.fingerprintLabel, 0, 2, 1, 1)
        layout.addLayout(audioLayout, 3, 0)
        
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        self.setWindowTitle("Music recognizer")
        self.songLabel.setText(u"Song:")
        self.inputLabel.setText(u"Input:")
        self.fftLabel.setText(u"FFT:")
        self.fingerprintLabel.setText(u"Fingerprint:")
        self.startButton.setText(u"Start recording")
        self.playButton.setText(u"Play recording")
        self.loadButton.setText(u"Load music")
        
        #signals
        
        self.startButton.clicked.connect(self.record)
        self.playButton.clicked.connect(self.play)
        self.loadButton.clicked.connect(self.loadFile)
        self.rec = Recording()
        
        print("UI setup complete")
        print("Loading songs.pickle")
        self.songsIndecies = pickle.load(open("songs.pickle", "rb"))
        print("Loading db.pickle")
        self.songsHashes = pickle.load(open("db.pickle", "rb"))
        print("Setup finished")
        

    def createThread(self, workerType: WorkerType, finishCallback):
        match workerType:
            case WorkerType.RECORD:
                self.worker = RecordingWorker(self.rec)
            case WorkerType.PLAY:
                self.worker = PlayWorker(self.rec)
                
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(finishCallback)

    def record(self):
        devices = sd.query_devices(kind="input")
        if not devices: 
            raise RuntimeError("Failed to find input devices")
        self.createThread(WorkerType.RECORD, self.endRecording)
        self.startButton.setEnabled(False)
        self.thread.start()
        
    def play(self):
        print(self.rec.data)
        print(self.rec.data.shape)
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
        
    def loadFile(self):
        path, _ = QFileDialog.getOpenFileName(self, u"Open file", os.getcwd(), "Audio file (*.wav *.wave *.flac *.mp3 *.aac *.m4a *.ogg *.oga);;WAV(*.wav *.wave);;FLAC(*.flac);;MP3(*.mp3);;AAC(*.aac *.m4a);;OGG Vorbis(*.ogg *.oga)")
        self.rec.load(path)
        print(self.rec.data)
        self.rec.generateHash(self.fingerprintWidget.axes)
        self.recognizeSong()
        self.__updatePlots()
    
    def recognizeSong(self):
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
        
        
        
        
import os
import datetime
import time
from threading import Thread
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from Voice_Reg_Tra import VoiceRegTra, lang_des_list, lang_src_list, multithread_translate, SrtFile


class Subs_View(QMainWindow):

    def __init__(self, srtfile):
        super().__init__()
        self.srtfile = srtfile
        self.subs = srtfile.get_subs()
        # setting title
        self.setWindowTitle(self.srtfile.path)
        wid = QWidget(self)
        self.setCentralWidget(wid)
        layout = QVBoxLayout()
        list_widget = QListWidget()

        for i, sub in enumerate(self.subs):
            txt = f"{i}: {sub.start} : {sub.content}"
            item = QListWidgetItem(txt)
            list_widget.addItem(item)

        self.saveb = QPushButton()
        self.saveb.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.saveb.clicked.connect(self.srtfile.save)
        layout.addWidget(list_widget)
        layout.addWidget(self.saveb)
        wid.setLayout(layout)

        self.show()


def get_smh(sec):
    return str(datetime.timedelta(seconds=sec))


class VideoWindow(QMainWindow):

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.dur = None
        self.path = None
        self.subsview = None
        self.subsview_2 = None
        self.subsview_merged = None
        self.position = 0
        self.setWindowTitle("PyQt Video Player")

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.videoWidget = QVideoWidget()
        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setShortcut(Qt.Key_Space)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.SeekForward = QPushButton()
        self.SeekForward.setEnabled(False)
        self.SeekForward.setShortcut(Qt.Key_Right)
        self.SeekForward.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.SeekForward.clicked.connect(self.seekForwardf)

        self.SeekBackward = QPushButton()
        self.SeekBackward.setEnabled(False)
        self.SeekBackward.setShortcut(Qt.Key_Left)
        self.SeekBackward.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.SeekBackward.clicked.connect(self.seekBackwardf)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.positionSlider.sliderReleased.connect(self.set_translate)

        self.durationlabel = QLabel()
        self.durationlabel.setMaximumHeight(15)
        self.durationlabel_2 = QLabel()
        self.durationlabel_2.setMaximumHeight(15)
        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                                      QSizePolicy.Maximum)
        self.errorLabel.setFont(QFont('Arial', 10))
        self.errorLabel.setMaximumHeight(15)
        self.errorLabel.setAlignment(Qt.AlignCenter)
        self.errorLabel.setWordWrap(True)

        self.lang_des_CB = QComboBox()
        self.lang_des_CB.setMaximumWidth(50)
        self.lang_des_CB.setMaximumHeight(20)

        self.setlang_des = QPushButton()
        self.setlang_des.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.setlang_des.clicked.connect(self.setlang_des_f)
        self.setlang_des.setMaximumWidth(50)
        self.setlang_des.setMaximumHeight(20)

        self.lang_src_CB = QComboBox()
        self.lang_src_CB.setMaximumWidth(50)
        self.lang_src_CB.setMaximumHeight(20)

        self.setlang_src = QPushButton()
        self.setlang_src.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.setlang_src.clicked.connect(self.setlang_src_f)
        self.setlang_src.setMaximumWidth(50)
        self.setlang_src.setMaximumHeight(20)

        self.vollabe = QLabel("Volume :  ")
        self.vollabe.setMaximumHeight(20)
        self.vollabe.setMaximumWidth(50)

        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.sliderMoved.connect(self.setVolume)
        self.volumeSlider.setValue(50)
        self.volumeSlider.setMaximumHeight(20)
        self.volumeSlider.setMaximumWidth(200)

        openAction = QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open movie')
        openAction.triggered.connect(self.openFile)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(openAction)

        show_subs = QAction('&Show Subs', self)
        show_subs.triggered.connect(self.showsubsf)

        set_silence_thresh_b = QAction('&Set Silence_Thresh', self)
        set_silence_thresh_b.triggered.connect(self.set_silence_thresh)

        min_silence_len_b = QAction('&Set Min_Silence_len', self)
        min_silence_len_b.triggered.connect(self.set_min_silence_len)

        setmode1 = QAction('&Start Mode 1', self)
        setmode1.triggered.connect(self.setmode1f)
        setbase = QAction('&Set Base', self)
        setbase.triggered.connect(self.setbasef)

        setmode2 = QAction('&Start Mode 2', self)
        setmode2.triggered.connect(self.setmode2f)

        setbase_2 = QAction('&Set Base 2', self)
        setbase_2.triggered.connect(self.setbase_2f)

        reset_allb = QAction('&Reset', self)
        reset_allb.triggered.connect(self.reset_all)

        savesrt = QAction('&Save SRT', self)
        savesrt.triggered.connect(self.savesrtf)

        multithread_t = QAction('&Multithread Translate', self)
        multithread_t.triggered.connect(self.multithread_tf)

        multithread_t_res = QAction('&Multithread Translate Res', self)
        multithread_t_res.triggered.connect(self.multithread_t_resf)

        multithread_t_2 = QAction('&Multithread Translate 2', self)
        multithread_t_2.triggered.connect(self.multithread_tf_2)

        multithread_t_res_2 = QAction('&Multithread Translate Res 2', self)
        multithread_t_res_2.triggered.connect(self.multithread_t_res_2f)

        multithread_t_merged = QAction('&Multithread Translate Merged', self)
        multithread_t_merged.triggered.connect(self.multithread_t_merged_f)

        multithread_t_res_merged = QAction('&Multithread Translate Merged Res', self)
        multithread_t_res_merged.triggered.connect(self.multithread_t_res_mergedf)

        stop_all = QAction('&Stop All', self)
        stop_all.triggered.connect(self.stop_allf)

        mode_1 = menuBar.addMenu('&Mode 1')
        mode_1.addAction(show_subs)
        mode_1.addAction(min_silence_len_b)
        mode_1.addAction(set_silence_thresh_b)
        mode_1.addAction(setbase)
        mode_1.addAction(setmode1)
        mode_1.addAction(reset_allb)
        mode_1.addAction(savesrt)
        mode_1.addAction(stop_all)

        mode_2 = menuBar.addMenu('&Mode 2')
        mode_2.addAction(show_subs)
        mode_2.addAction(setmode2)
        mode_2.addAction(setbase_2)
        mode_2.addAction(reset_allb)
        mode_2.addAction(savesrt)
        mode_2.addAction(stop_all)

        multithread = menuBar.addMenu('&Multithread')
        multithread.addAction(multithread_t)
        multithread.addAction(multithread_t_res)
        multithread.addAction(multithread_t_2)
        multithread.addAction(multithread_t_res_2)
        multithread.addAction(multithread_t_merged)
        multithread.addAction(multithread_t_res_merged)
        multithread.addAction(stop_all)

        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.durationlabel)
        controlLayout.addWidget(self.SeekBackward)
        controlLayout.addWidget(self.SeekForward)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(self.durationlabel_2)

        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget, 0)
        layout.addWidget(self.errorLabel)
        layout.addLayout(controlLayout)

        volLayout = QHBoxLayout()

        volLayout.addWidget(self.lang_src_CB)
        volLayout.addWidget(self.setlang_src)
        volLayout.addWidget(self.lang_des_CB)
        volLayout.addWidget(self.setlang_des)
        dummy = QWidget()
        volLayout.addWidget(dummy)
        volLayout.addWidget(self.vollabe)
        volLayout.addWidget(self.volumeSlider)

        layout.addLayout(volLayout)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.volumeChanged.connect(self.volumeChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.voiceregtra = None
        self.min_silence_len = 300
        self.silence_thresh = 10
        self.mode = 1
        self.base = 15
        self.base_2 = 5
        self.setAcceptDrops(True)
        self.set_lang_cb()
        self.mtt_list = []
        self.mtt_list_2 = []
        self.mtt_switch = [True]
        self.mtt_switch_2 = [True]
        self.multithread_merged_switch = False

    def stop_allf(self):
        if self.voiceregtra is not None:
            self.voiceregtra.stopall()
            self.mtt_switch[0] = False
            self.mtt_switch_2[0] = False
            self.multithread_merged_switch = False

    def multithread_t_resf(self):
        if len(self.mtt_list) > 0:
            srtfile = SrtFile(self.path)
            for file in self.mtt_list:
                srtfile.allsubs += file.get_srt_file().allsubs
            self.subsview = Subs_View(srtfile)

    def multithread_t_res_2f(self):
        if len(self.mtt_list_2) > 0:
            srtfile = SrtFile(self.path)
            for file in self.mtt_list_2:
                srtfile.allsubs += file.get_srt_file().allsubs
            self.subsview_2 = Subs_View(srtfile)

    def multithread_tf(self):
        if len(self.mtt_list) > 0 and self.mtt_switch[0]:
            qm = QMessageBox
            ret = qm.question(self, '', "Are you sure to stop the Translating ", qm.Yes | qm.No)
            if ret == qm.Yes:
                self.mtt_switch[0] = False
            self.multithread_merged_switch = False
            return False
        else:
            self.mtt_list = []
            self.mtt_switch[0] = True
            num, okPressed = QInputDialog.getInt(self, "Set threads count", "threads :", 10)
            if okPressed:
                multithread_translate(self.path, self.lang_src_CB.currentData(), self.lang_des_CB.currentData(),
                                      1,
                                      self.mtt_list, self.mtt_switch,
                                      min_silence_len=self.min_silence_len,
                                      silence_thresh=self.silence_thresh,
                                      base=self.base,
                                      base_2=self.base_2,
                                      num=num
                                      )
            return True

    def multithread_tf_2(self):
        if len(self.mtt_list_2) > 0 and self.mtt_switch_2[0]:
            qm = QMessageBox
            ret = qm.question(self, '', "Are you sure to stop the Translating", qm.Yes | qm.No)
            if ret == qm.Yes:
                self.mtt_switch_2[0] = False
                self.multithread_merged_switch = False
            return False

        else:
            self.mtt_list_2 = []
            self.mtt_switch_2[0] = True
            num, okPressed = QInputDialog.getInt(self, "Set threads count", "threads :", 10)
            if okPressed:
                multithread_translate(self.path, self.lang_src_CB.currentData(),
                                      self.lang_des_CB.currentData(),
                                      2,
                                      self.mtt_list_2,
                                      self.mtt_switch_2,
                                      min_silence_len=self.min_silence_len,
                                      silence_thresh=self.silence_thresh,
                                      base=self.base,
                                      base_2=self.base_2,
                                      num=num)
            return True

    def multithread_t_merged_f(self):
        def in_thread():

            while self.mtt_switch[0] or self.mtt_switch_2[0]:
                time.sleep(1)
            if self.multithread_merged_switch:
                srtfile = SrtFile(self.path)
                srtfile_2 = SrtFile(self.path)

                for file in self.mtt_list:
                    srtfile.allsubs += file.get_srt_file().allsubs

                for file in self.mtt_list_2:
                    srtfile_2.allsubs += file.get_srt_file().allsubs

                srtfile.updata(srtfile_2,dur=self.dur)
                srtfile.sort_subs()
                srtfile.save()
                print("Multithread Merged Finished")
            else:
                print("Multithread Merged Canceled")
        if self.multithread_merged_switch:
            qm = QMessageBox
            ret = qm.question(self, '', "Are you sure to stop the Translating", qm.Yes | qm.No)
            if ret == qm.Yes:
                self.mtt_switch_2[0] = False
                self.mtt_switch[0] = False
                self.multithread_merged_switch = False

        else:
            self.multithread_merged_switch = True
            self.mtt_list_2 = []
            self.mtt_switch_2[0] = True
            self.mtt_list = []
            self.mtt_switch[0] = True
            if self.multithread_tf():
                if self.multithread_tf_2():
                    Thread(target=in_thread).start()

    def multithread_t_res_mergedf(self):
        srtfile = SrtFile(self.path)
        srtfile_2 = SrtFile(self.path)

        for file in self.mtt_list:
            srtfile.allsubs += file.get_srt_file().allsubs

        for file in self.mtt_list_2:
            srtfile_2.allsubs += file.get_srt_file().allsubs

        srtfile.updata(srtfile_2, dur=self.dur)
        srtfile.sort_subs()

        self.subsview_merged = Subs_View(srtfile)
    def savesrtf(self):
        if self.voiceregtra:
            self.voiceregtra.savesrt()

    def setmode1f(self):
        if self.voiceregtra:
            self.mode = 1
            self.voiceregtra.setmode(1)
            current = int(self.mediaPlayer.position() / 1000)
            self.voiceregtra.startall(current)

    def setmode2f(self):
        if self.voiceregtra:
            self.mode = 2
            current = int(self.mediaPlayer.position() / 1000)
            self.voiceregtra.setmode(2)
            self.voiceregtra.startall(current)

    def setbasef(self):

        base, okPressed = QInputDialog.getInt(self, "Set value", "Base:", self.base)
        if okPressed:
            self.base = int(base)
            if self.voiceregtra:
                self.voiceregtra.setbase(base)

    def setbase_2f(self):

        base, okPressed = QInputDialog.getInt(self, "Set value", "Base:", self.base_2)
        if okPressed:
            self.base_2 = int(base)
            if self.voiceregtra:
                self.voiceregtra.setbase_2(base)

    def reset_all(self):
        if self.voiceregtra:
            current = int(self.mediaPlayer.position() / 1000)
            self.voiceregtra.reset(current)

    def set_min_silence_len(self):
        min_silence_len, okPressed = QInputDialog.getInt(self, "Set value", "min_silence_len:", self.min_silence_len)
        if okPressed:
            self.min_silence_len = int(min_silence_len)
            if self.voiceregtra:
                self.voiceregtra.min_silence_len = int(min_silence_len)

    def set_silence_thresh(self):
        silence_thresh, okPressed = QInputDialog.getInt(self, "Set value", "silence_thresh:", self.silence_thresh)
        if okPressed:
            self.silence_thresh = int(silence_thresh)
            if self.voiceregtra:
                self.voiceregtra.silence_thresh = int(silence_thresh)

    def set_translate(self):
        if self.voiceregtra:
            current = int(self.mediaPlayer.position() / 1000)
            self.voiceregtra.startall(current)

    def setlang_des_f(self):
        if self.voiceregtra:
            lang = self.lang_des_CB.currentData()
            self.voiceregtra.set_lang_des(lang)
            self.voiceregtra.reset_translate()

    def setlang_src_f(self):
        if self.voiceregtra:
            lang = self.lang_src_CB.currentData()
            self.voiceregtra.set_lang_src(lang)
            current = int(self.mediaPlayer.position() / 1000)
            self.voiceregtra.reset(current)

    def showsubsf(self):
        if self.voiceregtra:
            self.subsview = Subs_View(self.voiceregtra.get_srt_file())

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            self.openvideofile(f)

    def set_lang_cb(self):
        self.lang_des_CB.clear()
        self.lang_src_CB.clear()
        for lang in lang_des_list:
            self.lang_des_CB.addItem(lang, lang)
        for lang in lang_src_list:
            self.lang_src_CB.addItem(lang, lang)

    def seekForwardf(self):
        newpos = self.position + 5000
        self.setPosition(newpos)

    def seekBackwardf(self):
        newpos = self.position - 5000
        self.setPosition(newpos)

    def openvideofile(self, fileName):
        self.voiceregtra = VoiceRegTra(fileName, self.lang_src_CB.currentData(), self.lang_des_CB.currentData())
        if not self.voiceregtra.audio:
            print("file has no audio ")
            self.errorLabel.setText("file has no audio ")
            return
        name = os.path.basename(fileName)
        self.path = fileName
        self.setWindowTitle(f"Video Translator : {name}")

        if self.voiceregtra:
            self.voiceregtra.stopall()

        self.mediaPlayer.setMedia(
            QMediaContent(QUrl.fromLocalFile(fileName)))

        self.position = 0

        self.voiceregtra.mode = self.mode
        self.voiceregtra.base = self.base
        self.voiceregtra.silence_thresh = self.silence_thresh
        self.voiceregtra.min_silence_len = self.min_silence_len
        self.dur = int(self.voiceregtra.dur)
        text = f"{get_smh(int(self.voiceregtra.dur))}"
        self.durationlabel_2.setText(text)
        self.set_duration_label(0)

        self.playButton.setEnabled(True)
        self.SeekBackward.setEnabled(True)
        self.SeekForward.setEnabled(True)
        self.lang_src_CB.setEnabled(True)
        self.lang_des_CB.setEnabled(True)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                                                  QDir.homePath())

        if fileName != '':
            self.openvideofile(fileName)

    def closeEvent(self, event):
        if self.voiceregtra is not None:
            self.voiceregtra.stopall()
            self.mtt_switch[0] = False
            self.mtt_switch_2[0] = False

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        elif self.mediaPlayer.state() == QMediaPlayer.StoppedState:
            self.mediaPlayer.play()
            lang = self.lang_src_CB.currentData()
            self.voiceregtra.set_lang_src(lang)
            lang = self.lang_des_CB.currentData()
            self.voiceregtra.set_lang_des(lang)
            self.voiceregtra.startall(0)
        elif self.mediaPlayer.state() == QMediaPlayer.PausedState:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    def set_duration_label(self, msec):
        sec = int(msec / 1000)
        text = f"{get_smh(sec)}/ {get_smh(self.voiceregtra.getlastsec())} Mode {self.voiceregtra.mode} ="
        self.durationlabel.setText(text)

    def positionChanged(self, position):
        self.position = position
        self.positionSlider.setValue(position)
        msec = self.mediaPlayer.position()

        if self.voiceregtra:
            text = self.voiceregtra.get_sub(msec)
            self.set_duration_label(msec)
            self.errorLabel.setText(text)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def volumeChanged(self, position):
        self.volumeSlider.setValue(position)

    def setVolume(self, position):
        self.mediaPlayer.setVolume(position)

    def setPosition(self, position):
        self.position = position
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())




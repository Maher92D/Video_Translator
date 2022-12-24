import sys
from Video_Player import VideoWindow
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    if len(sys.argv) > 1:
        player.openvideofile(sys.argv[1])
    player.resize(800, 600)
    player.show()
    sys.exit(app.exec_())


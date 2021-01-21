from PyQt5.Qt import *
import sys
from MainWindowLogic import *
from ServerClientLogic import *


class MainWindow(QmyWidget, TcpLogic, UdpLogic):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.link_signal.connect(self.tcp_server_start())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

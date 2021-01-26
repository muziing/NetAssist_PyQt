from PyQt5.Qt import *
import sys
from MainWindowLogic import *
from ServerClientLogic import *


class MainWindow(QmyWidget, TcpLogic, UdpLogic):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.link_signal.connect(self.link_signal_handler)
        self.tcp_signal_write_msg.connect(self.msg_write)
        self.udp_signal_write_msg.connect(self.msg_write)

    def link_signal_handler(self, signal):
        """
        发送信号分用的槽函数
        :return: None
        """
        link_type, target_ip, my_port, target_port = signal
        if link_type == 0:
            self.tcp_server_start(my_port)
        elif link_type == 1:
            self.tcp_client_start(target_ip, target_port)
        elif link_type == 2:
            self.udp_server_start(my_port)
        elif link_type == 3:
            self.udp_client_start(target_ip, target_port)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

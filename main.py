from PyQt5.Qt import *
import sys
from MainWindowLogic import *
from ServerClientLogic import *


class MainWindow(QmyWidget, TcpLogic, UdpLogic):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.link_signal.connect(self.link_signal_handler)
        self.disconnect_signal.connect(self.disconnect_signal_handler)
        self.tcp_signal_write_msg.connect(self.msg_write)
        self.udp_signal_write_msg.connect(self.msg_write)
        self.send_signal.connect(self.send_signal_handler)

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

    def disconnect_signal_handler(self):
        self.tcp_close()
        self.udp_close()

    def send_signal_handler(self, msg):
        if self.link_flag == 0 or self.link_flag == 1:
            self.tcp_send(msg)
        elif self.link_flag == 3:
            self.udp_send(msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

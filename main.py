import sys

from PyQt5.QtWidgets import QApplication

from MainWindowLogic import *
from Network import TcpLogic, UdpLogic, WebLogic


class MainWindow(QmyWidget, TcpLogic, UdpLogic, WebLogic):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.link_signal.connect(self.link_signal_handler)
        self.disconnect_signal.connect(self.disconnect_signal_handler)
        self.send_signal.connect(self.send_signal_handler)
        self.tcp_signal_write_msg.connect(self.msg_write)
        self.tcp_signal_write_info.connect(self.info_write)
        self.udp_signal_write_msg.connect(self.msg_write)
        self.udp_signal_write_info.connect(self.info_write)

    def link_signal_handler(self, signal):
        """
        发送信号分用的槽函数
        :return: None
        """
        link_type, target_ip, port = signal
        if link_type == self.ServerTCP:
            self.tcp_server_start(port)
        elif link_type == self.ClientTCP:
            self.tcp_client_start(target_ip, port)
        elif link_type == self.ServerUDP:
            self.udp_server_start(port)
        elif link_type == self.ClientUDP:
            self.udp_client_start(target_ip, port)
        elif link_type == self.WebServer:
            self.web_server_start(port)

    def disconnect_signal_handler(self):
        """
        断开连接的槽函数
        :return: None
        """
        if self.link_flag == self.ServerTCP or self.link_flag == self.ClientTCP:
            self.tcp_close()
        elif self.link_flag == self.ServerUDP or self.link_flag == self.ClientUDP:
            self.udp_close()
        elif self.link_flag == self.WebServer:
            self.web_close()
            # TODO 解决Webserver线程无法正常关闭问题

    def send_signal_handler(self, msg):
        """
        发送按钮的槽函数
        :return: None
        """
        if self.link_flag == self.ServerTCP or self.link_flag == self.ClientTCP:
            self.tcp_send(msg)
            self.SendCounter += 1
        elif self.link_flag == self.ClientUDP:
            self.udp_send(msg)
            self.SendCounter += 1
        self.counter_signal.emit(self.SendCounter, self.ReceiveCounter)

    def closeEvent(self, event) -> None:
        """
        重写closeEvent方法，实现MainWindow窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        self.disconnect_signal_handler()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

import socket
import threading

from PyQt5.QtCore import pyqtSignal

from . import StopThreading


def get_host_ip() -> str:
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


class UdpLogic:
    udp_signal_write_msg = pyqtSignal(str)
    udp_signal_write_info = pyqtSignal(str, int)

    def __init__(self):
        self.link_flag = False
        self.udp_socket = None
        self.address = None
        self.sever_th = None
        self.client_th = None

    def udp_server_start(self, port) -> None:
        """
        开启UDP服务端方法
        """
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        port = int(port)
        address = ("", port)
        self.udp_socket.bind(address)
        self.sever_th = threading.Thread(target=self.udp_server_concurrency)
        self.sever_th.start()
        msg = "UDP服务端正在监听端口:{}\n".format(port)
        self.udp_signal_write_msg.emit(msg)

    def udp_server_concurrency(self) -> None:
        """
        用于创建一个线程持续监听UDP通信
        """
        while True:
            recv_msg, recv_addr = self.udp_socket.recvfrom(1024)
            info = recv_msg.decode("utf-8")
            msg = f"来自IP:{recv_addr[0]}端口:{recv_addr[1]}:"
            self.udp_signal_write_msg.emit(msg)
            self.udp_signal_write_info.emit(info, self.InfoRec)

    def udp_client_start(self, ip: str, port: int) -> None:
        """
        确认UDP客户端的ip及地址
        """
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = (ip, port)
        msg = "UDP客户端已启动\n"
        self.udp_signal_write_msg.emit(msg)

    def udp_send(self, send_info: str) -> None:
        """
        功能函数，用于UDP客户端发送消息
        """
        try:
            send_info_encoded = send_info.encode("utf-8")
            self.udp_socket.sendto(send_info_encoded, self.address)
            msg = "UDP客户端已发送"
            self.udp_signal_write_msg.emit(msg)
            self.udp_signal_write_info.emit(send_info, self.InfoSend)
        except Exception as ret:
            msg = "发送失败\n"
            self.udp_signal_write_msg.emit(msg)

    def udp_close(self) -> None:
        """
        功能函数，关闭网络连接的方法
        """
        if self.link_flag == self.ServerUDP:
            try:
                self.udp_socket.close()
                msg = "已断开网络\n"
                self.udp_signal_write_msg.emit(msg)
            except Exception as ret:
                pass

            try:
                StopThreading.stop_thread(self.sever_th)
            except Exception:
                pass

        if self.link_flag == self.ClientUDP:
            try:
                self.udp_socket.close()
                msg = "已断开网络\n"
                self.udp_signal_write_msg.emit(msg)
            except Exception as ret:
                pass

            try:
                StopThreading.stop_thread(self.client_th)
            except Exception:
                pass

    NoLink = -1
    ServerUDP = 2
    ClientUDP = 3
    InfoSend = 0
    InfoRec = 1

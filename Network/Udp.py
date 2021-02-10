import socket
import threading

from PyQt5.QtCore import pyqtSignal

from Network import StopThreading


def get_host_ip() -> str:
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


class UdpLogic:
    udp_signal_write_info = pyqtSignal(str)
    udp_signal_write_msg = pyqtSignal(str)
    # TODO 数据与提交信息分离

    def __init__(self):
        self.link_flag = False
        self.udp_socket = None
        self.address = None
        self.sever_th = None
        self.client_th = None

    def udp_server_start(self, port):
        """
        开启UDP服务端方法
        :return:
        """
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        port = int(port)
        address = ('', port)
        self.udp_socket.bind(address)
        self.sever_th = threading.Thread(target=self.udp_server_concurrency)
        self.sever_th.start()
        info = 'UDP服务端正在监听端口:{}\n'.format(port)
        self.udp_signal_write_info.emit(info)

    def udp_server_concurrency(self):
        """
        用于创建一个线程持续监听UDP通信
        :return:
        """
        while True:
            recv_msg, recv_addr = self.udp_socket.recvfrom(1024)
            msg = recv_msg.decode('utf-8')
            info = f'来自IP:{recv_addr[0]}端口:{recv_addr[1]}:'
            self.udp_signal_write_info.emit(info)
            self.udp_signal_write_msg.emit(msg)

    def udp_client_start(self, ip: str, port: int):
        """
        确认UDP客户端的ip及地址
        :return:
        """
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = (ip, port)
        info = 'UDP客户端已启动\n'
        self.udp_signal_write_info.emit(info)

    def udp_send(self, send_msg: str):
        """
        功能函数，用于UDP客户端发送消息
        :return: None
        """
        try:
            send_msg = send_msg.encode('utf-8')
            self.udp_socket.sendto(send_msg, self.address)
            info = 'UDP客户端已发送\n'
            self.udp_signal_write_info.emit(info)
        except Exception as ret:
            info = '发送失败\n'
            self.udp_signal_write_info.emit(info)

    def udp_close(self):
        """
        功能函数，关闭网络连接的方法
        :return:
        """
        if self.link_flag == self.ServerUDP:
            try:
                self.udp_socket.close()
                info = '已断开网络\n'
                self.udp_signal_write_info.emit(info)
            except Exception as ret:
                pass

            try:
                StopThreading.stop_thread(self.sever_th)
            except Exception:
                pass

        if self.link_flag == self.ClientUDP:
            try:
                self.udp_socket.close()
                info = '已断开网络\n'
                self.udp_signal_write_info.emit(info)
            except Exception as ret:
                pass

            try:
                StopThreading.stop_thread(self.client_th)
            except Exception:
                pass

    NoLink = -1
    ServerUDP = 2
    ClientUDP = 3
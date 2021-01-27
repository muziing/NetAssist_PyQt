import socket
import threading

from PyQt5.QtCore import pyqtSignal

import StopThreading


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
    udp_signal_write_msg = pyqtSignal(str)

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
        try:
            port = int(port)
            address = ('', port)
            self.udp_socket.bind(address)
        except Exception as ret:
            msg = '请检查端口号\n'
            self.udp_signal_write_msg.emit(msg)
        else:
            self.sever_th = threading.Thread(target=self.udp_server_concurrency)
            self.sever_th.start()
            msg = 'UDP服务端正在监听端口:{}\n'.format(port)
            self.udp_signal_write_msg.emit(msg)

    def udp_server_concurrency(self):
        """
        用于创建一个线程持续监听UDP通信
        :return:
        """
        while True:
            recv_msg, recv_addr = self.udp_socket.recvfrom(1024)
            msg = recv_msg.decode('utf-8')
            msg = '来自IP:{}端口:{}:\n{}\n'.format(recv_addr[0], recv_addr[1], msg)
            self.udp_signal_write_msg.emit(msg)

    def udp_client_start(self, ip, port):
        """
        确认UDP客户端的ip及地址
        :return:
        """
        # TODO UDP客户端可绑定本机端口
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.address = (str(ip), int(port))
        except Exception as ret:
            msg = '请检查目标IP，目标端口\n'
            self.udp_signal_write_msg.emit(msg)
        else:
            msg = 'UDP客户端已启动\n'
            self.udp_signal_write_msg.emit(msg)

    def udp_send(self, send_msg):
        """
        功能函数，用于UDP客户端发送消息
        :return: None
        """
        if self.link_flag == -1:
            msg = '请选择服务，并点击连接网络\n'
            self.udp_signal_write_msg.emit(msg)
        else:
            try:
                send_msg = send_msg.encode('utf-8')
                self.udp_socket.sendto(send_msg, self.address)
                msg = 'UDP客户端已发送\n'
                self.udp_signal_write_msg.emit(msg)
            except Exception as ret:
                msg = '发送失败\n'
                self.udp_signal_write_msg.emit(msg)

    def udp_close(self):
        """
        功能函数，关闭网络连接的方法
        :return:
        """
        if self.link_flag == self.ServerUDP:
            try:
                self.udp_socket.close()
                msg = '已断开网络\n'
                self.udp_signal_write_msg.emit(msg)
                # TODO 系统会报错，需要修bug
            except Exception as ret:
                pass

        elif self.link_flag == self.ClientUDP:
            try:
                self.udp_socket.close()
                msg = '已断开网络\n'
                self.udp_signal_write_msg.emit(msg)
            except Exception as ret:
                pass
            try:
                StopThreading.stop_thread(self.sever_th)
            except Exception:
                pass
            try:
                StopThreading.stop_thread(self.client_th)
            except Exception:
                pass

    NoLink = -1
    ServerUDP = 2
    ClientUDP = 3

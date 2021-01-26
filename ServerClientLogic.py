import socket
import threading
import time

from PyQt5.QtCore import pyqtSignal

import stopThreading


def get_host_ip() -> str:
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


class TcpLogic:
    tcp_signal_write_msg = pyqtSignal(str)

    def __init__(self):
        self.tcp_socket = None
        self.sever_th = None
        self.client_th = None
        self.client_socket_list = list()

        self.link = False  # 用于标记是否开启了连接

    def tcp_server_start(self, port):
        """
        功能函数，TCP服务端开启的方法
        :return: None
        """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 取消主动断开连接四次握手后的TIME_WAIT状态
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 设定套接字为非阻塞式
        self.tcp_socket.setblocking(False)
        try:
            port = int(port)
            self.tcp_socket.bind(('', port))
        except Exception as ret:
            msg = '请检查端口号\n'
            self.tcp_signal_write_msg.emit(msg)
        else:
            self.tcp_socket.listen()
            self.sever_th = threading.Thread(target=self.tcp_server_concurrency)
            self.sever_th.start()
            msg = 'TCP服务端正在监听端口:%s\n' % str(port)
            self.tcp_signal_write_msg.emit(msg)

    def tcp_server_concurrency(self):
        """
        功能函数，供创建线程的方法；
        使用子线程用于监听并创建连接，使主线程可以继续运行，以免无响应
        使用非阻塞式并发用于接收客户端消息，减少系统资源浪费，使软件轻量化
        :return:None
        """
        while True:
            try:
                client_socket, client_address = self.tcp_socket.accept()
            except Exception as ret:
                time.sleep(0.001)
            else:
                client_socket.setblocking(False)
                # 将创建的客户端套接字存入列表,client_address为ip和端口的元组
                self.client_socket_list.append((client_socket, client_address))
                msg = f'TCP服务端已连接IP:{client_address}端口:{client_socket}\n'
                self.tcp_signal_write_msg.emit(msg)
            # 轮询客户端套接字列表，接收数据
            for client, address in self.client_socket_list:
                try:
                    recv_msg = client.recv(1024)
                except Exception as ret:
                    pass
                else:
                    if recv_msg:
                        msg = recv_msg.decode('utf-8')
                        msg = '来自IP:{}端口:{}:\n{}\n'.format(address[0], address[1], msg)
                        self.tcp_signal_write_msg.emit(msg)
                    else:
                        client.close()
                        self.client_socket_list.remove((client, address))

    def tcp_client_start(self, ip, port):
        """
        功能函数，TCP客户端连接其他服务端的方法
        :return:
        """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            address = (str(ip), int(port))
        except Exception as ret:
            msg = '请检查目标IP，目标端口\n'
            self.tcp_signal_write_msg.emit(msg)
        else:
            try:
                msg = '正在连接目标服务器\n'
                self.tcp_signal_write_msg.emit(msg)
                self.tcp_socket.connect(address)
            except Exception as ret:
                msg = '无法连接目标服务器\n'
                self.tcp_signal_write_msg.emit(msg)
            else:
                self.client_th = threading.Thread(target=self.tcp_client_concurrency, args=(address,))
                self.client_th.start()
                msg = 'TCP客户端已连接IP:%s端口:%s\n' % address
                self.tcp_signal_write_msg.emit(msg)

    def tcp_client_concurrency(self, address):
        """
        功能函数，用于TCP客户端创建子线程的方法，阻塞式接收
        :return:
        """
        while True:
            recv_msg = self.tcp_socket.recv(1024)
            if recv_msg:
                msg = recv_msg.decode('utf-8')
                msg = '来自IP:{}端口:{}:\n{}\n'.format(address[0], address[1], msg)
                self.tcp_signal_write_msg.emit(msg)
            else:
                self.tcp_socket.close()
                self.reset()
                msg = '从服务器断开连接\n'
                self.tcp_signal_write_msg.emit(msg)
                break

    def tcp_send(self, send_msg):
        """
        功能函数，用于TCP服务端和TCP客户端发送消息
        :return: None
        """
        if self.link is False:
            msg = '请选择服务，并点击连接网络\n'
            self.tcp_signal_write_msg.emit(msg)
        else:
            try:
                send_msg = send_msg.encode('utf-8')
                if self.comboBox_tcp.currentIndex() == 0:
                    # 向所有连接的客户端发送消息
                    for client, address in self.client_socket_list:
                        client.send(send_msg)
                    msg = 'TCP服务端已发送\n'
                    self.tcp_signal_write_msg.emit(msg)
                if self.comboBox_tcp.currentIndex() == 1:
                    self.tcp_socket.send(send_msg)
                    msg = 'TCP客户端已发送\n'
                    self.tcp_signal_write_msg.emit(msg)
            except Exception as ret:
                msg = '发送失败\n'
                self.tcp_signal_write_msg.emit(msg)

    def tcp_close(self):
        """
        功能函数，关闭网络连接的方法
        :return:
        """
        if self.comboBox_tcp.currentIndex() == 0:
            try:
                for client, address in self.client_socket_list:
                    client.close()
                self.tcp_socket.close()
                if self.link is True:
                    msg = '已断开网络\n'
                    self.signal_write_msg.emit(msg)
            except Exception as ret:
                pass
        if self.comboBox_tcp.currentIndex() == 1:
            try:
                self.tcp_socket.close()
                if self.link is True:
                    msg = '已断开网络\n'
                    self.tcp_signal_write_msg.emit(msg)
            except Exception as ret:
                pass
        try:
            stopThreading.stop_thread(self.sever_th)
        except Exception:
            pass
        try:
            stopThreading.stop_thread(self.client_th)
        except Exception:
            pass


class UdpLogic:
    udp_signal_write_msg = pyqtSignal(str)

    def __init__(self):
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
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.address = (str(ip), int(port))
        except Exception as ret:
            msg = '请检查目标IP，目标端口\n'
            self.udp_signal_write_msg.emit(msg)
        else:
            msg = 'UDP客户端已启动\n'
            self.udp_signal_write_msg.emit(msg)

    def udp_send(self):
        """
        功能函数，用于UDP客户端发送消息
        :return: None
        """
        if self.link_flag is False:
            msg = '请选择服务，并点击连接网络\n'
            self.udp_signal_write_msg.emit(msg)
        else:
            try:
                send_msg = (str(self.textEdit_send.toPlainText())).encode('utf-8')
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
        try:
            self.udp_socket.close()
            if self.link is True:
                msg = '已断开网络\n'
                self.udp_signal_write_msg.emit(msg)
        except Exception as ret:
            pass
        try:
            self.udp_socket.close()
            if self.link is True:
                msg = '已断开网络\n'
                self.udp_signal_write_msg.emit(msg)
        except Exception as ret:
            pass
        try:
            stopThreading.stop_thread(self.sever_th)
        except Exception:
            pass
        try:
            stopThreading.stop_thread(self.client_th)
        except Exception:
            pass


if __name__ == '__main__':
    print((get_host_ip()))

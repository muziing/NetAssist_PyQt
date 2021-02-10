import socket
import threading
from time import sleep

from PyQt5.QtCore import pyqtSignal

from Network import StopThreading


class TcpLogic:
    tcp_signal_write_info = pyqtSignal(str)
    tcp_signal_write_msg = pyqtSignal(str)

    def __init__(self):
        self.tcp_socket = None
        self.sever_th = None
        self.client_th = None
        self.client_socket_list = list()
        self.link_flag = self.NoLink  # 用于标记是否开启了连接

    def tcp_server_start(self, port: int):
        """
        功能函数，TCP服务端开启的方法
        :return: None
        """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 取消主动断开连接四次握手后的TIME_WAIT状态
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 设定套接字为非阻塞式
        self.tcp_socket.setblocking(False)
        self.tcp_socket.bind(('', port))
        self.tcp_socket.listen(5)  # 限制最大连接数
        self.sever_th = threading.Thread(target=self.tcp_server_concurrency)
        self.sever_th.start()
        info = 'TCP服务端正在监听端口:%s\n' % str(port)
        self.tcp_signal_write_info.emit(info)

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
                sleep(0.002)
            else:
                client_socket.setblocking(False)
                # 将创建的客户端套接字存入列表,client_address为ip和端口的元组
                self.client_socket_list.append((client_socket, client_address))
                info = f'TCP服务端已连接IP:{client_address[0]}端口:{client_address[1]}\n'
                self.tcp_signal_write_info.emit(info)
            # 轮询客户端套接字列表，接收数据
            for client, address in self.client_socket_list:
                try:
                    recv_msg = client.recv(4096)
                except Exception as ret:
                    pass
                else:
                    if recv_msg:
                        msg = recv_msg.decode('utf-8')
                        info = f'来自IP:{address[0]}端口:{address[1]}:'
                        self.tcp_signal_write_info.emit(info)
                        self.tcp_signal_write_msg.emit(msg)
                    else:
                        client.close()
                        self.client_socket_list.remove((client, address))

    def tcp_client_start(self, ip: str, port: int):
        """
        功能函数，TCP客户端连接其他服务端的方法
        :return:
        """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = (ip, port)
        try:
            info = '正在连接目标服务器\n'
            self.tcp_signal_write_info.emit(info)
            self.tcp_socket.connect(address)
        except Exception as ret:
            info = '无法连接目标服务器\n'
            self.tcp_signal_write_info.emit(info)
        else:
            self.client_th = threading.Thread(target=self.tcp_client_concurrency, args=(address,))
            self.client_th.start()
            info = 'TCP客户端已连接IP:%s端口:%s\n' % address
            self.tcp_signal_write_info.emit(info)

    def tcp_client_concurrency(self, address) -> None:
        """
        功能函数，用于TCP客户端创建子线程的方法，阻塞式接收
        :return: None
        """
        while True:
            recv_msg = self.tcp_socket.recv(4096)
            if recv_msg:
                msg = recv_msg.decode('utf-8')
                info = f'来自IP:{address[0]}端口:{address[1]}:'
                self.tcp_signal_write_info.emit(info)
                self.tcp_signal_write_msg.emit(msg)
            else:
                self.tcp_socket.close()
                info = '从服务器断开连接\n'
                self.tcp_signal_write_info.emit(info)
                break

    def tcp_send(self, send_msg: str) -> None:
        """
        功能函数，用于TCP服务端和TCP客户端发送消息
        :return: None
        """
        try:
            send_msg = send_msg.encode('utf-8')
            if self.link_flag == self.ServerTCP:
                # 向所有连接的客户端发送消息
                if self.client_socket_list:
                    for client, address in self.client_socket_list:
                        try:
                            client.send(send_msg)
                        except Exception as ret:
                            # 处理Client异常掉线的情况
                            continue
                    info = 'TCP服务端已发送\n'
                    self.tcp_signal_write_info.emit(info)
            if self.link_flag == self.ClientTCP:
                self.tcp_socket.send(send_msg)
                info = 'TCP客户端已发送\n'
                self.tcp_signal_write_info.emit(info)
        except Exception as ret:
            info = '发送失败\n'
            self.tcp_signal_write_info.emit(info)

    def tcp_close(self) -> None:
        """
        功能函数，关闭网络连接的方法
        :return: None
        """
        if self.link_flag == self.ServerTCP:
            for client, address in self.client_socket_list:
                client.shutdown(2)
                client.close()
            self.client_socket_list = list()  # 把已连接的客户端列表重新置为空列表
            self.tcp_socket.close()
            info = '已断开网络\n'
            self.tcp_signal_write_info.emit(info)

            try:
                StopThreading.stop_thread(self.sever_th)
            except Exception as ret:
                pass

        elif self.link_flag == self.ClientTCP:
            try:
                self.tcp_socket.shutdown(2)
                self.tcp_socket.close()
                info = '已断开网络\n'
                self.tcp_signal_write_info.emit(info)
            except Exception as ret:
                pass

            try:
                StopThreading.stop_thread(self.client_th)
            except Exception as ret:
                pass

    NoLink = -1
    ServerTCP = 0
    ClientTCP = 1

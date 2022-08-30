import socket
import threading
from time import sleep

from PyQt5.QtCore import pyqtSignal

from . import StopThreading


class TcpLogic:
    tcp_signal_write_info = pyqtSignal(str, int)
    tcp_signal_write_msg = pyqtSignal(str)

    def __init__(self):
        self.tcp_socket = None
        self.sever_th = None
        self.client_th = None
        self.client_socket_list = list()
        self.link_flag = self.NoLink  # 用于标记是否开启了连接

    def tcp_server_start(self, port: int) -> None:
        """
        功能函数，TCP服务端开启的方法
        """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 取消主动断开连接四次握手后的TIME_WAIT状态
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 设定套接字为非阻塞式
        self.tcp_socket.setblocking(False)
        self.tcp_socket.bind(("", port))
        self.tcp_socket.listen(5)  # 限制最大连接数
        self.sever_th = threading.Thread(target=self.tcp_server_concurrency)
        self.sever_th.start()
        msg = "TCP服务端正在监听端口:%s\n" % str(port)
        self.tcp_signal_write_msg.emit(msg)

    def tcp_server_concurrency(self):
        """
        功能函数，供创建线程的方法；
        使用子线程用于监听并创建连接，使主线程可以继续运行，以免无响应
        使用非阻塞式并发用于接收客户端消息，减少系统资源浪费，使软件轻量化

        :return: None
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
                msg = f"TCP服务端已连接IP:{client_address[0]}端口:{client_address[1]}\n"
                self.tcp_signal_write_msg.emit(msg)
            # 轮询客户端套接字列表，接收数据
            for client, address in self.client_socket_list:
                try:
                    recv_msg = client.recv(4096)
                except Exception as ret:
                    pass
                else:
                    if recv_msg:
                        info = recv_msg.decode("utf-8")
                        msg = f"来自IP:{address[0]}端口:{address[1]}:"
                        self.tcp_signal_write_msg.emit(msg)
                        self.tcp_signal_write_info.emit(info, self.InfoRec)

                    else:
                        client.close()
                        self.client_socket_list.remove((client, address))

    def tcp_client_start(self, ip: str, port: int) -> None:
        """
        功能函数，TCP客户端连接其他服务端的方法
        """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = (ip, port)
        try:
            msg = "正在连接目标服务器……\n"
            self.tcp_signal_write_msg.emit(msg)
            self.tcp_socket.connect(address)
        except Exception as ret:
            msg = "无法连接目标服务器\n"
            self.tcp_signal_write_msg.emit(msg)
        else:
            self.client_th = threading.Thread(
                target=self.tcp_client_concurrency, args=(address,)
            )
            self.client_th.start()
            msg = "TCP客户端已连接IP:%s端口:%s\n" % address
            self.tcp_signal_write_msg.emit(msg)

    def tcp_client_concurrency(self, address) -> None:
        """
        功能函数，用于TCP客户端创建子线程的方法，阻塞式接收
        """
        while True:
            recv_msg = self.tcp_socket.recv(4096)
            if recv_msg:
                info = recv_msg.decode("utf-8")
                msg = f"来自IP:{address[0]}端口:{address[1]}:"
                self.tcp_signal_write_msg.emit(msg)
                self.tcp_signal_write_info.emit(info, self.InfoRec)
            else:
                self.tcp_socket.close()
                msg = "从服务器断开连接\n"
                self.tcp_signal_write_msg.emit(msg)
                break

    def tcp_send(self, send_info: str) -> None:
        """
        功能函数，用于TCP服务端和TCP客户端发送消息
        """
        try:
            send_info_encoded = send_info.encode("utf-8")
            if self.link_flag == self.ServerTCP:
                # 向所有连接的客户端发送消息
                if self.client_socket_list:
                    for client, address in self.client_socket_list:
                        client.send(send_info_encoded)
                    msg = "TCP服务端已发送"
                    self.tcp_signal_write_msg.emit(msg)
                    self.tcp_signal_write_info.emit(send_info, self.InfoSend)
            if self.link_flag == self.ClientTCP:
                self.tcp_socket.send(send_info_encoded)
                msg = "TCP客户端已发送"
                self.tcp_signal_write_msg.emit(msg)
                self.tcp_signal_write_info.emit(send_info, self.InfoSend)
        except Exception as ret:
            msg = "发送失败\n"
            self.tcp_signal_write_msg.emit(msg)

    def tcp_close(self) -> None:
        """
        功能函数，关闭网络连接的方法
        """
        if self.link_flag == self.ServerTCP:
            for client, address in self.client_socket_list:
                client.shutdown(socket.SHUT_RDWR)
                client.close()
            self.client_socket_list = list()  # 把已连接的客户端列表重新置为空列表
            self.tcp_socket.close()
            msg = "已断开网络\n"
            self.tcp_signal_write_msg.emit(msg)

            try:
                StopThreading.stop_thread(self.sever_th)
            except Exception as ret:
                pass

        elif self.link_flag == self.ClientTCP:
            try:
                self.tcp_socket.shutdown(socket.SHUT_RDWR)
                self.tcp_socket.close()
                msg = "已断开网络\n"
                self.tcp_signal_write_msg.emit(msg)
            except Exception as ret:
                pass

            try:
                StopThreading.stop_thread(self.client_th)
            except Exception as ret:
                pass

    NoLink = -1
    ServerTCP = 0
    ClientTCP = 1
    InfoSend = 0
    InfoRec = 1

import socket
import sys
import threading


def get_host_ip() -> str:
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


class ServerTCP:
    def __init__(self, host='0.0.0.0'):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s = s
            # 防止socket server 重启后端口被占用 (socket.error: [Error 98] Address already in use)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, 7777))
            s.listen(10)
        except socket.error as msg:
            print(msg)
            sys.exit(1)
        print("Waiting connection...")

    def start(self):
        while True:
            self.conn, self.addr = self.s.accept()
            t = threading.Thread(target=deal_data, args=(self.conn, self.addr))
            t.start()


def deal_data(conn, addr):
    print(f"Accept new connection from {addr}")
    conn.send("Hi, Welcome to the server!".encode())
    while True:
        data = conn.recv(1024)
        print(f"{addr} client send data is {data.decode()}")
        # time.sleep(1)
        if not data:
            print(f"{addr} connection close")
            conn.send(bytes("Connection closed!", 'UTF-8'))
            break
        conn.send(bytes(f"Hello, {data}", "UTF-8"))
    conn.close()


class ClientTCP:
    def __init__(self, target_ip: str, target_host: int):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s = s
            s.connect((target_ip, target_host))
        except socket.error as msg:
            print(msg)
            sys.exit(1)

    def start(self):
        while True:
            data = input('please input work: ').encode()
            self.s.send(data)
            print('aa', self.s.recv(1024))

    def stop(self):
        self.s.close()


if __name__ == '__main__':
    print((get_host_ip()))

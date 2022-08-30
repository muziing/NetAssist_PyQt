from .Tcp import TcpLogic
from .Udp import UdpLogic, get_host_ip
from .WebServer import WebLogic


class NetworkLogic(TcpLogic, UdpLogic, WebLogic):
    """
    综合了TCP UDP WebServer 的类
    """
    pass

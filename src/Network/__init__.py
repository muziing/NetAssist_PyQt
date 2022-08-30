from src.Network.Tcp import TcpLogic
from src.Network.Udp import UdpLogic
from src.Network.WebServer import WebLogic


class NetworkLogic(TcpLogic, UdpLogic, WebLogic):
    """
    综合了TCP UDP WebServer 的类
    """

    pass

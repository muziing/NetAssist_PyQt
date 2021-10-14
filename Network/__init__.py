from Network.Tcp import TcpLogic
from Network.Udp import UdpLogic, get_host_ip
from Network.WebServer import WebLogic


class NetworkLogic(TcpLogic, UdpLogic, WebLogic):
    """
    综合了TCP UDP WebServer 的类
    """

    pass

from PyQt5.QtCore import Qt, QRegExp, pyqtSignal
from PyQt5.QtGui import QIcon, QIntValidator, QValidator, QRegExpValidator
from PyQt5.QtWidgets import QWidget, QMessageBox
import MainWindowUI
import ServerClientLogic


class QmyWidget(QWidget, ServerClientLogic.TcpLogic, ServerClientLogic.UdpLogic):
    # link_signal = pyqtSignal((int, str, int, int))  # 连接类型, 目标IP, 本机端口, 目标端口
    link_signal = pyqtSignal(tuple)  # 连接类型, 目标IP, 本机端口, 目标端口
    disconnect_signal = pyqtSignal()
    send_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__ui = MainWindowUI.Ui_Form()
        self.__ui.setupUi(self)
        self.__ui.retranslateUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # 保持窗口最前
        self.__ui.MyIPLineEdit.setText(ServerClientLogic.get_host_ip())
        self.set_validator()
        self.setup_connect_button()
        self.link_flag = self.NoLink
        self.__ui.ConnectButton.clicked.connect(self.setup_connect_button)
        self.__ui.SendButton.clicked.connect(self.send_link)

    def set_validator(self):
        """为IP与端口的QLineEdit设置验证器"""

        class PortValidator(QIntValidator):
            def fixup(self, input: str) -> str:
                if len(input) == 0:
                    return ''
                elif int(input) > 65535:
                    return '7777'
                return input

        class IPValidator(QRegExpValidator):
            def validate(self, input: str, pos: int) -> [QValidator.State, str, int]:
                input = input.replace('。', '.')
                return super().validate(input, pos)

        validator_1 = PortValidator(0, 65535, self.__ui.TargetPortLineEdit)
        self.__ui.TargetPortLineEdit.setValidator(validator_1)
        self.__ui.MyPortLineEdit.setValidator(validator_1)
        reg_ex = QRegExp("((2[0-4]\\d|25[0-5]|[01]?\\d\\d?)\\.){3}(2[0-4]\\d|25[0-5]|[01]?\\d\\d?)")
        ip_input_validator = IPValidator(reg_ex, self.__ui.TargetIPLineEdit)
        self.__ui.TargetIPLineEdit.setValidator(ip_input_validator)

    def setup_connect_button(self):
        button = self.__ui.ConnectButton
        button.setCheckable(True)
        if not button.isChecked():
            button.setText("连接网络")
            self.click_disconnect()
            self.editable(True)
        else:
            button.setText("断开连接")
            self.click_link()
            self.editable(False)

    def editable(self, able: bool = True):
        """当连接建立后，部分选项不可再修改"""
        self.__ui.ProtocolTypeComboBox.setDisabled(not able)
        self.__ui.MyPortLineEdit.setReadOnly(not able)
        self.__ui.TargetIPLineEdit.setReadOnly(not able)
        self.__ui.TargetPortLineEdit.setReadOnly(not able)

    def click_link(self):
        """
        ConnectButton控件点击触发的槽
        :return: None
        """
        server_flag = False  # 如果没有输入目标IP与端口号，则作为Server使用
        protocol_type_index = self.__ui.ProtocolTypeComboBox.currentIndex()
        target_ip = str(self.__ui.TargetIPLineEdit.text())

        def get_int_port(port):
            # 用户未输入端口则置为-1
            return -1 if port == '' else int(port)

        my_port = get_int_port(self.__ui.MyPortLineEdit.text())
        target_port = get_int_port(self.__ui.TargetPortLineEdit.text())

        if target_port == -1 and target_ip == '':
            server_flag = True
        elif target_port == -1 and target_ip != '':
            mb = QMessageBox(QMessageBox.Critical, 'Client启动错误', '请输入目标端口号', QMessageBox.Ok, self)
            mb.open()
            self.__ui.ConnectButton.setChecked(False)
            # TODO 连接按钮复原
            # 提前终止槽函数
            return None
        elif target_port != -1 and target_ip == '':
            mb = QMessageBox(QMessageBox.Critical, 'Client启动错误', '请输入目标IP地址', QMessageBox.Ok, self)
            mb.open()
            self.__ui.ConnectButton.setChecked(False)
            # TODO 连接按钮复原
            # 提前终止槽函数
            return None

        if protocol_type_index == 0 and server_flag:
            self.link_signal.emit((self.ServerTCP, '', my_port, target_port))
            self.link_flag = self.ServerTCP
            self.__ui.StateLabel.setText("TCP服务端")
        elif protocol_type_index == 0 and not server_flag:
            self.link_signal.emit((self.ClientTCP, target_ip, my_port, target_port))
            self.link_flag = self.ClientTCP
            self.__ui.StateLabel.setText("TCP客户端")
        elif protocol_type_index == 1 and server_flag:
            self.link_signal.emit((self.ServerUDP, '', my_port, target_port))
            self.link_flag = self.ServerUDP
            self.__ui.StateLabel.setText("UDP服务端")
        elif protocol_type_index == 1 and not server_flag:
            self.link_signal.emit((self.ClientUDP, target_ip, my_port, target_port))
            self.link_flag = self.ClientUDP
            self.__ui.StateLabel.setText("UDP客户端")
        self.editable(False)  # 建立连接后不可再修改参数

    def send_link(self):
        """
        SendButton控件点击触发的槽
        :return: None
        """
        send_msg = self.__ui.SendPlainTextEdit.toPlainText()
        self.send_signal.emit(send_msg)

    def msg_write(self, msg):
        """
        将接收到的消息写入ReceivePlainTextEdit
        :return: None
        """
        self.__ui.ReceivePlainTextEdit.appendPlainText(msg)

    def click_disconnect(self):
        self.disconnect_signal.emit()
        self.link_flag = -1
        self.__ui.StateLabel.setText("未连接")

    NoLink = -1
    ServerTCP = 0
    ClientTCP = 1
    ServerUDP = 2
    ClientUDP = 3

from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog

from Network.UdpLogic import get_host_ip
from UI import MainWindowUI


class QmyWidget(QWidget):
    # link_signal = pyqtSignal((int, str, int, int))  # 连接类型, 目标IP, 本机端口, 目标端口
    link_signal = pyqtSignal(tuple)  # 连接类型, 目标IP, 本机/目标端口
    disconnect_signal = pyqtSignal()
    send_signal = pyqtSignal(str)
    counter_signal = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__ui = MainWindowUI.Ui_Form()
        self.__ui.setupUi(self)
        self.__ui.retranslateUi(self)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # 保持窗口最前
        self.__ui.MyHostAddrLineEdit.setText(get_host_ip())

        self.link_flag = self.NoLink
        self.SendCounter = 0
        self.ReceiveCounter = 0

        self.counter_signal.connect(self.counter_signal_handler)
        self.__ui.ConnectButton.toggled.connect(self.connect_button_toggled_handler)
        self.__ui.SendButton.clicked.connect(self.send_link_handler)
        self.__ui.RSaveDataButton.clicked.connect(self.r_save_data_button_handler)
        self.__ui.CounterResetLabel.clicked.connect(self.counter_reset_button_handler)
        self.__ui.ReceivePauseCheckBox.toggled.connect(self.receive_pause_checkbox_toggled_handler)

    def connect_button_toggled_handler(self, state):
        if state:
            self.click_link_handler()
        else:
            self.click_disconnect()
            self.editable(True)

    def editable(self, able: bool = True):
        """当连接建立后，部分选项不可再修改"""
        self.__ui.ProtocolTypeComboBox.setDisabled(not able)
        self.__ui.MyPortLineEdit.setReadOnly(not able)
        self.__ui.TargetIPLineEdit.setReadOnly(not able)
        self.__ui.TargetPortLineEdit.setReadOnly(not able)

    def click_link_handler(self):
        """
        ConnectButton控件点击触发的槽
        :return: None
        """
        server_flag = False  # 如果没有输入目标IP与端口号，则作为Server使用
        protocol_type_text = self.__ui.ProtocolTypeComboBox.currentText()
        target_ip = str(self.__ui.TargetIPLineEdit.text())

        def get_int_port(port):
            # 用户未输入端口则置为-1
            return -1 if port == '' else int(port)

        my_port = get_int_port(self.__ui.MyPortLineEdit.text())
        target_port = get_int_port(self.__ui.TargetPortLineEdit.text())
        self.editable(False)  # 建立连接后不可再修改参数

        # TODO 对用户同时输入了本机IP目标IP目标端口的情况进行异常处理

        if my_port == -1 and target_port == -1 and target_ip == '':
            mb = QMessageBox(QMessageBox.Critical, '错误', '请输入信息', QMessageBox.Ok, self)
            mb.open()
            self.editable(True)
            self.__ui.ConnectButton.setChecked(False)
            return None
        if target_port == -1 and target_ip == '':
            server_flag = True
        elif target_port == -1 and target_ip != '':
            mb = QMessageBox(QMessageBox.Critical, 'Client启动错误', '请输入目标端口号', QMessageBox.Ok, self)
            mb.open()
            # TODO 把MessageBox 改为 InputDialog
            self.__ui.ConnectButton.setChecked(False)
            self.editable(True)
            # 提前终止槽函数
            return None
        elif target_port != -1 and target_ip == '':
            mb = QMessageBox(QMessageBox.Critical, 'Client启动错误', '请输入目标IP地址', QMessageBox.Ok, self)
            mb.open()
            self.__ui.ConnectButton.setChecked(False)
            self.editable(True)
            # 提前终止槽函数
            return None

        if protocol_type_text == "TCP" and server_flag:
            self.link_signal.emit((self.ServerTCP, '', my_port))
            self.link_flag = self.ServerTCP
            self.__ui.StateLabel.setText("TCP服务端")
        elif protocol_type_text == "TCP" and not server_flag:
            self.link_signal.emit((self.ClientTCP, target_ip, target_port))
            self.link_flag = self.ClientTCP
            self.__ui.StateLabel.setText("TCP客户端")
        elif protocol_type_text == "UDP" and server_flag:
            self.link_signal.emit((self.ServerUDP, '', my_port))
            self.link_flag = self.ServerUDP
            self.__ui.StateLabel.setText("UDP服务端")
            # TODO 作为UDP服务端时禁用发送
        elif protocol_type_text == "UDP" and not server_flag:
            self.link_signal.emit((self.ClientUDP, target_ip, target_port))
            self.link_flag = self.ClientUDP
            self.__ui.StateLabel.setText("UDP客户端")

    def send_link_handler(self):
        """
        SendButton控件点击触发的槽
        :return: None
        """
        if self.link_flag != self.NoLink:
            loop_flag = self.__ui.LoopSendCheckBox.checkState()
            send_msg = self.__ui.SendPlainTextEdit.toPlainText()
            if loop_flag == 0:
                self.send_signal.emit(send_msg)
            elif loop_flag == 2:
                send_timer = QTimer(self)
                send_timer.start(int(self.__ui.LoopSendSpinBox.text()))
                send_timer.timeout.connect(lambda: self.send_signal.emit(send_msg))
                self.__ui.LoopSendCheckBox.stateChanged.connect(lambda val: send_timer.stop() if val == 0 else None)
                self.__ui.ConnectButton.toggled.connect(lambda val: None if val else send_timer.stop())

            # TODO 十六进制发送

    def msg_write(self, msg):
        """
        将接收到的消息写入ReceivePlainTextEdit
        :return: None
        """
        self.__ui.ReceivePlainTextEdit.appendPlainText(msg)
        self.ReceiveCounter += 1
        self.counter_signal.emit(self.SendCounter, self.ReceiveCounter)
        # TODO 十六进制接收

    def click_disconnect(self):
        self.disconnect_signal.emit()
        self.link_flag = self.NoLink
        self.__ui.StateLabel.setText("未连接")

    def counter_signal_handler(self, send_count, receive_count):
        self.__ui.SendCounterLabel.setText(str(send_count))
        self.__ui.ReceiveCounterLabel.setText(str(receive_count))

    # TODO 发送接收计数器

    def counter_reset_button_handler(self):
        self.SendCounter = 0
        self.ReceiveCounter = 0
        self.counter_signal.emit(self.SendCounter, self.ReceiveCounter)

    def r_save_data_button_handler(self):
        """
        接收设置保存数据按键的槽函数
        :return: None
        """
        text = self.__ui.ReceivePlainTextEdit.toPlainText()
        file_name = QFileDialog.getSaveFileName(self, "保存到txt", "./", "ALL(*, *);;txt文件(*.txt)", "txt文件(*.txt)")[0]
        try:
            with open(file_name, mode='w') as f:
                f.write(text)
        except FileNotFoundError:
            pass  # 如果用户取消输入，filename为空，会出现FileNotFoundError

    def receive_pause_checkbox_toggled_handler(self, ste: bool):
        """
        暂停接受复选框的槽函数
        :return: None
        """
        pass
        # TODO 实现暂停接收功能
        if ste:
            pass  # 暂时断开ReceivePlainTextEdit连接的信号
        else:
            self.__ui.ReceivePlainTextEdit.blockSignals(False)  # 恢复连接

    # TODO 最小化到托盘

    NoLink = -1
    ServerTCP = 0
    ClientTCP = 1
    ServerUDP = 2
    ClientUDP = 3


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = QmyWidget()
    window.show()
    sys.exit(app.exec_())

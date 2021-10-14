from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget

from Network import get_host_ip
from UI import MainWindowUI
from UI.MyWidgets import PortInputDialog


class WidgetLogic(QWidget):
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
        self.__ui.MyHostAddrLineEdit.setText(get_host_ip())  # 显示本机IP地址

        self.protocol_type = "TCP"
        self.link_flag = self.NoLink
        self.receive_show_flag = True  # 是否显示接收到的消息
        self.SendCounter = 0
        self.ReceiveCounter = 0
        self.dir = None

        self.counter_signal.connect(self.counter_signal_handler)
        self.__ui.ProtocolTypeComboBox.activated[str].connect(
            self.protocol_type_combobox_handler
        )
        self.__ui.ConnectButton.toggled.connect(self.connect_button_toggled_handler)
        self.__ui.SendButton.clicked.connect(self.send_link_handler)
        self.__ui.OpenFilePushButton.clicked.connect(self.open_file_handler)
        self.__ui.RSaveDataButton.clicked.connect(self.r_save_data_button_handler)
        self.__ui.CounterResetLabel.clicked.connect(self.counter_reset_button_handler)
        self.__ui.ReceivePauseCheckBox.toggled.connect(
            self.receive_pause_checkbox_toggled_handler
        )

    def connect_button_toggled_handler(self, state):
        if state:
            # 连接按钮连接
            self.click_link_handler()
        else:
            # 连接按钮断开连接
            self.click_disconnect()
            self.editable(True)

    def editable(self, able: bool = True):
        """当连接建立后，部分选项不可再修改"""
        self.__ui.ProtocolTypeComboBox.setDisabled(not able)
        self.__ui.MyPortLineEdit.setReadOnly(not able)
        self.__ui.TargetIPLineEdit.setReadOnly(not able)
        self.__ui.TargetPortLineEdit.setReadOnly(not able)

    def protocol_type_combobox_handler(self, p_type):
        """ProtocolTypeComboBox的槽函数"""
        self.protocol_type = p_type
        if self.protocol_type == "Web Server":
            self.__ui.SendPlainTextEdit.setPlainText("请打开index.html所在的文件路径")
            self.__ui.SendPlainTextEdit.setEnabled(False)
            self.__ui.OpenFilePushButton.setText("选择路径")
        else:
            # 恢复发送输入框可用
            self.__ui.SendPlainTextEdit.setEnabled(True)
            self.__ui.SendPlainTextEdit.clear()
            self.__ui.OpenFilePushButton.setText("打开文件")

    def click_link_handler(self):
        """连接按钮连接时的槽函数"""
        server_flag = False  # 如果没有输入目标IP与端口号，则作为Server使用
        target_ip = str(self.__ui.TargetIPLineEdit.text())

        def get_int_port(port):
            # 用户未输入端口则置为-1
            return -1 if port == "" else int(port)

        my_port = get_int_port(self.__ui.MyPortLineEdit.text())
        target_port = get_int_port(self.__ui.TargetPortLineEdit.text())
        self.editable(False)  # 建立连接后不可再修改参数

        if my_port == -1 and target_port == -1 and target_ip == "":
            mb = QMessageBox(QMessageBox.Critical, "错误", "请输入信息", QMessageBox.Ok, self)
            mb.open()
            self.editable(True)
            self.__ui.ConnectButton.setChecked(False)
            return None
        elif my_port != -1 and target_port != -1 and target_ip != "":
            mb = QMessageBox(
                QMessageBox.Critical, "错误", "输入的信息过多", QMessageBox.Ok, self
            )
            mb.open()
            self.editable(True)
            self.__ui.ConnectButton.setChecked(False)
            return None
        elif target_port == -1 and target_ip == "":
            server_flag = True
        elif target_port == -1 and target_ip != "":
            input_d = PortInputDialog(self)
            input_d.setWindowTitle("服务启动失败")
            input_d.setLabelText("请输入目标端口号作为Client启动，或取消")
            input_d.intValueSelected.connect(
                lambda val: self.__ui.TargetPortLineEdit.setText(str(val))
            )
            input_d.open()
            self.__ui.ConnectButton.setChecked(False)
            # 提前终止槽函数
            return None
        elif target_port != -1 and target_ip == "":
            mb = QMessageBox(
                QMessageBox.Critical, "Client启动错误", "请输入目标IP地址", QMessageBox.Ok, self
            )
            mb.open()
            self.__ui.ConnectButton.setChecked(False)
            # 提前终止槽函数
            return None
        if self.protocol_type == "Web Server" and not self.dir:
            # 处理用户未选择工作路径情况下连接网络
            self.dir = QFileDialog.getExistingDirectory(self, "选择index.html所在路径", "./")
            if self.dir:
                self.__ui.SendPlainTextEdit.clear()
                self.__ui.SendPlainTextEdit.appendPlainText(str(self.dir))
                self.__ui.SendPlainTextEdit.setEnabled(False)
            else:
                self.__ui.ConnectButton.setChecked(False)
                return None

        if self.protocol_type == "TCP" and server_flag:
            self.link_signal.emit((self.ServerTCP, "", my_port))
            self.link_flag = self.ServerTCP
            self.__ui.StateLabel.setText("TCP服务端")
        elif self.protocol_type == "TCP" and not server_flag:
            self.link_signal.emit((self.ClientTCP, target_ip, target_port))
            self.link_flag = self.ClientTCP
            self.__ui.StateLabel.setText("TCP客户端")
        elif self.protocol_type == "UDP" and server_flag:
            self.link_signal.emit((self.ServerUDP, "", my_port))
            self.link_flag = self.ServerUDP
            self.__ui.StateLabel.setText("UDP服务端")
            # TODO 作为UDP服务端时禁用发送
        elif self.protocol_type == "UDP" and not server_flag:
            self.link_signal.emit((self.ClientUDP, target_ip, target_port))
            self.link_flag = self.ClientUDP
            self.__ui.StateLabel.setText("UDP客户端")
        elif self.protocol_type == "Web Server" and server_flag and self.dir:
            self.link_signal.emit((self.WebServer, "", my_port))
            self.link_flag = self.WebServer
            self.__ui.StateLabel.setText("Web server")

    def send_link_handler(self):
        """
        SendButton控件点击触发的槽
        """
        if self.link_flag != self.NoLink:
            loop_flag = self.__ui.LoopSendCheckBox.checkState()  # 循环发送标识
            send_msg = self.__ui.SendPlainTextEdit.toPlainText()
            if loop_flag == 0:
                self.send_signal.emit(send_msg)
            elif loop_flag == 2:
                send_timer = QTimer(self)
                send_timer.start(int(self.__ui.LoopSendSpinBox.value()))
                send_timer.timeout.connect(lambda: self.send_signal.emit(send_msg))
                self.__ui.LoopSendCheckBox.stateChanged.connect(
                    lambda val: send_timer.stop() if val == 0 else None
                )
                self.__ui.ConnectButton.toggled.connect(
                    lambda val: None if val else send_timer.stop()
                )  # 断开连接停止计时

    def msg_write(self, msg: str):
        """将提示消息写入ReceivePlainTextEdit"""
        # TODO 显示接收时间
        if self.receive_show_flag:
            self.__ui.ReceivePlainTextEdit.appendPlainText(msg)

    def info_write(self, info: str, mode: int):
        """
        将接收到或已发送的消息写入ReceivePlainTextEdit
        :param info: 接收或发送的消息
        :param mode: 模式，接收/发送
        :return: None
        """
        if self.receive_show_flag:
            if mode == self.InfoRec:
                self.__ui.ReceivePlainTextEdit.appendHtml(
                    f'<font color="blue">{info}</font>'
                )
                self.ReceiveCounter += 1
                self.counter_signal.emit(self.SendCounter, self.ReceiveCounter)
            elif mode == self.InfoSend:
                self.__ui.ReceivePlainTextEdit.appendHtml(
                    f'<font color="green">{info}</font>'
                )
            self.__ui.ReceivePlainTextEdit.appendHtml("\n")
        else:
            if mode == self.InfoRec:
                self.ReceiveCounter += 1
                self.counter_signal.emit(self.SendCounter, self.ReceiveCounter)

    def click_disconnect(self):
        self.disconnect_signal.emit()
        self.link_flag = self.NoLink
        self.__ui.StateLabel.setText("未连接")

    def counter_signal_handler(self, send_count, receive_count):
        """控制收发计数器显示变化的槽函数"""
        self.__ui.SendCounterLabel.setText(str(send_count))
        self.__ui.ReceiveCounterLabel.setText(str(receive_count))

    def counter_reset_button_handler(self):
        """清零收发计数器的槽函数"""
        self.SendCounter = 0
        self.ReceiveCounter = 0
        self.counter_signal.emit(self.SendCounter, self.ReceiveCounter)

    def open_file_handler(self):
        if self.link_flag in [self.ServerTCP, self.ClientTCP, self.ClientUDP]:
            # 打开文本文件，加载到发送PlainTextEdit
            def read_file(file_dir):
                if file_dir:
                    try:
                        with open(file_dir, "r", encoding="UTF8") as f:
                            self.__ui.SendPlainTextEdit.clear()
                            self.__ui.SendPlainTextEdit.appendPlainText(f.read())
                    except UnicodeDecodeError:
                        #  如果不能用UTF8解码
                        mb = QMessageBox(
                            QMessageBox.Critical,
                            "无法读取文件",
                            "无法读取文件，请检查输入",
                            QMessageBox.Ok,
                            self,
                        )
                        mb.open()

            fd = QFileDialog(self, "选择一个文件", "./", "文本文件(*, *)")
            fd.setAcceptMode(QFileDialog.AcceptOpen)
            fd.setFileMode(QFileDialog.ExistingFile)
            fd.fileSelected.connect(read_file)
            fd.open()

        elif self.link_flag == self.NoLink and self.protocol_type == "Web Server":
            self.dir = QFileDialog.getExistingDirectory(self, "选择index.html所在路径", "./")
            self.__ui.SendPlainTextEdit.clear()
            self.__ui.SendPlainTextEdit.appendPlainText(str(self.dir))
            self.__ui.SendPlainTextEdit.setEnabled(False)

    def r_save_data_button_handler(self):
        """接收设置保存数据按键的槽函数"""
        text = self.__ui.ReceivePlainTextEdit.toPlainText()
        file_name = QFileDialog.getSaveFileName(
            self, "保存到txt", "./", "ALL(*, *);;txt文件(*.txt)", "txt文件(*.txt)"
        )[0]
        try:
            with open(file_name, mode="w") as f:
                f.write(text)
        except FileNotFoundError:
            pass  # 如果用户取消输入，filename为空，会出现FileNotFoundError

    def receive_pause_checkbox_toggled_handler(self, ste: bool):
        """暂停接受复选框的槽函数"""
        if ste:
            self.receive_show_flag = False
        else:
            self.receive_show_flag = True

    # TODO 最小化到托盘

    NoLink = -1
    ServerTCP = 0
    ClientTCP = 1
    ServerUDP = 2
    ClientUDP = 3
    WebServer = 4
    InfoSend = 0
    InfoRec = 1


if __name__ == "__main__":
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = WidgetLogic()
    window.show()
    sys.exit(app.exec_())

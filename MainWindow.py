from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QIntValidator, QValidator
from PyQt5.QtWidgets import QWidget
import MainWindowUI
import MySocket


class QmyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__ui = MainWindowUI.Ui_Form()
        self.__ui.setupUi(self)
        self.__ui.retranslateUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # 保持窗口最前
        self.setWindowIcon(QIcon('UI/Network.png'))
        self.__ui.MyIPLineEdit.setText(MySocket.get_host_ip())
        self.set_validator()

    def set_validator(self):
        """为IP与端口的QLineEdit设置验证器"""
        class PortValidator(QIntValidator):
            def fixup(self, input: str) -> str:
                if len(input) == 0:
                    return ''
                elif int(input) > 65535:
                    return '7777'
                return input

        class IPValidator(QValidator):
            pass

        validator_1 = PortValidator(0, 65535, self.__ui.TargetPortLineEdit)
        self.__ui.TargetPortLineEdit.setValidator(validator_1)
        self.__ui.MyPortLineEdit.setValidator(validator_1)
        # validator_2 = IPValidator(self.__ui.TargetIPLineEdit)
        # self.__ui.TargetIPLineEdit.setValidator(validator_2)

    def editable(self, able: bool = True):
        """当连接建立后，部分选项不可再修改"""
        if not able:
            self.__ui.MyPortLineEdit.setReadOnly(True)
            self.__ui.TargetIPLineEdit.setReadOnly(True)
            self.__ui.TargetPortLineEdit.setReadOnly(True)



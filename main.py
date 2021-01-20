from PyQt5.Qt import *
import sys
from MainWindow import *


def main():
    app = QApplication(sys.argv)
    window = QmyWidget()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

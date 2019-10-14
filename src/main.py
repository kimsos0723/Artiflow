import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic

import mainwindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = mainwindow.WindowClass()
    myWindow.show()
    app.exec_()

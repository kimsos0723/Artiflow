import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
form_class = uic.loadUiType('../Views/MainWindow.ui')[0]

class WindowClass(QMainWindow, form_class):    
    """
    Main Window Class
  
    """
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.initMenu(self)
        #Path https://pythonspot.com/pyqt5-file-dialog/
    
    def initMenu(self,_) :
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        helpMenu = mainMenu.addMenu('&Help')
        
        #File menu
        NewFile = QAction('&Add File',self)
        NewFile.triggered.connect(self.openFileNameDialog)
        #Help menu
        fileMenu.addAction(NewFile)

    def openFileNameDialog(self,_) :
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Open DB File", "", "DB Files (*.db);;All Files (*)",options=options)
        if fileName:
            msg = QMessageBox()
            msg.setText(fileName)
            msg.exec_()
        else : 
            msg = QMessageBox()
            msg.setText("Cannot Open !")
            msg.exec_()

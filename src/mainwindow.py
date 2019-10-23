from Controller.db_controller import *

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic

from Views import Ui_MainWindow as Ui
# form_class = uic.loadUiType('./Views/MainWindow.ui')[0]
class WindowClass(QMainWindow, Ui.Ui_MainWindow):    
    """
    Main Window Class
    """
    
    DBfilePaths = []

    def __init__(self):
        super().__init__()        
        self.setupUi(self)
        self.initUi(self)
        
    def initUi(self, _):
        self.initManu(self)

    def initManu(self, _):     
        mainManu = self.menuBar()
        fileManu = mainManu.addMenu('&File')
        viewManu = mainManu.addMenu('&View')
        helpManu = mainManu.addMenu('&Help')

        #file menu
        AddFile = QAction('&Add File',self)
        AddFile.triggered.connect(self.AddfileAction)
        fileManu.addAction(AddFile)
        
    def AddfileAction(self, _):
        path = ""
        path = self.openFileNameDialog(self)    
        if path == "" :
            return
        
        self.tabWidget.addTab(QTreeView(), self.DBfilePaths[-1].split('/')[-1])

    def openFileNameDialog(self,_):
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self,"Open DB File", "", "DB Files (*.db);;All Files (*)",options=options)

        try:          
            msg = QMessageBox()
            msg.setText(path)
            msg.exec_()
            self.DBfilePaths.append(path) 
        except Exception as e:
            msg = QMessageBox()
            msg.setText("Cannot Open !")            
            msg.exec_()
        
    def addTreeView(self, _):
           
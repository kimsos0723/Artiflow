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
    Databases = []    
    def __init__(self):
        super().__init__()        
        self.setupUi(self)
        self.initMenu(self)    
        
    def initMenu(self,_) :
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        helpMenu = mainMenu.addMenu('&Help')
        
        #File menucle
        NewFile = QAction('&Add File',self)
        NewFile.triggered.connect(self.openFileNameDialog)
        #Help menu
        fileMenu.addAction(NewFile)

    def openFileNameDialog(self,_) :
        options = QFileDialog.Options()
        # options |= QFileDialog.
        fileName, _ = QFileDialog.getOpenFileName(self,"Open DB File", "", "DB Files (*.db);;All Files (*)",options=options)
        if fileName:            
            msg = QMessageBox()
            msg.setText(fileName)
            msg.exec_()
            # db_ctr = DBController(fileName)
            # try:
            #     names, result = db_ctr.excute_sql('delete')            
            # except Exception as e:
            #     print(str(e))
            #     return
            # self.tableWidget.setColumnCount(len(names))
            # self.tableWidget.setRowCount(0)
            # self.tableWidget.setHorizontalHeaderLabels(names)    
            # for row_num, row_data in enumerate(result):
            #     self.tableWidget.insertRow(row_num)
            #     for column_num, data in enumerate(row_data):
            #         self.tableWidget.setItem(row_num, column_num, QTableWidgetItem(str(data)))
            # #Get Tables
            # _, result = db_ctr.excute_sql('SELECT name from sqlite_master where type= "table"')
            # print(result)
        else :
            msg = QMessageBox()
            msg.setText("Cannot Open !")
            msg.exec_()
        
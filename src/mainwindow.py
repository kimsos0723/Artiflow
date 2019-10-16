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
        self.initMenu(self)    
        
        
    def initMenu(self,_) :
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        helpMenu = mainMenu.addMenu('&Help')
        
        #File menucle
        AddFile = QAction('&Add File',self)
        AddFile.triggered.connect(self.AddFileAction)
        #Help menu
        fileMenu.addAction(AddFile)
        #TreeWidget Header
        self.tableWidget.setVerticalHeaderLabels(["Databases"])
        
        
    def AddFileAction(self, _):
        self.openFileNameDialog(self)
        self.addTreeWidgetItems(self)

    def openFileNameDialog(self,_) :
        options = QFileDialog.Options()    
        path, _ = QFileDialog.getOpenFileName(self,"Open DB File", "", "DB Files (*.db);;All Files (*)",options=options)
        if path:            
            msg = QMessageBox()
            msg.setText(path)
            msg.exec_()
            self.DBfilePaths.append(path)              
        else :
            msg = QMessageBox()
            msg.setText("Cannot Open !")
            msg.exec_()
    
    def addTreeWidgetItems(self, _) :
        db_ctr = DBController(self.DBfilePaths[0])
        #Get Tables
        _, result = db_ctr.excute_sql('SELECT name from sqlite_master where type= "table"')
        self.treeWidget.setColumnCount(len(self.DBfilePaths))
        root_item = QTreeWidgetItem([self.DBfilePaths[0].split('/')[-1]])
        self.treeWidget.addTopLevelItem(root_item)
        for i in result:
            QTreeWidgetItem(root_item, list(i))
                        
    def loadTable(self, _):
        try:
            names, result = db_ctr.excute_sql()
        except Exception as e:
            print(str(e))
            return            

        self.tableWidget.setRowCount(0)            
        self.tableWidget.setColumnCount(len(names))                
        for row_num, row_data in enumerate(result):
            self.tableWidget.insertRow(row_num)
            for column_num, data in enumerate(row_data):
                self.tableWidget.setItem(row_num, column_num, QTableWidgetItem(str(data)))
      
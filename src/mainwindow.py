import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic

from Controller.DbController import *
from Views import Ui_MainWindow as Ui
import dbTableWindow
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
                
        self.addTabWidget
        return

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
        
        self.addTabWidget(self)

    def addTabWidget(self, _):        
        db_ctr = DBController(self.DBfilePaths[-1])
        try:
            _, result = db_ctr.excute_sql(
                'SELECT name from sqlite_master where type= "table"')
            print(str(result))
        
        except Exception as e:
            print(str(e))
            return
            
        my_tree = self.addTreeWidget(result)
        self.tabWidget.addTab(my_tree, self.DBfilePaths[-1].split('/')[-1])

    def addTreeWidget(self, l : list) -> QTreeWidget :        
        db_tree = QTreeWidget()
        db_tree.setHeaderLabel("Tables")
        db_tree.itemDoubleClicked.connect(self.onItemClicked)
        for i in l:
            QTreeWidgetItem(db_tree, list(i))
        return db_tree

    @pyqtSlot(QTreeWidgetItem, int)
    def onItemClicked(self, it, col):
        # print(it, col, it.text(col))
        db_ctr = DBController(self.DBfilePaths[-1])
        names, result = db_ctr.excute_sql(
            "SELECT * from {}".format(it.text(col)))
        self.mydb = dbTableWindow.DbTableWindow(names, result)    

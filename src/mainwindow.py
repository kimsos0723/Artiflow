import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import re
import json

from Controller.DbController import *
from Views import Ui_MainWindow as Ui
import dbTableWindow

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class Canvas(FigureCanvas):
    def __init__(self, parent=None, width=10, height=10, dpi=100):
        self.behaviors = []
        self.lastBehaviorTime = 24
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.setWindow()

    def setWindow(self):
        self.gnt = self.figure.add_subplot(111)        
        self.gnt.set_ylabel('behavior')        
        self.gnt.grid(True)
        self.gnt.figure.canvas.draw()
    
    def DrawBarh(self, behaviors: list):
        appid_arr = np.array([i['AppId'] for i in behaviors])        
        times_arr = np.array([i['StartTime'] for i in behaviors])
        np.append(times_arr, [i['EndTime'] for i in behaviors])
        uniq_appid_arr = np.unique(appid_arr)
        self.gnt.set_ylim(0, uniq_appid_arr.size*5)
        xZero = times_arr.min()
        self.gnt.set_xlim(0, appid_arr.size)
        self.gnt.set_yticks([i*5 for i in range(uniq_appid_arr.size)])
        p = re.compile(r'(?!^\d+$)^.+$')
        appUniq = []
        for i in uniq_appid_arr:           
            appsStr = ''
            for j in json.loads(i):
                jj = j['application']
                if p.match(jj):
                    appsStr += jj+','
            appUniq.append(appsStr.split(',')[-2])
        print(appUniq)
        self.gnt.set_yticklabels(appUniq)
        self.gnt.broken_barh([(xZero, 15700)], (0, 5), 
                         facecolors ='tab:blue') 
        self.gnt.figure.canvas.draw()
    # def


class WindowClass(QMainWindow, Ui.Ui_MainWindow):
    """
    Main Window Class
    """

    DBfilePaths = []
    DBTables = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUi(self)

    def initUi(self, _):
        self.initManu(self)
        self.canvas = Canvas(parent=self, width=14, height=10)
        self.gridLayout.addWidget(self.canvas)

    def initManu(self, _):
        mainManu = self.menuBar()
        fileManu = mainManu.addMenu('&File')
        viewManu = mainManu.addMenu('&View')
        helpManu = mainManu.addMenu('&Help')

        #file menu
        AddFile = QAction('&Add File', self)
        AddFile.triggered.connect(self.AddfileAction)
        fileManu.addAction(AddFile)

        #view manu
        viewDevice = QAction('&Devices', self)
        viewDevice.triggered.connect(self.ViewDeviceAction)
        viewManu.addAction(viewDevice)
        #Log

    def ResentApp(self, db_ctr):
        a = []
        p = re.compile(r'(?!^\d+$)^.+$')
        _, res = db_ctr.excute_sql("select AppId from Activity where ETag = \
                            (select ManualSequence.value from ManualSequence)")
        if(res == []):
            _, res = db_ctr.excute_sql("select AppId from ActivityOperation where ETag = \
                            (select ManualSequence.value from ManualSequence)")
        
        for i in json.loads(res[0][0]):
            a.append(i['application'])
            

        return a

    def AppByNumber(self, db_ctr):
        _, res = db_ctr.excute_sql(
            'select Activity.Appid from Activity order by Activity.StartTime')
        appList =[]
        for i in res:
            appList.append(i[0])
        npAppList = np.array(appList)
        uniq, counts = np.unique(npAppList, return_counts=True)
        p = re.compile(r'(?!^\d+$)^.+$')
        appUniq = []
        for i in uniq:
            appsStr = ''
            for j in json.loads(i):
                jj = j['application']
                if p.match(jj):
                    appsStr += jj+','                    
            appUniq.append(appsStr)
            
                
        return dict(zip(appUniq, counts))

    def CopyPasteSnap(self, db_ctr):
        CPYDic = {
            "Copy": 0,
            "Paste": 0,
            "Snap": 0
        }
        _, res = db_ctr.excute_sql(
            r'select "Group" FROM Activity where Activity.ActivityType = 16')
        for i in res:
            if i[0] == "Copy":
                CPYDic["Copy"] = CPYDic["Copy"] + 1
            elif i[0] == "Paste":
                CPYDic["Paste"] = CPYDic["Paste"] + 1
            else:
                CPYDic["Snap"] = CPYDic["Snap"] + 1

        return CPYDic

    def BrowsernameAndUrl(self, db_ctr):
        a = []
        _, res = db_ctr.excute_sql(
            'select Activity.AppActivityId, Activity.AppId from Activity')
        for i in res:
            if re.findall(r"(http|ftp|https):\/\/[\w-]+(\.[\w-]+)+([\w.,@?^=%&amp;:\/~+#-]*[\w@?^=%&amp;\/~+#-])?", i[0]):
                a.append(
                    [re.findall(r'(\"application\"\:"(.*?)")', i[1])[0][1], i[0]])
        return a

    def AddfileAction(self, _):
        path = ""
        path = self.openFileNameDialog(self)
        if path == "":
            return

        db_ctr = DBController(self.DBfilePaths[-1])
        #graph 
        graph = self.DurationByApp(db_ctr)
        self.canvas.DrawBarh(graph)
        # recent
        recapp = self.ResentApp(db_ctr)
        recent_app = QTableWidget()
        recent_app.setColumnCount(1)
        recent_app.setRowCount(len(recapp))

        recent_app.setHorizontalHeaderLabels(["Recent APP"])
        for count, data in enumerate(recapp):
            recent_app.setItem(count, 0, QTableWidgetItem(str(data)))
        recent_app.show()

        self.tabWidget_2.addTab(recent_app, "Recent APP")

        #COUNT By APP
        cntapp = self.AppByNumber(db_ctr)
        cnt_app = QTableWidget()
        cnt_app.setColumnCount(2)
        cnt_app.setRowCount(len(cntapp))
        cnt_app.setHorizontalHeaderLabels(['App', 'count'])

        for count, i in enumerate(cntapp.keys()):
            cnt_app.setItem(count, 0, QTableWidgetItem(str(i)))

        for count, i in enumerate(cntapp.values()):
            cnt_app.setItem(count, 1, QTableWidgetItem(str(i)))

        self.tabWidget_2.addTab(cnt_app, "Count By App")

        #Clipboard

        clb = self.CopyPasteSnap(db_ctr)
        clb_app = QTableWidget()
        clb_app.setColumnCount(1)
        clb_app.setRowCount(len(clb))
        clb_app.setHorizontalHeaderLabels(["Cliboard"])
        count = 0
        for k, v in clb.items():
            clb_app.setItem(count, 0, QTableWidgetItem(str(k)+":"+str(v)))
            count += 1
        self.tabWidget_2.addTab(clb_app, "Cliboard")

        return

    def DurationByApp(self, db_ctr):
        AppList = []
        _, res = db_ctr.excute_sql('select Activity.AppId, Activity.StartTime, Activity.EndTime, Activity.PlatformDeviceId from Activity')
        for i in res:
            AppList.append(
                {
                    'AppId': i[0],
                    'StartTime': i[1],
                    'EndTime': i[2],
                    'PlatformDeviceId': i[3]
                }
            )
        _, res = db_ctr.excute_sql('select AppId, StartTime, EndTime, PlatformDeviceId from ActivityOperation')
        for i in res:
            AppList.append(
                {
                    'AppId': i[0],
                    'StartTime': i[1],
                    'EndTime': i[2],
                    'PlatformDeviceId': i[3]
                }
            )
        return AppList
        
    def ViewDeviceAction(self, _):
        db_ctr = DBController(self.DBfilePaths[-1])
        _, result = db_ctr.excute_sql(
            'select distinct Activity.PlatformDeviceId from Activity')
        print(str(result))

    def openFileNameDialog(self, _):
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(
            self, "Open DB File", "", "DB Files (*.db);;All Files (*)", options=options)
        msg = QMessageBox()
        try:
            msg.setText(path)
            msg.exec_()
            self.DBfilePaths.append(path)
        except Exception as e:
            msg = QMessageBox()
            msg.setText("Cannot Open !")
            return ''

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

    def addTreeWidget(self, l: list) -> QTreeWidget:
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
        print(self.DBTables)
        dbTableWindow.DbTableWindow(names, result, self.DBTables)


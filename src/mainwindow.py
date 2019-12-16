import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic

import re
import json
from datetime import datetime, timedelta

from Controller.DbController import *
from Views import Ui_MainWindow as Ui
import dbTableWindow

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np



class Canvas(FigureCanvas):
    def __init__(self, parent=None, width=20, height=20, dpi=80):
        self.behaviors = []
        self.lastBehaviorTime = 24
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.setWindow()

    def setWindow(self):
        self.barh = self.figure.add_subplot(111)
        self.barh.set_ylabel('Behavior')
        self.barh.set_xlabel('Hour')
        self.barh.grid(True)

        self.barh.figure.canvas.draw()

    def DrawBarh(self, behaviors: list):
        platforms = []
        starts = []
        ends = []
        diffs = []        
        for d in behaviors:
            platforms.append(d['PlatformDeviceId'])
            starts.append(d['StartTime'])
            ends.append(d['EndTime'])
            if (d['EndTime'] - d['StartTime']) < 0:
                diffs.append(
                    (d['StartTime'], 1, d['PlatformDeviceId']))
            else:
                diffs.append((d['StartTime'], d['EndTime'] -
                              d['StartTime'], d['PlatformDeviceId']))        
        platforms_uniq = list(set(platforms))
        poss_dict = {}

        for i in platforms_uniq:            
            poss_dict[i] = []        
        for data in diffs:            
            poss_dict[data[-1]].append((data[0], data[1]))

        for i, p in enumerate(poss_dict):
            self.barh.broken_barh(poss_dict[p], (i,0.5))
                    
        self.barh.set_yticks([i+0.5 for i in range(len(platforms_uniq))])
        self.barh.set_yticklabels(platforms_uniq)
        self.barh.figure.canvas.draw()

    # def DrawBarh2(self, )

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
        self.canvas = Canvas(parent=self, width=5, height=5)
        toolbar = NavigationToolbar(self.canvas, self)

        self.gridLayout.addWidget(self.canvas)
        self.gridLayout.addWidget(toolbar)
        self.comboBox.addItem("실행파일")
        self.comboBox.addItem("UserDoc")
        self.comboBox.addItem("webPage")
        self.comboBox.addItem("Wifi")
        self.comboBox.addItem("MISC")
        self.comboBox.currentIndexChanged.connect(self.on_select)

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
        appList = []
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
        _, res = db_ctr.excute_sql(
            'select Activity.AppId, Activity.StartTime, Activity.EndTime, Activity.PlatformDeviceId from Activity')
        for i in res:
            AppList.append(
                {
                    'AppId': i[0],
                    'StartTime': i[1],
                    'EndTime': i[2],
                    'PlatformDeviceId': i[3]
                }
            )
        _, res = db_ctr.excute_sql(
            'select AppId, StartTime, EndTime, PlatformDeviceId from ActivityOperation')
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

        db_ctr = DBController(self.DBfilePaths[-1])
        names, result = db_ctr.excute_sql(
            "SELECT * from {}".format(it.text(col)))        
        dbTableWindow.DbTableWindow(names, result, self.DBTables)


    def __make_table(self, RowSQL, sql, type, path):
        self.tableWidget_2.setSelectionBehavior(QTableView.SelectRows) # 여러 줄 선택

        db_ctr = DBController(path)
        
        _, RowCount = db_ctr.excute_sql(RowSQL)
        rc = RowCount[0][0]

        #표 그리기
        self.tableWidget_2.setColumnCount(3)
        self.tableWidget_2.setRowCount(rc)

        #column 헤더명 설정
        self.tableWidget_2.setHorizontalHeaderLabels(["AppActivityId", "time", "Endtime"])
        self.tableWidget_2.horizontalHeaderItem(0).setTextAlignment(Qt.AlignCenter)

        #cell에 데이터 입력

        for i in range(rc):
            a = i + 1
            sql2 = sql
            if rc < a:
                break
            sql2 = sql2 + str(a)
            _, result = db_ctr.excute_sql(sql2)
            if result == []:
                break

            Seq01 = str(result[0][1])
            timestmp = int(result[0][2])
            endTimeStmp = int(result[0][3])
            if endTimeStmp == 0:
                endDate = "No Endtime"
            else:
                endDate = str(datetime.fromtimestamp(endTimeStmp))
            date = str(datetime.fromtimestamp(timestmp))

            if type == ".exe":
                idx = Seq01.find(type)
                if idx == -1:
                    idx = Seq01.find("com.")
                    if idx == -1:
                        continue
                    Seq02 = Seq01[idx:]
                    idx2 = Seq02.find(",")
                    final = Seq02[:idx2]
                else:
                    Seq02 = Seq01[:idx+4]
                    idx2 = Seq02[::-1].find("\\")
                    Seq03 = Seq02[::-1]
                    Seq04 = Seq03[:idx2]
                    final = Seq04[::-1]
            elif type == "webPage":
                final = Seq01
            elif type == "UserDoc":
                idx = Seq01.find("\\")
                if idx == -1:
                    idx = Seq01[::-1].find("/")
                    if idx == -1:
                        Seq01 = str(result[0][4])
                        idx = Seq01.find(".exe")
                        if idx == -1:
                            idx = Seq01.find("com.")
                            if idx == -1:
                                continue
                            Seq02 = Seq01[idx:]
                            idx2 = Seq02.find(",")
                            final = Seq02[:idx2]
                        else:
                            Seq02 = Seq01[:idx + 4]
                            idx2 = Seq02[::-1].find("\\")
                            Seq03 = Seq02[::-1]
                            Seq04 = Seq03[:idx2]
                            final = Seq04[::-1]
                    else:
                        Seq02 = Seq01[::-1]
                        Seq03 = Seq02[:idx]
                        final = Seq03[::-1]

                else:
                    Seq02 = Seq01[::-1]
                    idx2 = Seq02.find("\\")
                    Seq03 = Seq02[:idx2]
                    final = Seq03[::-1]
                final = final.replace("%20", " ")
            elif type == "Wifi":
                final = "Wifi 연결정보"
            elif type == "MISC":
                idx = Seq01.find("displayText")
                if idx == -1:
                    continue
                Seq02 = Seq01[idx+13:]
                idx2 = Seq02.find(",")
                final = Seq02[:idx2]

            self.tableWidget_2.setItem(i, 0, QTableWidgetItem(final))
            self.tableWidget_2.setItem(i, 1, QTableWidgetItem(date))
            self.tableWidget_2.setItem(i, 2, QTableWidgetItem(endDate))


    @pyqtSlot()
    def on_select(self):
        result1 = str(self.comboBox.currentText())
        if result1 == "실행파일":
            RowSQL = "SELECT count(*) FROM Activity WHERE AppId LIKE '%.exe%' AND AppActivityID NOT LIKE '%.doc%' AND AppActivityId NOT LIKE '%.pdf%' AND AppActivityId NOT LIKE '%.xls%' AND AppActivityId NOT LIKE '%.ppt%' AND AppActivityId NOT LIKE '%.hwp%' AND AppActivityId NOT LIKE '%.txt%' AND AppId NOT LIKE '%Hwp.exe%' AND AppId NOT LIKE '%HShow.exe%' AND AppId NOT LIKE '%HCell.exe%' AND AppId NOT LIKE '%Notepad.exe%' AND AppId NOT LIKE '% OR AppId LIKE '%com.%'"
            sql = "WITH Temp AS(SELECT ROW_NUMBER() OVER(ORDER BY ETag ASC) AS 'No', AppId, StartTime, EndTime FROM Activity WHERE AppId like '%.exe%' AND AppActivityID NOT LIKE '%.doc%' AND AppActivityId NOT LIKE '%.pdf%' AND AppActivityId NOT LIKE '%.xls%' AND AppActivityId NOT LIKE '%.ppt%' AND AppActivityId NOT LIKE '%.hwp%' AND AppActivityId NOT LIKE '%.txt%' AND AppId NOT LIKE '%Hwp.exe%' AND AppId NOT LIKE '%HShow.exe%' AND AppId NOT LIKE '%HCell.exe%' AND AppId NOT LIKE '%Notepad.exe%' OR AppId LIKE '%com.%') SELECT * FROM Temp WHERE No ="
            type = ".exe"
        elif result1 == "webPage":
            RowSQL = "SELECT count(*) FROM Activity WHERE AppActivityId LIKE '%http%'"
            sql = "WITH Temp AS(SELECT ROW_NUMBER() OVER(ORDER BY ETag ASC) AS 'No', AppActivityId, StartTime, EndTime FROM Activity WHERE AppActivityId like '%http%') SELECT * FROM Temp WHERE No ="
            type = "webPage"
        elif result1 == "UserDoc":
            RowSQL = "SELECT count(*) FROM Activity WHERE AppActivityId LIKE '%.doc%' OR AppId LIKE '%Hwp.exe%' OR AppId LIKE '%HShow.exe%' OR AppId LIKE '%HCell.exe%' OR AppId LIKE '%Notepad.exe%' OR AppActivityId LIKE '%.pdf%' OR AppActivityId LIKE '%.xls%' OR AppActivityId LIKE '%.ppt%' OR AppActivityId LIKE '%.hwp%' OR AppActivityId LIKE '%.txt%'"
            sql = "WITH Temp AS(SELECT ROW_NUMBER() OVER(ORDER BY ETag ASC) AS 'No', AppActivityId, StartTime, EndTime, AppId FROM Activity WHERE AppActivityId LIKE '%.doc%' OR AppId LIKE '%Hwp.exe%' OR AppId LIKE '%HShow.exe%' OR AppId LIKE '%HCell.exe%' OR AppId LIKE '%Notepad.exe%' OR AppActivityId LIKE '%.pdf%' OR AppActivityId LIKE '%.xls%' OR AppActivityId LIKE '%ppt%' OR AppActivityId LIKE '%.hwp%' OR AppActivityId LIKE '%.txt%') SELECT * FROM Temp WHERE No ="
            type = "UserDoc"
        elif result1 == "Wifi":
            RowSQL = "SELECT count(*) FROM Activity WHERE ActivityType = 12 OR ActivityType = 11"
            sql = "WITH Temp AS(SELECT ROW_NUMBER() OVER(ORDER BY ETag ASC) AS 'No', AppId, StartTime, EndTime FROM Activity WHERE ActivityType = 11 OR ActivityType = 12) SELECT * FROM Temp WHERE No ="
            type = "Wifi"
        elif result1 == "MISC":
            RowSQL = "SELECT count(*) FROM Activity WHERE AppActivityId NOT like '%http%' AND AppId NOT LIKE '%.exe%' AND ActivityType NOT LIKE '%12%' AND AppActivityId NOT LIKE '%.pdf%' AND ActivityType NOT LIKE '%11%' AND Payload like '%displayText%'"
            sql = "WITH Temp AS(SELECT ROW_NUMBER() OVER(ORDER BY ETag ASC) AS 'No', Payload, StartTime, EndTime FROM Activity WHERE AppActivityId NOT like '%http%' AND AppActivityId NOT LIKE '%.pdf%' AND AppId NOT LIKE '%.exe%' AND ActivityType NOT LIKE '%12%' AND ActivityType NOT LIKE '%11%' AND Payload like '%displayText%') SELECT * FROM Temp WHERE No ="
            type = "MISC"        
        self.__make_table(RowSQL,sql,type, self.DBfilePaths[-1])
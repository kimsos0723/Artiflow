from PyQt5.QtWidgets import *


class DbTableWindow(QTreeWidget):
    def __init__(self, names: list, result: list, dbtables: list):
        super().__init__()
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(len(names))
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(names)
        self.tableWidget.destroyed.connect(
            lambda dbtables, self: dbtables.remove(self)
        )
        for row_num, row_data in enumerate(result):
            self.tableWidget.insertRow(row_num)
            for column_num, data in enumerate(row_data):
                self.tableWidget.setItem(
                    row_num, column_num, QTableWidgetItem(str(data)))
        dbtables.append(self)
        self.tableWidget.show()

        # print(names, result)

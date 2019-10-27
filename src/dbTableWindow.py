from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QDialog
class DbTablePopup(QDialog):
    def __init__(self, names : list, db : list, parent=None) :
        super().__init__(parent)
                
        self.db_table = QTableWidget()
        self.db_table.setColumnCount(len(names))
        self.db_table.setRowCount(0)
        self.db_table.setHorizontalHeaderLabels(names)   

        for row_num, row_data in enumerate(db):
            self.db_table.insertRow(row_num)
            for column_num, data in enumerate(row_data):
                self.db_table.setItem(row_num, column_num, QTableWidgetItem(str(data)))
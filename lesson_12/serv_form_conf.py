from PyQt5.QtWidgets import QTableWidgetItem, qApp
from PyQt5 import QtWidgets
from serv_form import *

class mywindow(QtWidgets.QMainWindow):

    def __init__(self, database, server):
        super(mywindow, self).__init__()

        self.database = database
        self.server = server
        self.table_cols = 0

        self.all_clients = []
        self.server_clients = {}
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.startServBtn.clicked.connect(self.startBtnClicked)
        self.ui.btnQuit_2.clicked.connect(qApp.quit)

        self.ui.tableWidget.setColumnCount(2)
        self.ui.tableWidget.setRowCount(self.table_cols)

    def fill_table(self):
        self.all_clients = self.database.get_all_clients()
        if len(self.all_clients) != self.table_cols:
            self.table_cols = len(self.all_clients)
            self.ui.tableWidget.setRowCount(self.table_cols)
            self.show()

        for idx in range(len(self.all_clients)):
            cell_name = QTableWidgetItem(self.all_clients[idx][0])
            cell_name.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
            )
            if self.all_clients[idx][0] in self.server.names.keys():
                cell_state = QTableWidgetItem("Active")
            else:
                cell_state = QTableWidgetItem("Lost")
            cell_state.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
            )
            self.ui.tableWidget.setItem(idx, 0, cell_name)
            self.ui.tableWidget.setItem(idx, 1, cell_state)


    def startBtnClicked(self):
        self.server.set_gui_params(self.ui.lineEditAddress.text(), self.ui.lineEditPort.text())
        self.server.start()
        self.ui.textViewTerminal.setText('Server started')
        self.fill_table()
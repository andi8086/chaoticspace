# This Python file uses the following encoding: utf-8
import sys
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
# from PySide2.QtWidgets import *
import os
from pathlib import Path
from mysql import connector

mysql_config = {
   'user': 'root',
   'password': 'root',
   'host': '127.0.0.1',
   'database': 'chaoticspace'
}

APPDIR = Path(__file__).parent

def MySQLError(self, err):
    QMessageBox.critical(self, "MySQL Error", err.msg)

def SQLExec(self, statement):
    try:
        cursor = self.cnx.cursor()
        cursor.execute(statement)
        if "INSERT" in statement:
            self.cnx.commit()
        return cursor
    except connector.Error as err:
        MySQLError(self, err)


def SetColWidths(table, widthlist):
    for k, v in enumerate(widthlist):
        table.setColumnWidth(k, v)

def InitTable(table, widthlist):
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    SetColWidths(table, widthlist)
    table.setSortingEnabled(True)
    table.setStyleSheet('QTableView {background-color: #000000; color:#777777;}')

def MapResultsToTable(res, table, vars):
    rowCount = 0
    for (vars) in res:
        rowCount += 1
        table.setRowCount(rowCount)
        for k, v in enumerate(vars):
            table.setItem(rowCount-1, k, QTableWidgetItem(str(v)))

def UpdateView(self, table, tablename, keys):
    table.setRowCount(0)
    res = SQLExec(self, "SELECT * FROM {} WHERE 1;".format(tablename))
    MapResultsToTable(res, table, keys)
    res.close()


class PartsManageDialog(QDialog):
    def __init__(self, parent, cnx):
        super().__init__(parent)
        uic.loadUi(os.path.join(Path(__file__).parent, 'partsManageDialog.ui'), self)
        self.createButton.clicked.connect(self.createPart)
        self.cnx = cnx
        self.partsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        SetColWidths(self.partsTable, [30, 250, 100, 200, 200, 200])
        self.partsTable.setSortingEnabled(True)
        self.partsTable.setStyleSheet('QTableView {background-color: #000000; color:#777777;}')
        self.Icon_IC = QIcon(os.path.join(os.path.join(APPDIR, 'icons'), 'integrated-circuit2.png'))
        self.update()
        self.show()

    def update(self):
        self.partsTable.setRowCount(0)
        cursor = self.cnx.cursor()
        try:
            cursor.execute("SELECT * FROM parts, places, categories WHERE parts.fkPlace = places.pkID AND parts.fkCategory = categories.pkID;")
        except connector.Error as err:
            MySQLError(self, err)

        rowCount = 0
        for (pkID, pName, pCount, fkPlace, pDesc, fkCat, pComments, placepkID, placeName, placeDesc, catpkID, catName, catDesc) in cursor:
            rowCount += 1
            self.partsTable.setRowCount(rowCount)
            self.partsTable.setItem(rowCount-1, 0, QTableWidgetItem(str(pkID)))
            name = QTableWidgetItem(str(pName))
            name.setIcon(self.Icon_IC)
            self.partsTable.setItem(rowCount-1, 1, name)
            self.partsTable.setItem(rowCount-1, 2, QTableWidgetItem(str(pCount)))
            placeItem = QTableWidgetItem(str(placeName))
            placeItem.setToolTip(placeDesc)
            self.partsTable.setItem(rowCount-1, 3, placeItem)
            self.partsTable.setItem(rowCount-1, 4, QTableWidgetItem(str(pDesc)))
            catItem = QTableWidgetItem(str(catName))
            catItem.setToolTip(catDesc)
            self.partsTable.setItem(rowCount-1, 5, catItem)
            commItem = QTableWidgetItem(str(pComments))
            commItem.setToolTip(str(pComments))
            self.partsTable.setItem(rowCount-1, 6, commItem)

        res = SQLExec(self, "SELECT * FROM places WHERE 1;")
        self.partPlace.clear()
        for (pkID, pName, pDesc) in cursor:
            self.partPlace.addItem(pName, {'pkID': pkID})
        res.close()

        res = SQLExec(self, "SELECT * FROM categories WHERE 1;")
        self.partCategory.clear()
        for (pkID, cName, cDesc) in cursor:
            self.partCategory.addItem(cName, {'pkID': pkID})
        res.close()

    def createPart(self, event):
        cursor = self.cnx.cursor()
        pName = self.partName.text()
        pCount = self.partCount.text()
        pPlace = self.partPlace.currentData()['pkID']
        pCat = self.partCategory.currentData()['pkID']
        pComments = self.partComments.toPlainText()
        pDesc = self.partDesc.text()
        QMessageBox.information(self, "", pComments)
        statement = """INSERT INTO parts (name, count, fkplace, description, fkcategory, comments)
                       VALUES (\"{}\", {}, {}, \"{}\", {}, \"{}\");""".format(
                        pName, pCount, pPlace, pDesc, pCat, pComments)
        SQLExec(self, statement)


class CatManageDialog(QDialog):
    def __init__(self, parent, cnx):
        super().__init__(parent)
        uic.loadUi(os.path.join(Path(__file__).parent, 'categoriesDialog.ui'), self)
        self.createButton.clicked.connect(self.createCat)
        self.cnx = cnx
        InitTable(self.categoriesTable, [30, 250, 400])
        self.update()
        self.show()

    def update(self):
        UpdateView(self, self.categoriesTable, "categories", ["ID", "Name", "Desc"])

    def createCat(self, event):
        cName = self.catName.text()
        cDesc = self.catDesc.text()
        statement = "INSERT INTO categories (name, description) VALUES (\"{}\", \"{}\");".format(cName, cDesc)
        SQLExec(self, statement).close()


class PlaceManageDialog(QDialog):
    def __init__(self, parent, cnx):
        super().__init__(parent)
        uic.loadUi(os.path.join(Path(__file__).parent, 'placesDialog.ui'), self)
        self.createButton.clicked.connect(self.createPlace)
        self.cnx = cnx
        InitTable(self.placesTable, [30, 250, 400])
        self.update()
        self.show()

    def update(self):
        UpdateView(self, self.placesTable, "places", ["ID", "Name", "Desc"])

    def createPlace(self, event):
        pName = self.placeName.text()
        pDesc = self.placeDesc.text()
        statement = "INSERT INTO places (name, description) VALUES (\"{}\", \"{}\");".format(pName, pDesc)
        SQLExec(self, statement).close()


class PartsDialog(QDialog):
    def __init__(self, parent, cnx):
        super().__init__(parent)
        uic.loadUi(os.path.join(Path(__file__).parent,'partsDialog.ui'), self)
        self.partName.textChanged.connect(self.newInput)
        InitTable(self.results, [300, 400, 150, 300])
        self.cnx = cnx
        self.show()

    def newInput(self, event):
        self.results.setRowCount(0)
        statement = "SELECT * FROM parts WHERE parts.name LIKE \"{}\";".format(
                self.partName.text().replace("*", "%"))
        res = SQLExec(self, statement)
        MapResultsToTable(res, self.results, ["name", "count", "desc", "place", "comment"])
        res.close()
        self.results.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(Path(__file__).parent,'mainwindow.ui'), self)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.partsQueryButton.clicked.connect(self.partQuery)
        self.placeManageButton.clicked.connect(self.placeManage)
        self.catManageButton.clicked.connect(self.catManage)
        self.partsManageButton.clicked.connect(self.partManage)
        self.actionQuit.triggered.connect(self.exit)
        try:
            self.cnx = connector.connect(**mysql_config)
        except connector.Error as err:
            if err.errno == connector.errorcode.ER_ACCESS_DENIED_ERROR:
                QMessageBox.critical(self, "MySQL Error",
                                "Server sais access denied.")
                self.close()
            elif err.errno == connector.errorcode.ER_BAD_DB_ERROR:
                print("Database not found")
            else:
                print(err)

    def exit(self, event):
        self.close()

    def partQuery(self, event):
        pd = PartsDialog(self, self.cnx)

    def partManage(self, event):
        pm = PartsManageDialog(self, self.cnx)

    def catManage(self, event):
        cm = CatManageDialog(self, self.cnx)

    def placeManage(self, event):
        pm = PlaceManageDialog(self, self.cnx)

    def closeEvent(self, event):
        if hasattr(self, 'cnx') and self.cnx:
            self.cnx.close()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    f = app.font()
    f.setPixelSize(14)
    app.setFont(f)
    window.show()
    sys.exit(app.exec_())

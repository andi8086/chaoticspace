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

class PartsManageDialog(QDialog):
    def __init__(self, parent, cnx):
        super().__init__(parent)
        uic.loadUi(os.path.join(Path(__file__).parent, 'partsManageDialog.ui'), self)
        self.createButton.clicked.connect(self.createPart)
        self.cnx = cnx
        self.partsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.partsTable.setColumnWidth(0, 30)
        self.partsTable.setColumnWidth(1, 250)
        self.partsTable.setColumnWidth(2, 100)
        self.partsTable.setColumnWidth(3, 200)
        self.partsTable.setColumnWidth(4, 200)
        self.partsTable.setColumnWidth(5, 200)
        self.partsTable.setSortingEnabled(True)
        self.partsTable.setStyleSheet('QTableView {background-color: #000000; color:#777777;}')
        self.Icon_IC = QIcon(os.path.join(os.path.join(APPDIR, 'icons'), 'integrated-circuit2.png'))
        self.updateView()


        self.show()

    def updateView(self):
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
        try:
            cursor.execute("SELECT * FROM places WHERE 1;")
        except connector.Error as err:
            MySQLError(self, err)

        self.partPlace.clear()
        for (pkID, pName, pDesc) in cursor:
            self.partPlace.addItem(pName, {'pkID': pkID})

        try:
            cursor.execute("SELECT * FROM categories WHERE 1;")
        except connector.Error as err:
            MySQLError(self, err)

        self.partCategory.clear()
        for (pkID, cName, cDesc) in cursor:
            self.partCategory.addItem(cName, {'pkID': pkID})

        cursor.close()


    def createPart(self, event):
        cursor = self.cnx.cursor()
        pName = self.partName.text()
        pCount = self.partCount.text()
        pPlace = self.partPlace.currentData()['pkID']
        pCat = self.partCategory.currentData()['pkID']
        pComments = self.partComments.toPlainText()
        pDesc = self.partDesc.text()
        QMessageBox.information(self, "", pComments)
        try:
            cursor.execute("""INSERT INTO parts (name, count, fkplace, description, fkcategory, comments)
                VALUES (\"{}\", {}, {}, \"{}\", {}, \"{}\");""".format(
                        pName, pCount, pPlace, pDesc, pCat, pComments))
            self.cnx.commit()
            cursor.close()
        except connector.Error as err:
            MySQLError(self, err)




class CatManageDialog(QDialog):
    def __init__(self, parent, cnx):
        super().__init__(parent)
        uic.loadUi(os.path.join(Path(__file__).parent, 'categoriesDialog.ui'), self)
        self.createButton.clicked.connect(self.createCat)
        self.cnx = cnx
        self.categoriesTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.categoriesTable.setColumnWidth(0, 30)
        self.categoriesTable.setColumnWidth(1, 250)
        self.categoriesTable.setColumnWidth(2, 400)
        self.categoriesTable.setSortingEnabled(True)
        self.categoriesTable.setStyleSheet('QTableView {background-color: #000000; color:#777777;}')
        self.updateView()
        self.show()

    def updateView(self):
        self.categoriesTable.setRowCount(0)
        cursor = self.cnx.cursor()
        try:
            cursor.execute("SELECT * FROM categories WHERE 1;")
        except connector.Error as err:
            MySQLError(self, err)

        rowCount = 0
        for (pkID, cName, cDesc) in cursor:
            rowCount += 1
            self.categoriesTable.setRowCount(rowCount)
            self.categoriesTable.setItem(rowCount-1, 0, QTableWidgetItem(str(pkID)))
            self.categoriesTable.setItem(rowCount-1, 1, QTableWidgetItem(str(cName)))
            self.categoriesTable.setItem(rowCount-1, 2, QTableWidgetItem(str(cDesc)))
        cursor.close()

    def createCat(self, event):
        cursor = self.cnx.cursor()
        cName = self.catName.text()
        cDesc = self.catDesc.text()
        try:
            cursor.execute("INSERT INTO categories (name, description) VALUES (\"{}\", \"{}\");".format(
                cName, cDesc))
            self.cnx.commit()
            cursor.close()
        except connector.Error as err:
            MySQLError(self, err)


class PlaceManageDialog(QDialog):
    def __init__(self, parent, cnx):
        super().__init__(parent)
        uic.loadUi(os.path.join(Path(__file__).parent, 'placesDialog.ui'), self)
        self.createButton.clicked.connect(self.createPlace)
        self.cnx = cnx
        self.placesTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.placesTable.setColumnWidth(0, 30)
        self.placesTable.setColumnWidth(1, 250)
        self.placesTable.setColumnWidth(2, 400)
        self.placesTable.setSortingEnabled(True)
        self.placesTable.setStyleSheet('QTableView {background-color: #000000; color:#777777;}')
        self.updateView()
        self.show()

    def updateView(self):
        self.placesTable.setRowCount(0)
        cursor = self.cnx.cursor()
        try:
            cursor.execute("SELECT * FROM places WHERE 1;")
        except connector.Error as err:
            MySQLError(self, err)

        rowCount = 0
        for (pkID, pName, pDesc) in cursor:
            rowCount += 1
            self.placesTable.setRowCount(rowCount)
            self.placesTable.setItem(rowCount-1, 0, QTableWidgetItem(str(pkID)))
            self.placesTable.setItem(rowCount-1, 1, QTableWidgetItem(str(pName)))
            self.placesTable.setItem(rowCount-1, 2, QTableWidgetItem(str(pDesc)))
        cursor.close()


    def createPlace(self, event):
        cursor = self.cnx.cursor()
        pName = self.placeName.text()
        pDesc = self.placeDesc.text()
        try:
            cursor.execute("INSERT INTO places (name, description) VALUES (\"{}\", \"{}\");".format(
                pName, pDesc))
            self.cnx.commit()
            cursor.close()
        except connector.Error as err:
            MySQLError(self, err)


class PartsDialog(QDialog):
    def __init__(self, parent, cnx):
        super().__init__(parent)
        uic.loadUi(os.path.join(Path(__file__).parent,'partsDialog.ui'), self)
        self.partName.insert("blah")
        self.partName.textChanged.connect(self.newInput)

        self.results.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results.setColumnCount(4)
        self.resultHeader = ['Name', 'Category', 'Count', 'Place']
        self.results.setHorizontalHeaderLabels(self.resultHeader)
        self.results.setColumnWidth(0, 300)
        self.results.setColumnWidth(1, 400)
        self.results.setColumnWidth(2, 150)
        self.results.setColumnWidth(3, 300)
        self.results.setSortingEnabled(True)
        self.results.setStyleSheet('QTableView {background-color: #000000; color:#777777;}')

        self.cnx = cnx
        self.show()

    def newInput(self, event):
        self.results.setItem(0, 1, QTableWidgetItem("blabla"))
        self.results.update()
        pass

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


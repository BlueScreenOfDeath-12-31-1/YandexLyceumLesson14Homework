import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QPushButton, QWidget, QMessageBox, QTextEdit, QTableWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic


class EditOrAddDialog(QWidget):
    def __init__(self, mode="Add", run_on_update=lambda: None):
        super().__init__()
        uic.loadUi("addEditCoffeeForm.ui", self)
        self.id = None
        self.mode = "Add"
        self.on_finish = run_on_update

        self.pushButton.clicked.connect(self.finish)

    def show(self, *args, mode=None, id_=None):
        if mode is not None:
            self.mode = mode
            self.id = id_
            if mode == "Edit":
                print(args)
                self.lineEdit.setText(str(id_))
                self.lineEdit_2.setText(str(args[1]))
                self.lineEdit_3.setText(str(args[2]))
                self.lineEdit_4.setText(str(args[3]))
                # self.textEdit: QTextEdit
                self.textEdit.setText(str(args[4]))
                self.lineEdit_5.setText(str(args[5]))
                self.lineEdit_6.setText(str(args[6]))
            else:
                self.lineEdit.setText("auto")
                self.lineEdit_2.setText("")
                self.lineEdit_3.setText("")
                self.lineEdit_4.setText("")
                # self.textEdit: QTextEdit
                self.textEdit.setText("")
                self.lineEdit_5.setText("")
                self.lineEdit_6.setText("")

        super().show()

    def finish(self):
        name = self.lineEdit_2.text()
        degree_of_roasting = self.lineEdit_3.text()
        grain_type = self.lineEdit_4.text()
        # self.textEdit: QTextEdit
        description = self.textEdit.toPlainText()
        price = self.lineEdit_5.text()
        volume = self.lineEdit_6.text()
        if name != "" and degree_of_roasting != "" and grain_type != "" and is_correct_price(price) and volume != "":
            if self.mode == "Add":
                add_data(self.id, name, degree_of_roasting, grain_type, description, float(price), volume)
            elif self.mode == "Edit":
                commit_edited_data(self.id, name, degree_of_roasting, grain_type, description, float(price), volume)
            else:
                print(f"Unknow mode = {self.mode}")
            self.on_finish()
            self.hide()
        else:
            QMessageBox.warning(None, "Неправельный ввод !", "Неправельный ввод !", QMessageBox.Ok)


def commit_edited_data(*args):
    con = sqlite3.connect("coffee.sqlite")
    con.cursor().execute(f"UPDATE cofee"
                         f" SET name = '{args[1]}', degree_of_roasting = '{args[2]}', grain_type = '{args[3]}',"
                         f"description = '{args[4]}', price = {args[5]}, volume = '{args[6]}' "
                         f"WHERE ID = {args[0]}")
    con.commit()
    con.close()


def add_data(*args):
    con = sqlite3.connect("coffee.sqlite")
    con.cursor().execute(f"INSERT INTO cofee("
                         f"name, degree_of_roasting, grain_type, description, price, volume) "
                         f"VALUES('{args[1]}', '{args[2]}', '{args[3]}', '{args[4]}', {args[5]}, '{args[6]}')")
    con.commit()
    con.close()


def get_data():
    con = sqlite3.connect("coffee.sqlite")
    cur = con.cursor()
    data = cur.execute("SELECT * from cofee").fetchall()
    con.close()
    return data


def is_correct_price(price: str) -> bool:
    if price.isdigit():
        return True
    if '.' in price or ',' in price:
        price.replace(",", ".")
        if price.count(".") > 1:
            return False
        if price[0:1] == "-":
            price = price[1:]
        delimiter_pos = price.find(".")
        if delimiter_pos == 0:
            delimiter_pos += 1
            price = "0" + price
        if (price[:delimiter_pos] + price[delimiter_pos + 1:]).isdigit():
            return True
    return False


class MyWindow1(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)

        self.pushButton: QPushButton
        self.pushButton_2: QPushButton
        self.pushButton_3: QPushButton
        self.pushButton_4: QPushButton

        self.pushButton_4.clicked.connect(self.update_table)

        self.pushButton.clicked.connect(lambda: self.edit_form.show(mode="Add", id_=None))
        self.pushButton_2.clicked.connect(self.try_open_update_window)

        self.update_table()

        self.edit_form = EditOrAddDialog(run_on_update=self.update_table)
        self.tableWidget: QTableWidget

        self.pushButton_3.clicked.connect(self.delete_element)

    def try_open_update_window(self):
        self.tableWidget: QTableWidget
        cr = self.tableWidget.currentRow()
        if cr is not None:
            if self.tableWidget.item(cr, 0) is not None:
                data = [self.tableWidget.item(cr, i).text() for i in range(7)]
                id_ = int(data[0])
                self.edit_form.show(*data, mode="Edit", id_=id_)

    def update_table(self):
        data_1 = get_data()
        title = ['ID', 'название сорта', 'степень обжарки', 'Тип зёрен', 'описание вкуса', 'цена', 'объем упаковки']
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(len(title))
        self.tableWidget.setHorizontalHeaderLabels(title)

        self.tableWidget.setRowCount(0)
        for i, row in enumerate(data_1):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                # print(i, row, j, elem, "$$$")
                a = QTableWidgetItem(str(elem))
                self.tableWidget.setItem(
                    i, j, a)

        self.tableWidget.resizeColumnsToContents()

    def delete_element(self):
        self.tableWidget: QTableWidget
        cr = self.tableWidget.currentRow()
        if cr is not None:
            if self.tableWidget.item(cr, 0) is not None:
                data = [self.tableWidget.item(cr, i).text() for i in range(7)]
                id_ = int(self.tableWidget.item(cr, 0).text())
                # self.edit_form.show(*data, mode="Edit", id_=id_)
                t = " ,".join(data)
                if QMessageBox.question(None, "Вы уверены?", f"Будет удалена запись :\n{t}",
                                        QMessageBox.Ok, QMessageBox.Cancel) == QMessageBox.Cancel:
                    return

                con = sqlite3.connect("coffee.sqlite")
                con.cursor().execute(f"DELETE FROM cofee WHERE ID = {id_}")
                con.commit()
                con.close()
                self.update_table()


if __name__ == '__main__':
    # print(get_data())
    # exit(0)
    app = QApplication(sys.argv)
    window = MyWindow1()
    window.show()
    sys.exit(app.exec_())

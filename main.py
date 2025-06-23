from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDialog, QLineEdit
from PyQt5.QtGui import QFont

from mysql.connector import connect

import sys

FONT = QFont("Arial", 16, QFont.Bold)
CONFIG = {
    "host": "localhost",
    "database": "exam",
    "user": "root",
    "password": ""
}


def connect_db():
    try:
        conn = connect(**CONFIG)
        return conn, conn.cursor()
    except Exception as err:
        print("Ошибка подключения к бд: " + str(err))


def create_label(win, text, x, y):
    label = QtWidgets.QLabel(win)
    label.setText(text)
    label.move(x, y)
    label.setFont(FONT)
    label.adjustSize()
    return label


def create_input(win, win_x, win_y, x, y, text=""):
    edit = QtWidgets.QLineEdit(win)
    edit.setText(text)
    edit.move(win_x, win_y)
    edit.setFont(FONT)
    edit.resize(x, y)
    return edit


def create_button(win, win_x, win_y, x, y, text, command):
    btn = QtWidgets.QPushButton(win)
    btn.setText(text)
    btn.move(win_x, win_y)
    btn.resize(x, y)
    btn.setFont(FONT)
    btn.clicked.connect(command)
    return btn


def create_table(win, win_x, win_y, x, y, header):
    table = QtWidgets.QTableWidget(win)
    table.move(win_x, win_y)
    table.resize(x, y)
    table.setColumnCount(len(header))
    table.setHorizontalHeaderLabels(header)
    table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
    return table


def message(win, title, text):
    QtWidgets.QMessageBox.information(win, title, text)


class WindowEdit(QDialog):
    def __init__(self, main_window, text_button):
        super().__init__()
        self.setWindowTitle('Окно')
        self.setGeometry(1400, 350, 300, 400)
        self.labels, self.inputs = [], []
        self.main_window = main_window
        for i, text in enumerate(self.main_window.data_to_edit):
            self.labels.append(create_label(self, str(text), 40, 20 + i * 80))
            self.inputs.append(create_input(self, 40, 55 + i * 80, 220, 35, self.main_window.data_to_edit.get(text)))

        self.button = create_button(self, 40, 340, 220, 50, text_button, lambda: self.send())

    def send(self):
        try:
            for i, text in enumerate(self.main_window.data_to_edit):
                self.main_window.data_to_edit[text] = self.inputs[i].text()
            self.accept()
        except Exception as err:
            message(self, "Ошибка", f"Ошибка при изменении внутренней переменной: {err}")


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Главная')
        self.setGeometry(1350, 150, 400, 800)

        self.data_to_edit = {"ID": None, "Имя": None, "Срок": None, "Цена": None}

        self.label0 = create_label(self, "Главное окно", 140, 50)
        self.button0 = create_button(self, 340, 30, 35, 35, "🗘", lambda: self.load())
        self.table = create_table(self, 10, 100, 380, 300, [i for i in self.data_to_edit])

        self.label1 = create_label(self, "Имя", 50, 450)
        self.input1 = create_input(self, 50, 480, 120, 35)
        self.button1 = create_button(self, 50, 525, 120, 35, "Поиск", self.poisk1)

        self.label2 = create_label(self, "Дата", 230, 450)
        self.input2 = create_input(self, 230, 480, 120, 35)
        self.button2 = create_button(self, 230, 525, 120, 35, "Поиск", self.poisk2)

        self.button_add = create_button(self, 50, 610, 300, 50, "Добавить", self.add)
        self.button_edit = create_button(self, 50, 670, 300, 50, "Изменить ", self.edit)
        self.button_delete = create_button(self, 50, 730, 300, 50, "Удалить", self.delete)

        self.conn, self.cur = connect_db()

        self.load()

    def load(self, request="select * from products", param=()):
        self.conn, self.cur = connect_db()
        try:
            self.cur.execute(request, param)
            data = self.cur.fetchall()
            self.table.setRowCount(len(data))

            for row in range(len(data)):
                for col, item in enumerate(data[row]):
                    self.table.setItem(row, col, QtWidgets.QTableWidgetItem(str(item)))

        except Exception as err:
            message(self, "Ошибка", f"Ошибка загрузки данных: {str(err)}")
        finally:
            self.conn.close()

    def add(self):
        self.data_to_edit = {"ID": None, "Имя": None, "Срок": None, "Цена": None}
        window_add = WindowEdit(self, "Добавить")
        if window_add.exec_():
            self.conn, self.cur = connect_db()
            try:
                self.cur.execute("insert into products (id, name, date_save, price) values (%s, %s, %s, %s);",
                                 (self.data_to_edit.get("ID"),
                                  self.data_to_edit.get("Имя"),
                                  self.data_to_edit.get("Срок"),
                                  self.data_to_edit.get("Цена"))
                                 )
                self.conn.commit()
                self.load()
            except Exception as err:
                self.conn.rollback()
                message(self, "Ошибка", f"Ошибка добавления данных: {str(err)}")
            finally:
                self.conn.close()

    def edit(self):
        current_row = self.table.currentRow()

        if current_row >= 0:
            id_remember = self.table.item(current_row, 0).text()
            for ind, item in enumerate(self.data_to_edit):
                self.data_to_edit[item] = self.table.item(current_row, ind).text()

            window_edit = WindowEdit(self, "Изменить")
            if window_edit.exec_():
                self.conn, self.cur = connect_db()
                try:
                    self.cur.execute("update products set id=%s, name=%s, date_save=%s, price=%s where id=%s",
                                     (self.data_to_edit.get("ID"),
                                      self.data_to_edit.get("Имя"),
                                      self.data_to_edit.get("Срок"),
                                      self.data_to_edit.get("Цена"),
                                      id_remember),
                                     )
                    self.conn.commit()
                    self.load()
                except Exception as err:
                    self.conn.rollback()
                    message(self, "Ошибка", f"Ошибка изменения данных: {str(err)}")
                finally:
                    self.conn.close()
        else:
            message(self, "Ошибка", "Выберите строку")

    def delete(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.conn, self.cur = connect_db()
            try:
                id_product = self.table.item(current_row, 0).text()
                self.cur.execute("delete from products where id = %s", (id_product,))
                self.conn.commit()
                self.load()
            except Exception as err:
                message(self, "Ошибка", f"Ошибка при удалении данных: {err}")
            finally:
                self.conn.close()
        else:
            message(self, "Ошибка", "Выберите строку")

    def poisk1(self):
        name = self.input1.text()
        self.load("select * from products where name like %s", (f"%{name}%",))

    def poisk2(self):
        date = self.input2.text()
        self.load("select * from products where date_save >= %s", (date,))


class Reg(QWidget):
    def __init__(self, login_window=None):
        super().__init__()

        self.setWindowTitle('регистрация')
        self.setGeometry(1350, 150, 400, 800)

        self.label1 = create_label(self, "Логин", 160, 50)
        self.input1 = create_input(self, 50, 120, 300, 35)
        self.label2 = create_label(self, "Пароль", 160, 200)
        self.input2 = create_input(self, 50, 270, 300, 35)
        self.input2.setEchoMode(QLineEdit.Password)
        self.label3 = create_label(self, "Повторите пароль", 100, 350)
        self.input3 = create_input(self, 50, 420, 300, 35)
        self.input3.setEchoMode(QLineEdit.Password)
        self.button2 = create_button(self, 50, 570, 300, 50, "Зарегистрироваться", self.registr)
        self.button1 = create_button(self, 50, 650, 300, 50, "Войти", self.login)

        self.main_window = None
        self.login_window = login_window

        self.conn, self.cur = connect_db()

    def login(self):
        try:
            self.hide()
            if self.login_window:
                self.login_window.show()
        except Exception as err:
            message(self, "Ошибка", f"Ошибка открытия окна: {str(err)}")

    def registr(self):
        try:
            username, password, password1 = self.input1.text(), self.input2.text(), self.input3.text()

            if password != password1:
                message(self, "Неверный пароль", "Пароли не совпадают")
                return

            elif len(password) < 6:
                message(self, "Неверный пароль", "Пароль слишком короткий")
                return

            else:
                self.cur.execute("insert into user(username, password) values (%s, %s);",
                                 (username, password))
                self.conn.commit()
                message(self, "Успешная регистрация", "Вы успешно зарегистрировались")
                self.hide()
                if self.login_window:
                    self.login_window.show()

        except Exception as err:
            self.conn.rollback()
            message(self, "Ошибка", f"Ошибка в приложении {str(err)}")
        finally:
            self.conn.close()


class Login(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('вход')
        self.setGeometry(1350, 150, 400, 800)

        self.label1 = create_label(self, "Логин", 160, 50)
        self.input1 = create_input(self, 50, 120, 300, 35)
        self.label2 = create_label(self, "Пароль", 160, 200)
        self.input2 = create_input(self, 50, 270, 300, 35)
        self.input2.setEchoMode(QLineEdit.Password)

        self.button1 = create_button(self, 50, 570, 300, 50, "Войти", self.login)
        self.button2 = create_button(self, 50, 650, 300, 50, "Зарегистрироваться", self.registr)

        self.main_window = None
        self.reg_window = None

        self.conn, self.cur = connect_db()

    def login(self):
        try:
            username, password = self.input1.text(), self.input2.text()
            self.cur.execute("select id from user where username = %s and password = %s", (username, password))
            id_user = self.cur.fetchone()

            if id_user:
                message(self, "Успешный вход", "Добро пожаловать")
                self.hide()
                self.main_window = Window()
                self.main_window.show()
            else:
                message(self, "Ошибка", "Неверный логин или пароль")

        except Exception as err:
            message(self, "Ошибка", f"Ошибка в приложении {str(err)}")
        finally:
            self.conn.close()

    def registr(self):
        try:
            self.reg_window = Reg(self)
            self.hide()
            self.reg_window.show()
        except Exception as err:
            message(self, "Ошибка", f"Ошибка открытия окна: {str(err)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    sys.exit(app.exec_())

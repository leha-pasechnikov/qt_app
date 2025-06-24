import sys
from datetime import datetime

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QDialog, QApplication, QMessageBox, QLineEdit, QTableWidget
import mysql.connector


class Database(object):
    def __init__(self):
        self.__host = "localhost"
        self.__user = "root"
        self.__database = "exam"
        self.__password = ""

        self.conn, self.cur = None, None

    def close(self):
        self.conn.close()
        self.cur.close()

    def connect(self):
        try:
            self.conn = mysql.connector.connect(host=self.__host,
                                                user=self.__user,
                                                database=self.__database,
                                                password=self.__password)
            if self.conn.is_connected():
                self.cur = self.conn.cursor()
                return self.conn, self.cur
            return False
        except Exception as err:
            print(f"Ошибка подключения к бд: {err}")
            return False

    def execute(self, sql, param=()):
        self.conn, self.cur = self.connect()
        try:
            self.cur.execute(sql, param)
            self.conn.commit()
        except Exception as err:
            self.conn.rollback()
            raise ValueError(f"Ошибка при выполнении запроса: {err}")
        finally:
            self.close()

    def query(self, sql, param):
        self.conn, self.cur = self.connect()
        try:
            self.cur.execute(sql, param)
            return self.cur.fetchall()
        except Exception as err:
            raise ValueError(f"Ошибка при выполнении запроса: {err}")
        finally:
            self.close()


class User(Database):
    def __init__(self):
        super().__init__()
        self.id = None
        self.username = None
        self.password = None

    def check(self):
        if self.id is not None:
            if not isinstance(self.id, int):
                raise TypeError("id должен быть целым числом (int)")
            elif self.id < 0:
                raise TypeError("id должен быть больше нуля")

        if not isinstance(self.username, str):
            raise TypeError("username должен быть строкой (str)")
        elif not self.username.strip():
            raise ValueError("username должен быть непустой строкой")

        if not isinstance(self.password, str):
            raise TypeError("password должен быть строкой (str)")
        elif not self.password.strip():
            raise ValueError("password должен быть непустой строкой")

    def add(self, username, password, id_user=None):
        self.id = id_user
        self.username = username
        self.password = password
        self.check()

        if self.id:
            self.execute("insert into user(id, username, password) values(%s, %s, %s);",
                         (self.id, self.username, self.password))
        else:
            self.execute("insert into user(username, password) values(%s, %s);",
                         (self.username, self.password))

    def select(self, username, password):
        self.username = username
        self.password = password
        self.check()
        return self.query("select * from user where username = %s and password = %s;", (username, password))


class Products(Database):
    def __init__(self):
        super().__init__()
        self.id = None
        self.name = None
        self.date = None
        self.price = None

    def check(self):
        if self.id is not None:
            if not isinstance(self.id, int):
                raise TypeError("id должен быть целым числом (int)")
            elif self.id < 0:
                raise ValueError("id должен быть больше или равен нулю")

        if not isinstance(self.name, str):
            raise TypeError("name должно быть строкой (str)")
        elif not self.name.strip():
            raise ValueError("name не должно быть пустой строкой")

        if not isinstance(self.date, str):
            raise TypeError("date должно быть строкой (str)")
        elif not self.date.strip():
            raise ValueError("date не должно быть пустой строкой")
        else:
            try:
                datetime.strptime(self.date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Дата должна быть в формате ГГГГ-ММ-ДД")

        if not isinstance(self.price, float):
            raise TypeError("price должно быть числом (float)")
        elif self.price <= 0:
            raise ValueError("price должно быть больше нуля")

    def add(self, name, date, price, id_user=None):
        self.id = id_user
        self.name = name
        self.date = date
        self.price = price
        self.check()

        if self.id:
            self.execute("insert into products(id, name, date_save, price) values(%s, %s, %s, %s);",
                         (self.id, self.name, self.date, self.price))
        else:
            self.execute("insert into products(name, date_save, price) values(%s, %s, %s);",
                         (self.name, self.date, self.price))

    def edit(self, name, date, price, new_id, last_id):
        self.id = new_id
        self.name = name
        self.date = date
        self.price = price
        self.check()

        self.execute("update products set id=%s, name=%s, date_save=%s, price=%s where id = %s;",
                     (self.id, self.name, self.date, self.price, last_id))

    def select(self, sql="select * from  products", param=()):
        return self.query(sql, param)

    def delete(self, id_delete):
        if isinstance(id_delete, int):
            self.execute("delete from products where id = %s;", (id_delete,))
        else:
            raise ValueError("id_delete должен быть числом (int)")


def message(win, title, text):
    QMessageBox.information(win, title, text)


def date_to_str(date):
    return str(datetime.strptime(date, "%d.%m.%Y").date())


class EditDialog(QDialog):
    def __init__(self, new_id=None, name=None, date=None, price=None):
        super().__init__()
        uic.loadUi("dialog.ui", self)

        if new_id:
            self.spinBox.setValue(new_id)
        if name:
            self.lineEdit_2.setText(name)
        if date:
            self.dateEdit.setDate(date)
        if price:
            self.doubleSpinBox.setValue(price)

        self.pushButton.clicked.connect(lambda: self.do())
        self.values = {"name": None, "date": None, "price": None, "id": None}

    def do(self):
        try:
            self.values = {"name": self.lineEdit_2.text(),
                           "date": date_to_str(self.dateEdit.text()),
                           "price": float(self.doubleSpinBox.text().replace(',', '.')),
                           "id": int(self.spinBox.text())
                           }
            self.accept()
        except Exception as err:
            message(self, "Ошибка", str(err))


class Main(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("main.ui", self)

        column_width = 275
        self.tableWidget.setColumnWidth(0, column_width)
        self.tableWidget.setColumnWidth(1, column_width)
        self.tableWidget.setColumnWidth(2, column_width)
        self.tableWidget.setColumnWidth(3, column_width)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)

        self.pushButton_3.clicked.connect(self.add)
        self.pushButton_4.clicked.connect(self.edit)
        self.pushButton_5.clicked.connect(self.delete)

        self.pushButton_6.clicked.connect(self.poisk1)
        self.pushButton_7.clicked.connect(self.poisk2)

        self.pushButton_8.clicked.connect(lambda: self.load())

        self.product = Products()
        self.load()

    def load_data(self, data):
        self.tableWidget.setRowCount(len(data))
        for row in range(len(data)):
            for col, item in enumerate(data[row]):
                self.tableWidget.setItem(row, col, QtWidgets.QTableWidgetItem(str(item)))

    def load(self):
        data = self.product.select()
        self.load_data(data)

    def add(self):
        window_edit = EditDialog()
        if window_edit.exec_():
            try:
                self.product.add(*window_edit.values.values())
                message(self, "Успех", "Данные успешно добавлены")
                self.load()
            except Exception as err:
                message(self, "Ошибка", f"Произошла ошибка при заполнении данных: {err}")
        del window_edit

    def edit(self):
        current_row = self.tableWidget.currentRow()
        if current_row != -1:
            last_id = int(self.tableWidget.item(current_row, 0).text())
            last_name = self.tableWidget.item(current_row, 1).text()
            last_date = datetime.strptime(self.tableWidget.item(current_row, 2).text(), "%Y-%m-%d")
            last_price = float(self.tableWidget.item(current_row, 3).text())
            window_edit = EditDialog(last_id, last_name, last_date, last_price)
            if window_edit.exec_():
                self.product.edit(*window_edit.values.values(), last_id)
                self.load()
                message(self, "Успех", "Данные успешно изменены")
        else:
            message(self, "Ошибка", "Выберите строку для изменения")

    def delete(self):
        current_row = self.tableWidget.currentRow()
        if current_row != -1:
            id_del = self.tableWidget.item(current_row, 0).text()
            self.product.delete(int(id_del))
            self.load()
        else:
            message(self, "Ошибка", "Выберите строку для удаления")

    def poisk1(self):
        text = self.lineEdit_3.text()
        data = self.product.select("select * from products where name like %s;", (f"%{text}%",))
        self.load_data(data)

    def poisk2(self):
        date = self.dateEdit.text()
        date = date_to_str(date)
        data = self.product.select("select * from products where date_save >= %s;", (date,))
        self.load_data(data)


class Reg(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("registr.ui", self)

        self.pushButton.clicked.connect(self.reg)
        self.pushButton_2.clicked.connect(self.back)

        self.lineEdit_2.setEchoMode(QLineEdit.Password)
        self.lineEdit_3.setEchoMode(QLineEdit.Password)

    def back(self):
        self.accept()

    def reg(self):
        login = self.lineEdit.text()
        password = self.lineEdit_2.text()
        password_2 = self.lineEdit_3.text()

        if password != password_2:
            message(self, "Ошибка", "Пароли должны совпадать!")
            return

        if len(password) < 6:
            message(self, "Ошибка", "Пароль должен быть длиннее 6 символов!")
            return
        try:
            person = User()
            person.add(login, password)
            del person

            message(self, "Успех", "Вы успешно зарегистрировались")
            self.accept()
        except Exception as err:
            message(self, "Ошибка", f"Произошла ошибка при регистрации: {err}")


class Login(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("login.ui", self)

        self.pushButton.clicked.connect(self.login)
        self.pushButton_2.clicked.connect(self.reg)

        self.lineEdit_2.setEchoMode(QLineEdit.Password)

        self.reg_window = None
        self.main_window = None

    def login(self):
        login = self.lineEdit.text()
        password = self.lineEdit_2.text()

        person = User()
        res = person.select(login, password)
        del person

        if res:
            self.main_window = Main()
            message(self, "Вход", "Добро пожаловать")
            self.close()
            self.main_window.show()
        else:
            message(self, "Ошибка", "Неверный логин или пароль")

    def reg(self):
        self.reg_window = Reg()
        self.reg_window.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    sys.exit(app.exec_())

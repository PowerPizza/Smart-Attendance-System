import os
from PyQt5.QtWidgets import *
from additional_widgets import *
from PyQt5.QtCore import Qt, QThread, QSize
from PyQt5.QtGui import QIntValidator, QIcon
from database_manager import MsAccessDriver, EncodeType

class CredEntry(QGroupBox):
    entry_ = None
    edit_enabled = False
    show_text= False
    def __init__(self, title):
        super().__init__()
        self.setTitle(title)
        self.setObjectName("cred_entry")

        layout_ = QHBoxLayout(self)
        self.entry_ = QLineEdit()
        self.entry_.setObjectName("input_field")
        self.entry_.setEnabled(self.edit_enabled)
        self.entry_.setEchoMode(QLineEdit.Password)
        layout_.addWidget(self.entry_)

        self.btn_eye = btn_eye = QPushButton()
        btn_eye.setIcon(QIcon("icons/eye_close_icon.svg"))
        btn_eye.setIconSize(QSize(24, 24))
        btn_eye.clicked.connect(self.on_eye_click)
        btn_eye.setCursor(Qt.PointingHandCursor)
        layout_.addWidget(btn_eye)

        self.btn_edit = btn_edit = QPushButton()
        btn_edit.setIcon(QIcon("icons/pencil_icon.svg"))
        btn_edit.clicked.connect(self.on_edit_click)
        btn_edit.setIconSize(QSize(24, 24))
        btn_edit.setCursor(Qt.PointingHandCursor)
        layout_.addWidget(btn_edit)

    def setValue(self, value_):
        self.entry_.setText(str(value_))

    def getValue(self):
        return self.entry_.text()

    def on_edit_click(self):
        if not self.edit_enabled:
            self.btn_edit.setStyleSheet("border: 2px solid #32b8c6;")
        else:
            self.btn_edit.setStyleSheet("border: 2px solid transparent;")
        self.edit_enabled = not self.edit_enabled
        self.entry_.setEnabled(self.edit_enabled)

    def on_eye_click(self):
        if not self.show_text:
            self.btn_eye.setIcon(QIcon("icons/eye_open_icon.svg"))
            self.entry_.setEchoMode(QLineEdit.Normal)
        else:
            self.btn_eye.setIcon(QIcon("icons/eye_close_icon.svg"))
            self.entry_.setEchoMode(QLineEdit.Password)
        self.show_text = not self.show_text

class AdminCredentialsArea(QFrame):
    db_instance = None
    entry_username = None
    entry_password = None
    def __init__(self, db_instance:MsAccessDriver):
        super().__init__()
        self.db_instance = db_instance
        layout_ = QHBoxLayout(self)

        ui_holder = QGroupBox()
        ui_holder.setTitle("Admin Credentials")
        ui_holder_layout = QVBoxLayout(ui_holder)
        ui_holder_layout.setContentsMargins(12, 20, 12, 12)

        self.entry_username = CredEntry("User Name")
        ui_holder_layout.addWidget(self.entry_username)

        self.entry_password = CredEntry("Password")
        ui_holder_layout.addWidget(self.entry_password)
        self.load_default_values()

        btn_save = QPushButton("Save")
        btn_save.setObjectName("btn_save")
        btn_save.setFixedWidth(250)
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self.on_save)
        ui_holder_layout.addWidget(btn_save, alignment=Qt.AlignHCenter)

        layout_.addWidget(ui_holder)

    def load_default_values(self):
        try:
            self.db_instance.cursor.execute("SELECT user_name, password FROM admin_creds WHERE field_no=?", 0)
            db_resp = self.db_instance.cursor.fetchone()
            self.entry_username.setValue(MsAccessDriver.decrypt(EncodeType(db_resp[0])))
            self.entry_password.setValue(MsAccessDriver.decrypt(EncodeType(db_resp[1])))
        except BaseException as e:
            print(e)

    def on_save(self):
        try:
            if not self.entry_username.getValue() or not self.entry_password.getValue():
                MessageBox().show_message("Error", "Please fill the enties.", "error")
                return
            uname_ = MsAccessDriver.encrypt(self.entry_username.getValue()).data
            password_ = MsAccessDriver.encrypt(self.entry_password.getValue()).data
            self.db_instance.cursor.execute("UPDATE admin_creds SET user_name=?, password=? WHERE field_no=?", uname_, password_, 0)
            if not self.db_instance.cursor.rowcount:
                MessageBox().show_message("Error", "Unable to save credentials.\nError : Unknown", "error")
                return
            self.db_instance.cursor.commit()
            MessageBox().show_message("Success", "Admin login credentials has been changed successfully.", "info")
        except BaseException as e:
            MessageBox().show_message("Error", f"Unable to save credentials.\nError : {e}", "error")

class SettingsPage(QFrame):
    def __init__(self, db_instance:MsAccessDriver):
        super().__init__()
        with open("style_sheets/settings_page.css", "r") as fp:
            self.setStyleSheet(fp.read())
        self.setObjectName("settings_body")

        layout_ = QVBoxLayout(self)
        layout_.setContentsMargins(0, 0, 0, 0)

        scrollable_ = QScrollArea(self)
        scrollable_.setObjectName("scroll_area")
        scrollable_.setWidgetResizable(True)

        ui_area = QWidget()
        ui_area.setObjectName("ui_area")
        ui_area_layout = QVBoxLayout(ui_area)

        admin_cred_area = AdminCredentialsArea(db_instance=db_instance)
        admin_cred_area.setObjectName("admin_cred_area")
        ui_area_layout.addWidget(admin_cred_area)

        ui_area_layout.addStretch(1)
        scrollable_.setWidget(ui_area)

        layout_.addWidget(scrollable_)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app_ = QApplication([])

    win_ = QMainWindow()
    ele_ = SettingsPage()
    win_.setCentralWidget(ele_)
    win_.show()

    app_.exec()
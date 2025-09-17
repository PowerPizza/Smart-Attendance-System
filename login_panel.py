from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from database_manager import MsAccessDriver, EncodeType
from additional_widgets import MessageBox

class LoginPanel(QFrame):
    username = None
    password = None
    db_instance = None
    def __init__(self, db_instance:MsAccessDriver):
        super().__init__()
        self.db_instance = db_instance
        self.setObjectName("login_screen")
        with open("style_sheets/login_panel.css", "r") as fp:
            self.setStyleSheet(fp.read())

        main_layout = QVBoxLayout(self)

        card = QFrame()
        card.setMinimumWidth(400)
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)

        title = QLabel("<h1>Smart Attendance System</h1>")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        self.username = username = QLineEdit()
        username.setObjectName("entry")
        username.setPlaceholderText("Username")
        card_layout.addWidget(username)

        # Password input
        self.password = password = QLineEdit()
        password.setObjectName("entry")
        password.setPlaceholderText("Password")
        password.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(password)

        # Login button
        self.login_button = login_button = QPushButton("Login as Admin")
        login_button.setObjectName("login_btn")
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.setDefault(True)
        card_layout.addWidget(login_button)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("color: #444;")
        card_layout.addWidget(divider)

        # Footer (Student link)
        footer_layout = QHBoxLayout()
        footer_layout.setAlignment(Qt.AlignCenter)
        student_label = QLabel("Student?")
        student_label.setStyleSheet("color: white; font-size: 16px;")
        footer_layout.addWidget(student_label)

        self.mark_attendance = QPushButton('Mark Attendance')
        self.mark_attendance.setObjectName("mark_attendance")
        self.mark_attendance.setCursor(Qt.PointingHandCursor)
        footer_layout.addWidget(self.mark_attendance)

        card_layout.addLayout(footer_layout)

        main_layout.addWidget(card, alignment=Qt.AlignCenter)

    def onOpenFaceAttendancePanel(self, callback_):
        self.mark_attendance.clicked.connect(callback_)

    def onClickLogin(self, callback_):
        def callback_caller():
            try:
                self.db_instance.cursor.execute("SELECT user_name, password FROM admin_creds WHERE field_no=?", 0)
                db_resp = self.db_instance.cursor.fetchone()
                db_uname = MsAccessDriver.decrypt(EncodeType(db_resp[0]))
                db_pass = MsAccessDriver.decrypt(EncodeType(db_resp[1]))
                if self.username.text() != db_uname or self.password.text() != db_pass:
                    MessageBox().show_message("Error", "Failed to login.\nError : INVALID CREDENTIALS", "error")
                    return
                callback_()
            except BaseException as e:
                MessageBox().show_message("Error", f"Failed to login.\nError : {e}", "error")
        self.login_button.clicked.connect(callback_caller)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app_ = QApplication([])

    win_ = QMainWindow()
    ele_ = LoginPanel()
    win_.setCentralWidget(ele_)
    win_.show()

    app_.exec()
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class LoginPanel(QFrame):
    def __init__(self):
        super().__init__()
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

        username = QLineEdit()
        username.setObjectName("entry")
        username.setPlaceholderText("Username")
        card_layout.addWidget(username)

        # Password input
        password = QLineEdit()
        password.setObjectName("entry")
        password.setPlaceholderText("Password")
        password.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(password)

        # Login button
        self.login_button = login_button = QPushButton("Login as Admin")
        login_button.setObjectName("login_btn")
        login_button.setCursor(Qt.PointingHandCursor)
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
        self.login_button.clicked.connect(callback_)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app_ = QApplication([])

    win_ = QMainWindow()
    ele_ = LoginPanel()
    win_.setCentralWidget(ele_)
    win_.show()

    app_.exec()
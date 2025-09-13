from PyQt5.QtWidgets import *
from additional_widgets import *
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QIntValidator, QIcon
from app_constants import AppConstant
from excel_functions import *

class AutoAttendancePage(QFrame):
    def __init__(self):
        super().__init__()
        with open("style_sheets/auto_attendance_page.css", "r") as fp:
            self.setStyleSheet(fp.read())
        self.setObjectName("auto_attendance_body")

        layout_ = QVBoxLayout(self)

        content_area = QFrame()
        content_area.setObjectName("content_area")
        content_area_layout = QVBoxLayout(content_area)

        title_ = QLabel("<h1>Live Face Attendance</h1>")
        title_.setObjectName("title_")
        content_area_layout.addWidget(title_, alignment=Qt.AlignHCenter)

        cam_preview = QImageView("tests/a.png", size=(600, 600))
        cam_preview.setObjectName("cam_preview")
        content_area_layout.addWidget(cam_preview, alignment=Qt.AlignHCenter)

        log_area = QFrame()
        log_area_layout = QVBoxLayout(log_area)
        log_area.setObjectName("log_area")
        lbl_info = QLabel("No face detected.")
        log_area_layout.addWidget(lbl_info)
        content_area_layout.addWidget(log_area)

        start_btn = QPushButton("Start")
        start_btn.setObjectName("btn")
        start_btn.setProperty("ui", "blue")
        start_btn.setCursor(Qt.PointingHandCursor)
        content_area_layout.addWidget(start_btn)

        stop_btn = QPushButton("Stop")
        stop_btn.setObjectName("btn")
        stop_btn.setVisible(False)
        stop_btn.setProperty("ui", "red")
        stop_btn.setCursor(Qt.PointingHandCursor)
        content_area_layout.addWidget(stop_btn)

        hr_ = QFrame()
        hr_.setFixedHeight(1)
        QHBoxLayout(hr_)
        hr_.setStyleSheet("border: 1px solid gray;")
        content_area_layout.addWidget(hr_)

        self.admin_login = QPushButton("Admin Login")
        self.admin_login .setObjectName("admin_login")
        self.admin_login .setCursor(Qt.PointingHandCursor)
        content_area_layout.addWidget(self.admin_login , alignment=Qt.AlignHCenter)

        layout_.addWidget(content_area, alignment=Qt.AlignCenter)

    def onClickAdminLogin(self, callback_):
        self.admin_login.clicked.connect(callback_)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app_ = QApplication([])

    win_ = QMainWindow()
    ele_ = AutoAttendancePage()
    win_.setCentralWidget(ele_)
    win_.show()

    app_.exec()
import os
import pickle

import face_recognition
from PyQt5.QtWidgets import *
from additional_widgets import *
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QIntValidator, QIcon
from app_constants import AppConstant
from excel_functions import *
from qt_theading import LiveFaceRecorder

class AutoAttendancePage(QFrame):
    cam_preview = None
    td1 = None
    admin_login = None
    worker_ = None
    stop_btn = None
    start_btn = None
    lbl_info = None
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

        self.cam_preview = QImageView("icons/no_face_detected.png", size=(500, 400))
        self.cam_preview.setObjectName("cam_preview")
        content_area_layout.addWidget(self.cam_preview, alignment=Qt.AlignHCenter)

        log_area = QFrame()
        log_area_layout = QVBoxLayout(log_area)
        log_area.setObjectName("log_area")
        self.lbl_info = QLabel("No face detected.")
        log_area_layout.addWidget(self.lbl_info)
        content_area_layout.addWidget(log_area)

        self.start_btn = start_btn = QPushButton("Start")
        start_btn.setObjectName("btn")
        start_btn.setProperty("ui", "blue")
        start_btn.setCursor(Qt.PointingHandCursor)
        start_btn.clicked.connect(self.start_live_camera)
        content_area_layout.addWidget(start_btn)

        self.stop_btn = stop_btn = QPushButton("Stop")
        stop_btn.setObjectName("btn")
        stop_btn.setVisible(False)
        stop_btn.setProperty("ui", "red")
        stop_btn.setCursor(Qt.PointingHandCursor)
        stop_btn.clicked.connect(self.stop_live_camera)
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


    def start_live_camera(self):
        def on_msg(msg):
            if msg["type"] == "warn":
                self.cam_preview.setIcon("icons/no_face_detected.png")
            self.lbl_info.setText(msg["msg"])

        def on_face_encodings(ecd):
            try:
                for encoding_file in os.listdir(AppConstant.ENCODINGS_DIRECTORY):
                    with open(os.path.join(AppConstant.ENCODINGS_DIRECTORY, encoding_file), "rb") as fp:
                        known_enc = pickle.load(fp)
                    resp_ = face_recognition.compare_faces(known_enc["encodings"], ecd)
                    # sheet_ =
                    print(known_enc["admission_no"])
            except BaseException as e:
                print(e)
        def on_face_img(img):
            self.cam_preview.setIconFromBytes(img)

        self.td1 = QThread()
        self.td1.started.connect(self.show_stop_btn)
        self.td1.finished.connect(self.show_start_btn)
        self.worker_ = LiveFaceRecorder()
        self.worker_.moveToThread(self.td1)
        self.td1.started.connect(self.worker_.run)
        self.worker_.face_img_channel.connect(on_face_img)
        self.worker_.msg_channel.connect(on_msg)
        self.worker_.face_encoding_channel.connect(on_face_encodings)
        self.td1.start()

    def stop_live_camera(self):
        try:
            self.worker_.stop()
            self.td1.quit()
            self.td1.wait()
            self.td1 = None
            self.worker_ = None
            self.cam_preview.setIcon("icons/no_face_detected.png")
        except BaseException as e:
            print(e)

    def show_start_btn(self):
        self.stop_btn.setVisible(False)
        self.start_btn.setVisible(True)
    def show_stop_btn(self):
        self.start_btn.setVisible(False)
        self.stop_btn.setVisible(True)

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
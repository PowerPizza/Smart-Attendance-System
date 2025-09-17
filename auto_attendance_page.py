import os
import pickle
import random

import face_recognition
import numpy as np
from PyQt5.QtWidgets import *
from additional_widgets import *
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QIntValidator, QIcon
from app_constants import AppConstant
from qt_theading import LiveFaceRecorder
from database_manager import MsAccessDriver
import datetime as real_datetime

class MarkedAttendanceTable(QFrame):
    cur_date = None
    def __init__(self):
        super().__init__()
        self.cur_date = real_datetime.datetime.now().strftime("%d-%m-%Y")

        layout_ = QVBoxLayout(self)
        lbl_table_title = QLabel(f"<h2>List Marked attendance of '{self.cur_date}'</h2>")
        lbl_table_title.setObjectName("lbl_table_title")
        layout_.addWidget(lbl_table_title, alignment=Qt.AlignHCenter)
        self.table_ = QTableWidget(self)
        self.table_.setObjectName("table_")
        self.table_.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_.setShowGrid(False)
        self.table_.verticalHeader().setVisible(False)
        self.table_.setSortingEnabled(True)
        self.table_.setColumnCount(5)
        self.table_.setMinimumWidth(550)
        self.table_.setHorizontalHeaderLabels(["Admission No.", "Student Name", "Father Name", "Class & Section", self.cur_date])
        table_header = self.table_.horizontalHeader()
        table_header.setStretchLastSection(False)
        table_header.setSortIndicatorShown(True)
        table_header.setSectionsClickable(True)
        table_header.setSortIndicator(0, Qt.AscendingOrder)
        table_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        layout_.addWidget(self.table_, alignment=Qt.AlignHCenter)

    def load_data(self, data_list):
        try:
            self.table_.setSortingEnabled(False)
            self.table_.clear()
            self.table_.setColumnCount(5)
            self.table_.setRowCount(0)
            for row_idx, row_ in enumerate(data_list):
                self.table_.insertRow(row_idx)
                for col_idx, col_ in enumerate(row_):
                    data_ = QTableWidgetItem(str(col_))
                    self.table_.setItem(row_idx, col_idx, data_)
            self.table_.setSortingEnabled(True)
        except BaseException as e:
            print(e)

    def insert_data(self, data_row):
        self.table_.setSortingEnabled(False)
        new_row_at = self.table_.rowCount()
        self.table_.insertRow(new_row_at)
        for col_idx, item in enumerate(data_row):
            data_ = QTableWidgetItem(str(item))
            self.table_.setItem(new_row_at, col_idx, data_)
        self.table_.setSortingEnabled(True)

class AutoAttendancePage(QFrame):
    cam_preview = None
    td1 = None
    admin_login = None
    worker_ = None
    stop_btn = None
    start_btn = None
    lbl_info = None
    db_instance = None
    def __init__(self, db_instance:MsAccessDriver):
        super().__init__()
        self.db_instance = db_instance
        with open("style_sheets/auto_attendance_page.css", "r") as fp:
            self.setStyleSheet(fp.read())
        self.setObjectName("auto_attendance_body")

        layout_ = QHBoxLayout(self)

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
        self.lbl_attendance_marked = QLabel("")
        log_area_layout.addWidget(self.lbl_attendance_marked)
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
        layout_.addWidget(content_area, alignment=Qt.AlignCenter, stretch=1)

        self.marked_table = marked_table = MarkedAttendanceTable()
        marked_table.setObjectName("table_holder")
        layout_.addWidget(marked_table, stretch=1)


    def start_live_camera(self):
        def on_msg(msg):
            if msg["type"] == "warn":
                self.lbl_attendance_marked.setText("")
                self.cam_preview.setIcon("icons/no_face_detected.png")
            self.lbl_info.setText(f'{random.choice("🔹🔸")} {msg["msg"]}')

        def on_face_encodings(ecd):
            try:
                for encoding_file in os.listdir(AppConstant.ENCODINGS_DIRECTORY):
                    with open(os.path.join(AppConstant.ENCODINGS_DIRECTORY, encoding_file), "rb") as fp:
                        known_enc = pickle.load(fp)
                    resp_ = face_recognition.compare_faces(known_enc["encodings"], ecd)
                    if resp_.count(np.True_) > resp_.count(np.False_):
                        found_adm_no = known_enc["admission_no"]
                        self.db_instance.cursor.execute("SELECT student_name, father_name, class, section FROM students WHERE admission_no=?", found_adm_no)
                        data_found = self.db_instance.cursor.fetchone()
                        if not data_found:
                            self.lbl_info.setText(f"Face detected : but this student not exists in database, please add him/her first.")
                            return
                        self.lbl_info.setText(f"Face detected :\n\tStudent Name : {data_found[0]}\n\tFather Name : {data_found[1]}\n\tClass & Section : {data_found[2]}-{data_found[3]}")
                        date_ = real_datetime.datetime.now().date()
                        self.db_instance.cursor.execute("SELECT * FROM attendance WHERE admission_no=? AND mark_date=?", found_adm_no, date_)
                        db_resp = self.db_instance.cursor.fetchone()
                        if db_resp:
                            self.lbl_attendance_marked.setText("🔴 Already Marked")
                        else:
                            self.db_instance.cursor.execute("SELECT MAX(id) FROM attendance")
                            new_id = self.db_instance.cursor.fetchone()[0]
                            new_id = 0 if new_id is None else new_id
                            self.db_instance.cursor.execute("INSERT INTO attendance VALUES (?, ?, ?, ?)", new_id+1, found_adm_no, date_, "P")
                            self.db_instance.cursor.commit()
                            self.lbl_attendance_marked.setText("🟢 Attendance Marked")
                            self.marked_table.insert_data([found_adm_no, data_found[0], data_found[1], f"{data_found[2]}-{data_found[3]}", "P"])
                        break
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
        def callback_with_stop():
            self.stop_live_camera()
            callback_()
        self.admin_login.clicked.connect(callback_with_stop)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app_ = QApplication([])

    win_ = QMainWindow()
    ele_ = AutoAttendancePage()
    win_.setCentralWidget(ele_)
    win_.show()

    app_.exec()
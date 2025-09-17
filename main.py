import os.path

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QIcon, QFont
from additional_widgets import *
from login_panel import LoginPanel
from admin_panel import AdminPanel
from auto_attendance_page import AutoAttendancePage
from excel_functions import *
from app_constants import *
from database_manager import MsAccessDriver

def create_shadow(blur_radius:int, color_hex:str, offset_xy:tuple=(0, 0), parent=None):
    shadow_ = QGraphicsDropShadowEffect(parent)
    shadow_.setBlurRadius(blur_radius)
    shadow_.setColor(QColor(color_hex))
    shadow_.setOffset(offset_xy[0], offset_xy[1])
    return shadow_

def setup_database():
    if not os.path.exists(AppConstant.DATA_DIRECTORY):
        os.mkdir(AppConstant.DATA_DIRECTORY)
    if not os.path.exists(AppConstant.CLASS_DIRECTORY):
        os.mkdir(AppConstant.CLASS_DIRECTORY)
    if not os.path.exists(AppConstant.ENCODINGS_DIRECTORY):
        os.mkdir(AppConstant.ENCODINGS_DIRECTORY)
    if not os.path.exists(AppConstant.STUDENTS_DIRECTORY):
        os.mkdir(AppConstant.STUDENTS_DIRECTORY)
    if not os.path.exists(AppConstant.STUDENTS_FILE):
        createStudentsExcelFile(AppConstant.STUDENTS_FILE)

class MainApplication(QApplication):
    main_window = None
    _screen_w = None
    _screen_h = None
    db_ = None

    def __init__(self):
        super().__init__([])
        try:
            setup_database()
            self.db_ = MsAccessDriver()  # initializing database, it will auto-create required tables etc, if not exits.
        except BaseException as e:
            MessageBox().show_message("Error", f"An error occur while setting up database.\nError : {e}", "error")
            exit(0)

        self._screen_w, self._screen_h = QDesktopWidget().width(), QDesktopWidget().height()
        window_w, window_h = (600, 400)
        window_x, window_y = (self._screen_w // 2) - (window_w // 2), (self._screen_h // 2) - (window_h // 2)
        self.main_window = QMainWindow()
        self.main_window.setGeometry(window_x, window_y, window_w, window_h)
        self.main_window.setWindowTitle("Smart Attendance System")

        self.create_login_panel()

    def create_login_panel(self):
        login_form_ = LoginPanel(db_instance=self.db_)
        login_form_.onOpenFaceAttendancePanel(self.face_attendance_panel)
        login_form_.onClickLogin(self.open_admin_panel)
        self.main_window.setCentralWidget(login_form_)

    def face_attendance_panel(self):
        panel_ = AutoAttendancePage(db_instance=self.db_)
        panel_.onClickAdminLogin(self.create_login_panel)
        self.main_window.setCentralWidget(panel_)

    def open_admin_panel(self):
        admin_panel = AdminPanel(self.main_window, db_instance=self.db_)
        admin_panel.setLogoutCommand(self.create_login_panel)
        self.main_window.setCentralWidget(admin_panel)

    def run(self):
        self.main_window.show()
        self.exec()

if __name__ == '__main__':
    app_ = MainApplication()
    app_.run()

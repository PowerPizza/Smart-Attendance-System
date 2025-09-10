import os.path

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QIcon
from additional_widgets import *
from class_n_section import ClassNSectionPage
from students_page import StudentsPage
from attendance_page import AttendancePage
from app_constants import *
from excel_functions import *

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
    if not os.path.exists(AppConstant.STUDENTS_DIRECTORY):
        os.mkdir(AppConstant.STUDENTS_DIRECTORY)
    if not os.path.exists(AppConstant.STUDENTS_FILE):
        createStudentsExcelFile(AppConstant.STUDENTS_FILE)

class MainApplication(QApplication):
    main_window = None
    _screen_w = None
    _screen_h = None
    _selected_tab_action = None

    def __init__(self):
        super().__init__([])
        try:
            setup_database()
        except BaseException as e:
            MessageBox().show_message("Error", f"An error occur while setting up database.\nError : {e}", "error")
            exit(0)

        self._screen_w, self._screen_h = QDesktopWidget().width(), QDesktopWidget().height()
        window_w, window_h = (600, 400)
        window_x, window_y = (self._screen_w // 2) - (window_w // 2), (self._screen_h // 2) - (window_h // 2)
        self.main_window = QMainWindow()
        self.main_window.setGeometry(window_x, window_y, window_w, window_h)
        self.main_window.setWindowTitle("Smart Attendance System")

        with open("style_sheets/main_window.css", "r") as fp:
            self.setStyleSheet(fp.read())

        self.main_body = QWidget()
        self.main_body.setObjectName("main_body")
        self.main_body.setStyleSheet("#main_body {background-color: #1f2121;}")
        self.layout_ = QVBoxLayout()
        self.main_body.setLayout(self.layout_)

        main_header = Header()
        self.layout_.addWidget(main_header, stretch=0)

        # --------------- TOOL BAR STARTS ------------------------
        tool_bar = QToolBar("MY TB", self.main_window)
        tool_bar.setObjectName("tool_bar")

        class_n_sec = QAction("Class && Section", self.main_window)
        class_n_sec.setCheckable(True)
        class_n_sec.triggered.connect(lambda: self.onChangeWindow(class_n_sec, ClassNSectionPage()))
        tool_bar.addAction(class_n_sec)

        students = QAction("Students", self.main_window)
        students.setCheckable(True)
        students.triggered.connect(lambda: self.onChangeWindow(students, StudentsPage()))
        tool_bar.addAction(students)

        attendance = QAction("Attendance", self.main_window)
        attendance.setCheckable(True)
        attendance.triggered.connect(lambda: self.onChangeWindow(attendance, AttendancePage()))
        tool_bar.addAction(attendance)

        reports = QAction("Reports", self.main_window)
        reports.setCheckable(True)
        reports.triggered.connect(lambda: self.onChangeWindow(reports))
        tool_bar.addAction(reports)

        import_export = QAction("Import/Export", self.main_window)
        import_export.setCheckable(True)
        import_export.triggered.connect(lambda: self.onChangeWindow(import_export))
        tool_bar.addAction(import_export)

        self.layout_.addWidget(tool_bar)
        for action_ in tool_bar.actions():
            btn_ = tool_bar.widgetForAction(action_)
            if btn_:
                btn_.setCursor(Qt.PointingHandCursor)
        # ------------------- TOOL BAR ENDS ----------------------

        self.content_ = content_ = ContentArea(self.main_body)
        self.layout_.addWidget(content_, stretch=1)

        # self.layout_.addStretch(1)
        self.main_window.setCentralWidget(self.main_body)

    def onChangeWindow(self, action, win_widget:QWidget):
        if self._selected_tab_action == action:
            action.setChecked(True)
            return
        if self._selected_tab_action is not None:
            self._selected_tab_action.setChecked(False)

        self._selected_tab_action = action
        self._selected_tab = win_widget
        w = self.content_.currentWidget()
        if w:
            w.deleteLater()
        self.content_.addWidget(win_widget)

        # change window code here...

    def run(self):
        self.main_window.show()
        self.exec()

class Header(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("main_header")
        layout_ = QHBoxLayout()
        heading_ = QLabel("Admin Dashboard", self)
        heading_.setObjectName("heading_")
        layout_.addWidget(heading_)
        self.setLayout(layout_)

class ContentArea(QStackedWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("contentArea")
        with open("style_sheets/main_window.css", "r") as fp:
            self.setStyleSheet(fp.read())

if __name__ == '__main__':
    app_ = MainApplication()
    app_.run()

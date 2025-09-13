import os.path

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QIcon, QFont
from additional_widgets import *
from class_n_section import ClassNSectionPage
from students_page import StudentsPage
from attendance_records_page import AttendanceRecordsPage
from mark_attendance_page import MarkAttendancePage
from auto_attendance_page import AutoAttendancePage
from login_panel import LoginPanel
from app_constants import *
from excel_functions import *

class AdminPanel(QFrame):
    _selected_tab_action = None
    _selected_tab = None
    content_ = None

    def __init__(self, window_instance):
        super().__init__()
        self.setObjectName("main_body")
        with open("style_sheets/admin_panel.css", "r") as fp:
            self.setStyleSheet(fp.read())

        layout_ = QVBoxLayout(self)

        self.main_header = Header()
        layout_.addWidget(self.main_header, stretch=0)

        # --------------- TOOL BAR STARTS ------------------------
        tool_bar = QToolBar("MY TB", window_instance)
        tool_bar.setObjectName("tool_bar")

        class_n_sec = QAction("Class && Section", window_instance)
        class_n_sec.setCheckable(True)
        class_n_sec.triggered.connect(lambda: self.onChangeWindow(class_n_sec, ClassNSectionPage()))
        tool_bar.addAction(class_n_sec)

        students = QAction("Students", window_instance)
        students.setCheckable(True)
        students.triggered.connect(lambda: self.onChangeWindow(students, StudentsPage()))
        tool_bar.addAction(students)

        attendance = QAction("Attendance Records", window_instance)
        attendance.setCheckable(True)
        attendance.triggered.connect(lambda: self.onChangeWindow(attendance, AttendanceRecordsPage()))
        tool_bar.addAction(attendance)

        mark_attendance = QAction("Mark Attendance", window_instance)
        mark_attendance.setCheckable(True)
        mark_attendance.triggered.connect(lambda: self.onChangeWindow(mark_attendance, MarkAttendancePage()))
        tool_bar.addAction(mark_attendance)

        reports = QAction("Reports", window_instance)
        reports.setCheckable(True)
        reports.triggered.connect(lambda: self.onChangeWindow(reports))
        tool_bar.addAction(reports)

        import_export = QAction("Import/Export", window_instance)
        import_export.setCheckable(True)
        import_export.triggered.connect(lambda: self.onChangeWindow(import_export))
        tool_bar.addAction(import_export)

        layout_.addWidget(tool_bar)
        for action_ in tool_bar.actions():
            btn_ = tool_bar.widgetForAction(action_)
            if btn_:
                btn_.setCursor(Qt.PointingHandCursor)
        # ------------------- TOOL BAR ENDS ----------------------

        self.content_ = ContentArea(self)
        layout_.addWidget(self.content_, stretch=1)

        # self.layout_.addStretch(1)

    def onChangeWindow(self, action, win_widget: QWidget):
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

    def setLogoutCommand(self, callback_):
        self.main_header.btn_logout.clicked.connect(callback_)

class Header(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("main_header")
        layout_ = QHBoxLayout()
        heading_ = QLabel("Admin Dashboard", self)
        heading_.setObjectName("heading_")
        layout_.addWidget(heading_)

        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setObjectName("logout_btn")
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        layout_.addWidget(self.btn_logout, alignment=Qt.AlignRight)

        self.setLayout(layout_)

class ContentArea(QStackedWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("contentArea")
        with open("style_sheets/main_window.css", "r") as fp:
            self.setStyleSheet(fp.read())

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app_ = QApplication([])

    win_ = QMainWindow()
    ele_ = AdminPanel(win_)
    win_.setCentralWidget(ele_)
    win_.show()

    app_.exec()
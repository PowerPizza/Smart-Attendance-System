import os
import openpyxl
from PyQt5.QtWidgets import *
from additional_widgets import *
from PyQt5.QtCore import Qt, QVersionNumber, QDate
from PyQt5.QtGui import QIntValidator, QIcon
from app_constants import AppConstant
import datetime as real_datetime
from excel_functions import ExcelFileWorker

class Header(QFrame):
    f_date_entries = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.f_date_entries = []
        self.setObjectName("header_")
        layout_ = QHBoxLayout(self)

        cls_n_sec_area = QGroupBox()
        cls_n_sec_area.setTitle("Select Class-Section")
        cls_n_sec_filter_layout = QHBoxLayout(cls_n_sec_area)
        self.f_select_cls_n_sec = select_cls_n_sec = QComboBox()
        select_cls_n_sec.setObjectName("cls_n_sec_select")
        cls_n_sec_filter_layout.addWidget(select_cls_n_sec)
        layout_.addWidget(cls_n_sec_area, stretch=1)
        self.load_cls_sec_list()

        current_date = real_datetime.datetime.now()
        date_filter = QGroupBox()
        date_filter.setObjectName("#date_select_frame")
        date_filter.setTitle("Select Date (DD-MM-YYYY)")
        date_filter_layout = QHBoxLayout(date_filter)
        day_entry = QComboBox()
        day_entry.setFixedWidth(50)
        for x in range(1, 32):
            day_entry.addItem(str(x))
        day_entry.setCurrentText(str(current_date.day))
        date_filter_layout.addWidget(day_entry)
        self.f_date_entries.append(day_entry)
        month_entry = QComboBox()
        month_entry.setFixedWidth(50)
        for x in range(1, 13):
            month_entry.addItem(str(x))
        month_entry.setCurrentText(str(current_date.month))
        date_filter_layout.addWidget(month_entry)
        self.f_date_entries.append(month_entry)
        year_entry = QComboBox()
        year_entry.setFixedWidth(70)
        for x in range(current_date.year-25, current_date.year+25):
            year_entry.addItem(str(x))
        year_entry.setCurrentText(str(current_date.year))
        date_filter_layout.addWidget(year_entry)
        self.f_date_entries.append(year_entry)
        layout_.addWidget(date_filter)

        self.open_sheet_btn = QPushButton("Open attendance sheet")
        self.open_sheet_btn.setObjectName("load_sheet_btn")
        self.open_sheet_btn.setCursor(Qt.PointingHandCursor)
        layout_.addWidget(self.open_sheet_btn, alignment=Qt.AlignVCenter)
        # self.on_cls_sec_change(select_cls_n_sec.currentText())

    def load_cls_sec_list(self):
        cls_sec_list = os.listdir(AppConstant.CLASS_DIRECTORY)
        if not cls_sec_list:
            self.f_select_cls_n_sec.addItem("No class found.")
        for cls_sec in cls_sec_list:
            self.f_select_cls_n_sec.addItem(cls_sec)

    def set_on_open_sheet(self, callable_):
        def launch_():
            date_ = real_datetime.date(*[int(inp.currentText()) for inp in self.f_date_entries][::-1])
            callable_(self.f_select_cls_n_sec.currentText(), date_)
        self.open_sheet_btn.clicked.connect(launch_)

class MarkAttendanceArea(QFrame):
    new_attendance = None

    def __init__(self):
        super().__init__()
        self.new_attendance = []
        self.setObjectName("marking_area")
        layout_ = QVBoxLayout(self)

        self.lbl_no_sheet = QLabel("<h2>No attendance sheet is loaded.</h2>")
        self.lbl_no_sheet.setObjectName("lbl_no_sheet")
        layout_.addWidget(self.lbl_no_sheet, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.table_ = QTableWidget(self)
        self.table_.setVisible(False)
        self.table_.setObjectName("table_")
        self.table_.setShowGrid(False)
        self.table_.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table_.verticalHeader().setVisible(False)
        self.table_.setSortingEnabled(True)
        table_header = self.table_.horizontalHeader()
        table_header.setSortIndicatorShown(True)
        table_header.setSectionsClickable(True)
        table_header.setSortIndicator(0, Qt.AscendingOrder)
        table_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        layout_.addWidget(self.table_)

    def load_sheet(self, sheet_worker:ExcelFileWorker, date_:real_datetime.date):
        students_list = zip(sheet_worker.getColumnByIndex(0), sheet_worker.getColumnByIndex(1))
        self.lbl_no_sheet.setVisible(False)
        self.table_.setSortingEnabled(False)
        self.table_.clear()
        self.table_.setRowCount(0)
        self.table_.setColumnCount(3)
        self.table_.setVisible(True)
        self.table_.setHorizontalHeaderLabels(list(students_list.__next__())+[str(date_.strftime("%d-%m-%Y"))])
        i = 0
        try:
            for adm_no, std_name in students_list:
                self.new_attendance.append('N/A')
                self.table_.insertRow(i)
                self.table_.setRowHeight(i, 60)

                adm_no_col = QTableWidgetItem()
                adm_no_col.setData(Qt.DisplayRole, int(adm_no))
                self.table_.setItem(i, 0, adm_no_col)

                std_name_col = QTableWidgetItem(std_name)
                self.table_.setItem(i, 1, std_name_col)

                marking_col = QWidget()
                marking_col.setObjectName("marking_col")
                marking_col_layout = QHBoxLayout(marking_col)
                present_opt = QRadioButton("Present")
                present_opt.setObjectName("present_opt")
                present_opt.toggled.connect(lambda _, i_copy=i: self.mark_new_attendance("P", i_copy))
                marking_col_layout.addWidget(present_opt, stretch=1)
                absent_opt = QRadioButton("Absent")
                absent_opt.setObjectName("absent_opt")
                absent_opt.toggled.connect(lambda _, i_copy=i: self.mark_new_attendance("A", i_copy))
                marking_col_layout.addWidget(absent_opt, stretch=1)
                na_opt = QRadioButton("N/A")
                na_opt.setObjectName("na_opt")
                na_opt.setChecked(True)
                na_opt.toggled.connect(lambda _, i_copy=i: self.mark_new_attendance("N/A", i_copy))
                marking_col_layout.addWidget(na_opt, stretch=1)
                self.table_.setCellWidget(i, 2, marking_col)
                i += 1
            self.table_.setSortingEnabled(True)
            if i == 0:
                self.table_.setVisible(False)
                self.lbl_no_sheet.setVisible(True)
                MessageBox().show_message("Error", f"Can't load! Attendance sheet of year '{date_.year}' has no students.", "error")
        except BaseException as e:
            print(e)

    def mark_new_attendance(self, status, idx_):
        self.new_attendance[idx_] = status

    def get_new_attendance(self):
        return self.new_attendance

class MarkAttendancePage(QFrame):
    cur_sheet_worker = None
    cur_clas_sec = None
    selected_date = None
    excel_col_to_update = None

    def __init__(self):
        super().__init__()
        with open("style_sheets/mark_attendance_page.css") as fp:
            self.setStyleSheet(fp.read())
        self.setObjectName("mark_attendance_body")
        layout_ = QVBoxLayout(self)

        self.header_ = Header(self)
        self.header_.set_on_open_sheet(self.on_open_sheet)
        layout_.addWidget(self.header_)

        bi_area = QWidget()
        bi_area_layout = QHBoxLayout(bi_area)
        bi_area_layout.setContentsMargins(0, 0, 0, 0)
        self.marking_area = marking_area = MarkAttendanceArea()
        bi_area_layout.addWidget(marking_area, stretch=1)

        page_opt_area = QWidget()
        page_opt_area.setObjectName("page_opt_area")
        page_opt_area_layout = QVBoxLayout(page_opt_area)

        btn_save = QPushButton("Save Attendance Sheet")
        btn_save.setObjectName("save_attendance_btn")
        btn_save.setFixedWidth(300)
        btn_save.clicked.connect(self.on_save_attendance)
        page_opt_area_layout.addWidget(btn_save, alignment=Qt.AlignTop | Qt.AlignRight)

        # btn_close = QPushButton("Close Attendance Sheet")
        # btn_close.setObjectName("close_attendance_btn")
        # btn_close.setFixedWidth(300)
        # btn_close.clicked.connect(self.on_save_attendance)
        # page_opt_area_layout.addWidget(btn_close, alignment=Qt.AlignTop | Qt.AlignRight)
        page_opt_area_layout.addStretch(1)
        bi_area_layout.addWidget(page_opt_area, stretch=1)
        layout_.addWidget(bi_area, stretch=1)


    def on_open_sheet(self, cls_sec, date_:real_datetime.date):
        sheet_path = os.path.join(AppConstant.CLASS_DIRECTORY, cls_sec, f"{date_.year}.xlsx")
        if not os.path.exists(sheet_path):
            MessageBox().show_message("Error", f"Class of year '{date_.year}' not exists.", "error")
            if self.selected_date:
                self.header_.f_date_entries[-1].setCurrentText(str(self.selected_date.year))
            return
        sheet_worker = ExcelFileWorker(sheet_path)
        stringed_date = str(date_.strftime("%d-%m-%Y"))
        if stringed_date in sheet_worker.getHeaderLabels():
            MessageBox().show_message("Warning", f"Attendance of date '{stringed_date}' has already been marked.\nPlease go to 'Attendance Report' page to edit.", "warn")
            return
        self.cur_clas_sec = cls_sec
        self.selected_date = date_
        self.excel_col_to_update = sheet_worker.getNoOfColumns() + 1
        self.cur_sheet_worker = sheet_worker
        self.marking_area.load_sheet(sheet_worker, date_)

    def on_save_attendance(self):
        try:
            to_add = [str(self.selected_date.strftime("%d-%m-%Y"))] + self.marking_area.get_new_attendance()
            self.cur_sheet_worker.insertColumn(self.excel_col_to_update, to_add)
            MessageBox().show_message("Success", f"Attendance for class {self.cur_clas_sec} dated {to_add[0]} has been recorded successfully.", "info")
        except BaseException as e:
            MessageBox().show_message("Error", f"Can't save attendance.\nError : {e}", "error")
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app_ = QApplication([])

    win_ = QMainWindow()
    ele_ = MarkAttendancePage()
    win_.setCentralWidget(ele_)
    win_.show()

    app_.exec()
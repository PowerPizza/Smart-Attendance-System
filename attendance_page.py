import datetime
import os

import openpyxl
from PyQt5.QtWidgets import *
from additional_widgets import *
from PyQt5.QtCore import Qt, QVersionNumber, QDate
from PyQt5.QtGui import QIntValidator, QIcon
from app_constants import AppConstant
from excel_functions import *

class AttendanceRecordTable(QFrame):
    f_select_cls_n_sec = None
    f_date_entry = None  # filter date entry
    f_show_all_opt = None
    f_upto_days_slider = None

    def __init__(self):
        super().__init__()
        self.setObjectName("record_table_area")
        layout_ = QVBoxLayout(self)

        header_ = QLabel("<h1>Attendance Records</h1>")
        header_.setObjectName("header_")
        layout_.addWidget(header_)

        filters_ = QWidget(self)
        filters_.setObjectName("filters_area")
        filters_layout = QHBoxLayout(filters_)
        filters_layout.setContentsMargins(0, 0, 0, 0)

        cls_n_sec_filter = QGroupBox(filters_)
        cls_n_sec_filter.setTitle("Select Class-Section")
        cls_n_sec_filter_layout = QHBoxLayout(cls_n_sec_filter)
        self.f_select_cls_n_sec = select_cls_n_sec = QComboBox(filters_)
        select_cls_n_sec.setObjectName("cls_n_sec_select")
        for cls_sec in os.listdir(AppConstant.CLASS_DIRECTORY):
            select_cls_n_sec.addItem(cls_sec)
        cls_n_sec_filter_layout.addWidget(select_cls_n_sec)
        filters_layout.addWidget(cls_n_sec_filter, stretch=1)

        date_filter = QGroupBox(filters_)
        date_filter.setObjectName("#date_select_frame")
        date_filter.setTitle("Select Date")
        date_filter_layout = QHBoxLayout(date_filter)
        self.f_date_entry = select_date = QDateEdit(date_filter)  # ADD DIFFERNET DROPDOWNS FOR (MONTH, DAYS, YEARS) INSTEAD OF ONE SINGLE ENTRY..
        select_date.setCalendarPopup(True)
        select_date.dateChanged.connect(self.on_date_change)
        select_date.setObjectName("date_select")
        date_filter_layout.addWidget(select_date, stretch=1)
        self.f_show_all_opt = show_all_opt = QCheckBox("Show all of ____")
        show_all_opt.setChecked(False)
        show_all_opt.stateChanged.connect(self.on_check_show_all)
        show_all_opt.setObjectName("show_all_opt")
        date_filter_layout.addWidget(show_all_opt)
        self.on_date_change(select_date.date())
        filters_layout.addWidget(date_filter, stretch=1)

        upto_days = QGroupBox(filters_)
        upto_days.setObjectName("upto_days")
        upto_days.setTitle("Show results upto _ days")
        upto_days_layout = QVBoxLayout(upto_days)
        self.f_upto_days_slider = upto_days_slider = QSlider(Qt.Horizontal)
        upto_days_slider.valueChanged.connect(lambda value: upto_days.setTitle(f"Show results upto {value} days"))
        upto_days_slider.setFixedWidth(200)
        upto_days_slider.setRange(1, 366)
        upto_days_slider.setPageStep(1)
        upto_days_layout.addWidget(upto_days_slider)
        filters_layout.addWidget(upto_days)

        btn_apply_filter = QPushButton("Apply Filter")
        btn_apply_filter.setObjectName("apply_filter_btn")
        btn_apply_filter.clicked.connect(self.on_apply_filter)
        btn_apply_filter.setFixedWidth(200)
        btn_apply_filter.setCursor(Qt.PointingHandCursor)
        filters_layout.addWidget(btn_apply_filter)

        layout_.addWidget(filters_)

        self.table_ = QTableWidget(self)
        self.table_.setObjectName("table_")
        self.table_.setShowGrid(False)
        self.table_.setRowCount(4)
        self.table_.setColumnCount(4)
        # self.load_data()

        # def setCellBeforeValue(row_, col_):
        #     cell_ = self.table_.item(row_, col_)
        #     if cell_:
        #         self.table_.old_value = self.table_.item(row_, col_).text()
        #     else:
        #         self.table_.old_value = ""

        # self.table_.cellDoubleClicked.connect(setCellBeforeValue)
        # self.table_.cellChanged.connect(self.onEdit)
        self.table_.verticalHeader().setVisible(False)
        self.table_.setSortingEnabled(True)
        table_header = self.table_.horizontalHeader()
        table_header.setStretchLastSection(True)
        table_header.setSortIndicatorShown(True)
        table_header.setSectionsClickable(True)
        table_header.setSortIndicator(0, Qt.AscendingOrder)
        table_header.setSectionResizeMode(QHeaderView.Stretch)
        layout_.addWidget(self.table_)

        layout_.addStretch(1)

    def on_date_change(self, date_: QDate):
        self.f_show_all_opt.setText(f"Show all of {date_.year()}")
        print(date_.year())

    def on_check_show_all(self, is_checked):
        if is_checked:
            self.f_date_entry.setStyleSheet("#date_select {color: gray}")
            self.f_date_entry.setEnabled(False)
        else:
            self.f_date_entry.setStyleSheet("#date_select {color: white}")
            self.f_date_entry.setEnabled(True)

    def on_apply_filter(self):
        print(self.f_select_cls_n_sec.currentText())
        print(self.f_date_entry.date())
        print(self.f_show_all_opt.checkState())
        print(self.f_upto_days_slider.value())
        self.load_data()

    def load_data(self):
        sheet_path_ = os.path.join(AppConstant.CLASS_DIRECTORY, self.f_select_cls_n_sec.currentText(), f"{self.f_date_entry.date().year()}.xlsx")
        if not os.path.exists(sheet_path_):
            return

        atd_sheet_db = ExcelFileWorker(sheet_path_)
        self.table_.clear()
        total_rows = atd_sheet_db.getNoOfRows()
        total_cols = atd_sheet_db.getNoOfColumns()

        self.table_.setRowCount(total_rows - 1)
        self.table_.setColumnCount(total_cols)

        self.table_.setHorizontalHeaderLabels(atd_sheet_db.getHeaderLabels())

        if total_rows - 1 <= 0:
            self.table_.setRowCount(1)
            no_item_text = QTableWidgetItem(str("No Records found."))
            no_item_text.setTextAlignment(Qt.AlignCenter)
            self.table_.setItem(0, 0, no_item_text)
            self.table_.setSpan(0, 0, 1, total_cols)
            return
        for x in range(total_rows - 1):
            row_ = atd_sheet_db.getRowByIndex(x + 1)

            for idx_, data_ in enumerate(row_):
                if idx_ == atd_sheet_db.primary_column_idx:
                    data_item = QTableWidgetItem()
                    data_item.setData(Qt.DisplayRole, int(data_))
                else:
                    data_item = QTableWidgetItem(str(data_))
                data_item.setTextAlignment(Qt.AlignCenter)
                self.table_.setItem(x, idx_, data_item)
        self.table_.resizeColumnsToContents()


class AttendancePage(QFrame):
    def __init__(self):
        super().__init__()
        with open("style_sheets/attendance_page.css", "r") as fp:
            self.setStyleSheet(fp.read())
        self.setObjectName("attendance_page_body")
        layout_ = QVBoxLayout(self)

        table_area = AttendanceRecordTable()
        layout_.addWidget(table_area)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app_ = QApplication([])

    win_ = QMainWindow()
    ele_ = AttendancePage()
    win_.setCentralWidget(ele_)
    win_.show()

    app_.exec()
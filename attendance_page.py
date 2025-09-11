import os

import openpyxl
from PyQt5.QtWidgets import *
from additional_widgets import *
from PyQt5.QtCore import Qt, QVersionNumber, QDate
from PyQt5.QtGui import QIntValidator, QIcon
from app_constants import AppConstant
from excel_functions import *
import datetime as real_datetime

class AttendanceRecordTable(QFrame):
    f_select_cls_n_sec = None  # filter class and section entry
    f_date_entries = None
    f_upto_days_slider = None
    atd_sheet_db = None
    is_data_loading = False

    def __init__(self):
        super().__init__()
        self.f_date_entries = []
        self.setObjectName("record_table_area")
        layout_ = QVBoxLayout(self)

        header_ = QLabel("<h1>Attendance Records</h1>")
        header_.setObjectName("header_")
        layout_.addWidget(header_)

        dfc = QWidget(self)
        dfc_layout = QVBoxLayout(dfc)
        filters_ = QFrame(self)
        filters_.setObjectName("filters_area")
        filters_layout = QHBoxLayout(filters_)
        filters_layout.setContentsMargins(0, 0, 0, 0)

        cls_n_sec_filter = QGroupBox(filters_)
        cls_n_sec_filter.setTitle("Select Class-Section")
        cls_n_sec_filter_layout = QHBoxLayout(cls_n_sec_filter)
        self.f_select_cls_n_sec = select_cls_n_sec = QComboBox(filters_)
        select_cls_n_sec.setObjectName("cls_n_sec_select")
        select_cls_n_sec.currentTextChanged.connect(self.on_cls_sec_change)
        cls_n_sec_filter_layout.addWidget(select_cls_n_sec)
        filters_layout.addWidget(cls_n_sec_filter, stretch=1)
        self.load_cls_sec_list()

        date_filter = QGroupBox(filters_)
        date_filter.setObjectName("#date_select_frame")
        date_filter.setTitle("Select Date (DD-MM-YYYY)")
        date_filter_layout = QHBoxLayout(date_filter)
        day_entry = QComboBox()
        day_entry.setFixedWidth(50)
        day_entry.addItem("All")
        for x in range(1, 32):
            day_entry.addItem(str(x))
        date_filter_layout.addWidget(day_entry)
        self.f_date_entries.append(day_entry)
        month_entry = QComboBox()
        month_entry.addItem("All")
        month_entry.setFixedWidth(50)
        for x in range(1, 13):
            month_entry.addItem(str(x))
        date_filter_layout.addWidget(month_entry)
        self.f_date_entries.append(month_entry)
        year_entry = QComboBox()
        year_entry.setFixedWidth(70)
        year_entry.addItem("null")
        date_filter_layout.addWidget(year_entry)
        self.f_date_entries.append(year_entry)
        filters_layout.addWidget(date_filter)
        self.on_cls_sec_change(select_cls_n_sec.currentText())

        # upto_days = QGroupBox(filters_)  # WILL BE ADDED IN FEATURE.
        # upto_days.setObjectName("upto_days")
        # upto_days.setTitle("Show results upto _ days")
        # upto_days_layout = QVBoxLayout(upto_days)
        # self.f_upto_days_slider = upto_days_slider = QSlider(Qt.Horizontal)
        # upto_days_slider.valueChanged.connect(lambda value: upto_days.setTitle(f"Show results upto {value} days"))
        # upto_days_slider.setRange(1, 366)
        # upto_days_slider.setPageStep(1)
        # upto_days_layout.addWidget(upto_days_slider)
        # filters_layout.addWidget(upto_days)

        btn_apply_filter = QPushButton("Apply Filter")
        btn_apply_filter.setObjectName("apply_filter_btn")
        btn_apply_filter.clicked.connect(self.on_apply_filter)
        btn_apply_filter.setFixedWidth(200)
        btn_apply_filter.setCursor(Qt.PointingHandCursor)
        filters_layout.addWidget(btn_apply_filter)

        dfc_layout.addWidget(filters_)
        dfc_layout.addStretch(1)
        layout_.addWidget(dfc)
        # layout_.addWidget(filters_,  stretch=0)

        self.lbl_no_result = QLabel("<h2>No attendance records are found!</h2>")
        self.lbl_no_result.setObjectName("lbl_no_result")
        self.lbl_no_result.setAlignment(Qt.AlignCenter)
        layout_.addWidget(self.lbl_no_result, stretch=1)

        self.table_ = QTableWidget(self)
        self.table_.setObjectName("table_")
        self.table_.setShowGrid(False)
        self.table_.setRowCount(4)
        self.table_.setColumnCount(4)
        self.table_.setVisible(False)

        def setCellBeforeValue(row_, col_):
            cell_ = self.table_.item(row_, col_)
            if cell_:
                self.table_.old_value = self.table_.item(row_, col_).text()
            else:
                self.table_.old_value = ""

        self.table_.cellDoubleClicked.connect(setCellBeforeValue)
        self.table_.cellChanged.connect(self.onEdit)
        self.table_.verticalHeader().setVisible(False)
        self.table_.setSortingEnabled(True)
        table_header = self.table_.horizontalHeader()
        table_header.setSortIndicatorShown(True)
        table_header.setSectionsClickable(True)
        table_header.setSortIndicator(0, Qt.AscendingOrder)
        table_header.setSectionResizeMode(QHeaderView.Interactive)
        table_header.setStretchLastSection(False)
        self.table_.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout_.addWidget(self.table_, stretch=1)

        # layout_.addStretch(1)


    def load_cls_sec_list(self):
        cls_sec_list = os.listdir(AppConstant.CLASS_DIRECTORY)
        if not cls_sec_list:
            self.f_select_cls_n_sec.addItem("No class found.")
        for cls_sec in cls_sec_list:
            self.f_select_cls_n_sec.addItem(cls_sec)

    def on_cls_sec_change(self, cls_sec):
        if not self.f_date_entries or cls_sec == "No class found.":
            return
        self.f_date_entries[-1].clear()
        sheet_name_list = os.listdir(os.path.join(AppConstant.CLASS_DIRECTORY, str(cls_sec)))
        if not sheet_name_list:
            self.f_date_entries[-1].addItem("null")
            return
        for item in sheet_name_list:
            self.f_date_entries[-1].addItem(item.replace(".xlsx", ""))

    def on_apply_filter(self):
        self.load_data()

    def load_data(self):
        sheet_path_ = os.path.join(AppConstant.CLASS_DIRECTORY, self.f_select_cls_n_sec.currentText(), f"{self.f_date_entries[-1].currentText()}.xlsx")
        if not os.path.exists(sheet_path_):
            return
        if not self.atd_sheet_db:
            self.atd_sheet_db = ExcelFileWorker(sheet_path_)

        self.is_data_loading = True
        self.atd_sheet_db = ExcelFileWorker(sheet_path_)
        self.table_.setSortingEnabled(False)
        self.table_.clear()
        total_rows = self.atd_sheet_db.getNoOfRows()

        valid_header_labels = ["Delete"]+self.atd_sheet_db.getHeaderLabels()[:2]
        for item in self.atd_sheet_db.getHeaderLabels()[2:]:
            date_obj = datetime.strptime(item, "%d-%m-%Y")

            day_ = str(self.f_date_entries[0].currentText())
            month_ = str(self.f_date_entries[1].currentText())

            if day_.isnumeric() and month_.isnumeric():
                if int(day_) == date_obj.day and int(month_) == date_obj.month:
                    valid_header_labels.append(item)
            elif (month_.isnumeric() and int(month_) == date_obj.month) or (day_.isnumeric() and int(day_) == date_obj.day):
                valid_header_labels.append(item)
            elif not day_.isnumeric() and not month_.isnumeric():
                valid_header_labels.append(item)

        if len(valid_header_labels) <= 3 or total_rows - 1 <= 0:
            self.table_.setVisible(False)
            self.lbl_no_result.setVisible(True)
            self.is_data_loading = False
            return

        self.table_.setVisible(True)
        self.lbl_no_result.setVisible(False)

        self.table_.setRowCount(total_rows - 1)
        self.table_.setColumnCount(len(valid_header_labels))

        self.table_.setHorizontalHeaderLabels(valid_header_labels)

        for x in range(total_rows - 1):
            delete_btn = QImageView("icons/delete_icon.svg")
            delete_btn.setAlignment(Qt.AlignCenter)
            delete_btn.on_click = lambda x_copy=x: self.onDelete(x_copy)
            self.table_.setCellWidget(x, 0, delete_btn)

            row_ = self.atd_sheet_db.selectRowByFilter(valid_header_labels, x+1)
            for idx_, data_ in enumerate(row_):
                pos_ = data_[1]  # location of column in excel sheet - tuple (row, column)
                data_ = data_[0]
                if idx_ == self.atd_sheet_db.primary_column_idx:
                    data_item = QTableWidgetItem()
                    data_item.setData(Qt.DisplayRole, int(data_))
                else:
                    data_item = QTableWidgetItem(str(data_))
                data_item.setTextAlignment(Qt.AlignCenter)
                data_item.location_ = pos_  # setting position as instace variable so that even after table filter the position stays absolute as mapped with excel sheet
                self.table_.setItem(x, idx_+1, data_item)

        self.is_data_loading = False
        self.table_.resizeColumnsToContents()
        self.table_.setSortingEnabled(True)

    def onEdit(self, row_, col_):
        if self.is_data_loading:
            return
        try:
            update_location = self.table_.item(row_, col_).location_
            new_value = self.table_.item(row_, col_).text()
            if col_ == self.atd_sheet_db.primary_column_idx:
                if not new_value.isnumeric():
                    MessageBox().show_message("Error", "Can't update value - Required type int.", "error")
                    self.table_.item(row_, col_).setText(self.table_.old_value)
                    self.table_.cellChanged.connect(self.onEdit)
                    return
                self.atd_sheet_db.updateByLocation(update_location[0]+1, update_location[1]+1, int(new_value))
            else:
                self.atd_sheet_db.updateByLocation(update_location[0]+1, update_location[1]+1, new_value)
        except BaseException as e:
            MessageBox().show_message("Error", f"Can't update value.\nError : {e}", "error")

    def onDelete(self, row_):
        conf_ = MessageBox.ask_question("Do you really want to permanently delete whole attendance record of selected student?")
        if conf_:
            self.atd_sheet_db.deleteRowByIndex(row_ + 1)
            self.atd_sheet_db.save()
            self.load_data()

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
import os

import openpyxl
from PyQt5.QtWidgets import *
from additional_widgets import *
from PyQt5.QtCore import Qt, QVersionNumber, QDate
from PyQt5.QtGui import QIntValidator, QIcon
import datetime as real_datetime
from database_manager import MsAccessDriver
import pandas as pd

class AttendanceRecordTable(QFrame):
    f_date_entries = None
    f_upto_days_slider = None
    is_data_loading = False
    db_instance = None

    def __init__(self, db_instance:MsAccessDriver):
        super().__init__()
        self.db_instance = db_instance
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

        adm_no_filter = QGroupBox(filters_)
        adm_no_filter.setTitle("Select Admission No.")
        adm_no_filter_layout = QHBoxLayout(adm_no_filter)
        self.f_select_adm_no = QComboBox(filters_)
        self.f_select_adm_no.setEditable(True)
        self.f_select_adm_no.setObjectName("cls_n_sec_select")
        adm_no_filter_layout.addWidget(self.f_select_adm_no)
        filters_layout.addWidget(adm_no_filter, stretch=1)


        cls_filter = QGroupBox(filters_)
        cls_filter.setTitle("Select Class")
        cls_filter_layout = QHBoxLayout(cls_filter)
        self.f_select_cls = QComboBox(filters_)
        self.f_select_cls.setObjectName("cls_n_sec_select")
        cls_filter_layout.addWidget(self.f_select_cls)
        filters_layout.addWidget(cls_filter, stretch=1)

        sec_filter = QGroupBox(filters_)
        sec_filter.setTitle("Select Section")
        sec_filter_layout = QHBoxLayout(sec_filter)
        self.f_select_sec = QComboBox(filters_)
        self.f_select_sec.setObjectName("cls_n_sec_select")
        sec_filter_layout.addWidget(self.f_select_sec)
        filters_layout.addWidget(sec_filter, stretch=1)
        self.auto_filler()

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
        year_entry.addItem("All")
        cur_year = real_datetime.datetime.now().year
        for yr in range(cur_year-25, cur_year+25):
            year_entry.addItem(str(yr))
        date_filter_layout.addWidget(year_entry)
        self.f_date_entries.append(year_entry)
        filters_layout.addWidget(date_filter)

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
        self.load_all_data()  # LOADING TABLE DATA
        table_header = self.table_.horizontalHeader()
        table_header.setSortIndicatorShown(True)
        table_header.setSectionsClickable(True)
        table_header.setSortIndicator(0, Qt.AscendingOrder)
        table_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        table_header.setStretchLastSection(False)
        self.table_.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout_.addWidget(self.table_, stretch=1)
        # layout_.addStretch(1)

    def auto_filler(self):
        self.db_instance.cursor.execute("SELECT admission_no FROM students")
        db_resp = self.db_instance.cursor.fetchall()
        if not db_resp:
            self.f_select_adm_no.addItem("null")
        else:
            self.f_select_adm_no.addItem("All")
            for item in db_resp:
                self.f_select_adm_no.addItem(str(item[0]))

        self.db_instance.cursor.execute("SELECT DISTINCT class FROM students")
        db_resp = self.db_instance.cursor.fetchall()
        if not db_resp:
            self.f_select_cls.addItem("null")
        else:
            self.f_select_cls.addItem("All")
            for item in db_resp:
                self.f_select_cls.addItem(str(item[0]))

        self.db_instance.cursor.execute("SELECT DISTINCT section FROM students")
        db_resp = self.db_instance.cursor.fetchall()
        if not db_resp:
            self.f_select_sec.addItem("null")
        else:
            self.f_select_sec.addItem("All")
            for item in db_resp:
                self.f_select_sec.addItem(str(item[0]))

    def on_apply_filter(self):
        self.load_all_data()

    def load_all_data(self):
        try:
            dates_ = [item.currentText() for item in self.f_date_entries]  # dd - mm - yyyy
            query_ = "SELECT students.admission_no, student_name, class, section, mark_date, status FROM students INNER JOIN attendance ON students.admission_no = attendance.admission_no"
            query_values = []
            claus_to_add = "WHERE"
            if self.f_select_adm_no.currentText() != "All":
                query_ += f" {claus_to_add} students.admission_no=?"
                query_values.append(self.f_select_adm_no.currentText())
                claus_to_add = "AND"
            if self.f_select_cls.currentText() != "All":
                query_ += f" {claus_to_add} class=?"
                query_values.append(self.f_select_cls.currentText())
                claus_to_add = "AND"
            if self.f_select_sec.currentText() != "All":
                query_ += f" {claus_to_add} section=?"
                query_values.append(self.f_select_sec.currentText())
                claus_to_add = "AND"
            if dates_[0] != "All":
                query_ += f" {claus_to_add} DAY(mark_date)=?"
                query_values.append(dates_[0])
                claus_to_add = "AND"
            if dates_[1] != "All":
                query_ += f" {claus_to_add} MONTH(mark_date)=?"
                query_values.append(dates_[1])
                claus_to_add = "AND"
            if dates_[2] != "All":
                query_ += f" {claus_to_add} YEAR(mark_date)=?"
                query_values.append(dates_[2])
            query_ += "  ORDER BY mark_date ASC"
            self.db_instance.cursor.execute(query_, query_values)
            db_resp = self.db_instance.cursor.fetchall()
            df1 = pd.DataFrame([], columns=["admission_no", "student_name", "class", "section"])
            for item in db_resp:
                if item[0] not in df1["admission_no"].values:
                    new_row = len(df1)
                    df1.loc[new_row, ["admission_no", "student_name", "class", "section"]] = list(item[:4])
                    df1.loc[new_row, item[4].strftime("%d-%m-%Y")] = item[5]
                else:
                    df1.loc[df1["admission_no"] == item[0], item[4].strftime("%d-%m-%Y")] = item[5]

            if df1.empty:
                self.table_.setVisible(False)
                self.lbl_no_result.setVisible(True)
                return
            self.is_data_loading = True
            self.table_.setSortingEnabled(False)
            self.table_.clear()
            self.table_.setRowCount(0)
            self.table_.setColumnCount(len(df1.columns)+1)
            self.table_.setHorizontalHeaderLabels(["Delete"]+list(df1.columns))
            self.lbl_no_result.setVisible(False)
            self.table_.setVisible(True)

            for row_idx in range(len(df1)):
                self.table_.insertRow(row_idx)
                for col_idx in range(len(df1.columns)):
                    data_ = df1.iloc[row_idx, col_idx]

                    if col_idx == 0:
                        empty_item = QTableWidgetItem()
                        empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsSelectable)
                        self.table_.setItem(row_idx, 0, empty_item)
                        delete_btn = QImageView("icons/delete_icon.svg")
                        delete_btn.setAlignment(Qt.AlignCenter)
                        delete_btn.on_click = lambda adm_no_copy=int(data_): self.onDelete(adm_no_copy)
                        self.table_.setCellWidget(row_idx, 0, delete_btn)

                        data_item = QTableWidgetItem()
                        data_item.setData(Qt.DisplayRole, int(data_))
                    else:
                        data_item = QTableWidgetItem(str(data_))
                    if col_idx < 4:  # disabling editing of admission no and student name columns.
                        data_item.setFlags(data_item.flags() & ~Qt.ItemIsEditable)
                    data_item.setTextAlignment(Qt.AlignCenter)
                    self.table_.setItem(row_idx, col_idx + 1, data_item)
            self.is_data_loading = False
            self.table_.resizeColumnsToContents()
            self.table_.setSortingEnabled(True)
        except BaseException as e:
            print("error : ", e)

    def onEdit(self, row_, col_):
        if self.is_data_loading:
            return
        try:
            adm_no = self.table_.item(row_, 1).text()
            date_ = self.table_.horizontalHeaderItem(col_).text()
            new_value = self.table_.item(row_, col_).text()
            if new_value not in ["P", "A", "N/A"]:
                self.table_.item(row_, col_).setText(self.table_.old_value)
                MessageBox().show_message("Warning", "Can't update! Value should be 'P', 'A' or 'N/A'", "warn")
                return
            self.db_instance.cursor.execute(f"UPDATE attendance SET status=? WHERE mark_date=? AND admission_no=?", new_value, real_datetime.datetime.strptime(date_, "%d-%m-%Y"), adm_no)
            if not self.db_instance.cursor.rowcount:
                self.table_.item(row_, col_).setText(self.table_.old_value)
                MessageBox().show_message("Error", "Failed! No rows affected, May the entry of attendance of the selected student at selected date not exists.", "error")
                return
        except BaseException as e:
            self.table_.item(row_, col_).setText(self.table_.old_value)
            MessageBox().show_message("Error", f"Can't update value.\nError : {e}", "error")

    def onDelete(self, adm_no):
        try:
            selected_cols = self.table_.selectedItems()
            if not selected_cols:
                MessageBox().show_message("Warning", "Please select the date columns for which you want to delete attendance.\nWARNING : NO DATE COLUMN SELECTED!", "warn")
                return
            try:
                dates_to_del = [real_datetime.datetime.strptime(self.table_.horizontalHeaderItem(col_.column()).text(), "%d-%m-%Y") for col_ in selected_cols]
                # dates_to_del = list(set(dates_to_del))
            except BaseException as e:
                MessageBox().show_message("Error", f"All selected columns must be of date type.\nError : {e}", "error")
                return

            conf_ = MessageBox.ask_question(f"Do you really want to permanently delete selected attendance record(s) of student with admission no. {adm_no}?")
            if not conf_:
                return
            res_ = []
            for item in dates_to_del:
                self.db_instance.cursor.execute("DELETE FROM attendance WHERE mark_date=? AND admission_no=?", item, adm_no)
                res_.append(self.db_instance.cursor.rowcount)
            self.db_instance.cursor.commit()
            self.load_all_data()
            MessageBox().show_message("Success", f"Successfully deleted {len(res_) - res_.count(0)} entries.\nFailed : {res_.count(0)}", "info")
        except BaseException as e:
            MessageBox().show_message("Error", f"Unexpected error.\nError : {e}", "error")

class AttendanceRecordsPage(QFrame):
    def __init__(self, db_instance:MsAccessDriver):
        super().__init__()
        with open("style_sheets/attendance_records_page.css", "r") as fp:
            self.setStyleSheet(fp.read())
        self.setObjectName("attendance_page_body")
        layout_ = QVBoxLayout(self)

        table_area = AttendanceRecordTable(db_instance=db_instance)
        layout_.addWidget(table_area)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app_ = QApplication([])

    win_ = QMainWindow()
    ele_ = AttendanceRecordsPage()
    win_.setCentralWidget(ele_)
    win_.show()

    app_.exec()
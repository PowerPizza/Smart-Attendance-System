from PyQt5.QtWidgets import *
from additional_widgets import *
from PyQt5.QtCore import Qt, QVersionNumber, QDate
from PyQt5.QtGui import QIntValidator, QIcon
from app_constants import AppConstant
import datetime as real_datetime
from database_manager import MsAccessDriver

class Header(QFrame):
    f_date_entries = None
    db_instance = None

    def __init__(self, db_instance:MsAccessDriver, parent=None):
        super().__init__(parent)
        self.f_date_entries = []
        self.db_instance = db_instance
        self.setObjectName("header_")
        layout_ = QHBoxLayout(self)

        cls_area = QGroupBox()
        cls_area.setTitle("Select Class")
        cls_filter_layout = QHBoxLayout(cls_area)
        self.f_select_cls = QComboBox()
        self.f_select_cls.setObjectName("cls_n_sec_select")
        cls_filter_layout.addWidget(self.f_select_cls)
        layout_.addWidget(cls_area, stretch=1)

        sec_area = QGroupBox()
        sec_area.setTitle("Select Section")
        sec_filter_layout = QHBoxLayout(sec_area)
        self.f_select_sec = QComboBox()
        self.f_select_sec.setObjectName("cls_n_sec_select")
        sec_filter_layout.addWidget(self.f_select_sec)
        layout_.addWidget(sec_area, stretch=1)
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

        self.open_sheet_btn = QPushButton("Load students")
        self.open_sheet_btn.setObjectName("load_sheet_btn")
        self.open_sheet_btn.setCursor(Qt.PointingHandCursor)
        layout_.addWidget(self.open_sheet_btn, alignment=Qt.AlignVCenter)

    def load_cls_sec_list(self):
        self.db_instance.cursor.execute("SELECT DISTINCT class FROM students")
        db_resp = self.db_instance.cursor.fetchall()
        if not db_resp:
            self.f_select_cls.addItem("No class found")
        for item in db_resp:
            self.f_select_cls.addItem(str(item[0]))

        self.db_instance.cursor.execute("SELECT DISTINCT section FROM students")
        db_resp = self.db_instance.cursor.fetchall()
        if not db_resp:
            self.f_select_cls.addItem("No section found")
        for item in db_resp:
            self.f_select_sec.addItem(str(item[0]))

    def set_on_open_sheet(self, callable_):
        def launch_():
            date_ = real_datetime.date(*[int(inp.currentText()) for inp in self.f_date_entries][::-1])
            callable_(self.f_select_cls.currentText(), self.f_select_sec.currentText(), date_)
        self.open_sheet_btn.clicked.connect(launch_)

class MarkAttendanceArea(QFrame):
    new_attendance = None

    def __init__(self):
        super().__init__()
        self.new_attendance = {}
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

    def load_sheet(self, students_list, date_:real_datetime.date):
        self.lbl_no_sheet.setVisible(False)
        self.table_.setSortingEnabled(False)
        self.table_.clear()
        self.table_.setRowCount(0)
        self.table_.setColumnCount(3)
        self.table_.setVisible(True)
        self.table_.setHorizontalHeaderLabels(["admission_no", "student_name"]+[str(date_.strftime("%d-%m-%Y"))])
        i = 0
        try:
            for adm_no, std_name in students_list:
                self.new_attendance[adm_no] = 'N/A'
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
                present_opt.toggled.connect(lambda _, adm_no_cpy=adm_no: self.mark_new_attendance("P", adm_no_cpy))
                marking_col_layout.addWidget(present_opt, stretch=1)
                absent_opt = QRadioButton("Absent")
                absent_opt.setObjectName("absent_opt")
                absent_opt.toggled.connect(lambda _, adm_no_cpy=adm_no: self.mark_new_attendance("A", adm_no_cpy))
                marking_col_layout.addWidget(absent_opt, stretch=1)
                na_opt = QRadioButton("N/A")
                na_opt.setObjectName("na_opt")
                na_opt.setChecked(True)
                na_opt.toggled.connect(lambda _, adm_no_cpy=adm_no: self.mark_new_attendance("N/A", adm_no_cpy))
                marking_col_layout.addWidget(na_opt, stretch=1)
                self.table_.setCellWidget(i, 2, marking_col)
                i += 1
            self.table_.setSortingEnabled(True)
        except BaseException as e:
            print(e)

    def mark_new_attendance(self, status, adm_no):
        self.new_attendance[adm_no] = status

    def get_new_attendance(self):
        return self.new_attendance

class MarkAttendancePage(QFrame):
    selected_cls = None
    selected_sec = None
    selected_date = None
    db_instance = None

    def __init__(self, db_instance:MsAccessDriver):
        super().__init__()
        self.db_instance = db_instance
        with open("style_sheets/mark_attendance_page.css") as fp:
            self.setStyleSheet(fp.read())
        self.setObjectName("mark_attendance_body")
        layout_ = QVBoxLayout(self)

        self.header_ = Header(db_instance=db_instance)
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

        btn_save = QPushButton("Save Attendance")
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


    def on_open_sheet(self, cls, sec, date_:real_datetime.date):
        try:
            self.db_instance.cursor.execute("SELECT COUNT(admission_no) FROM attendance WHERE mark_date=?", date_)
            db_resp = self.db_instance.cursor.fetchone()[0]
            if db_resp:
                conf_ = MessageBox.ask_question(f"It looks like attendance of '{db_resp}' students is already marked at selected date '{date_.strftime("%d-%m-%Y")}'.\nWould you like to retake attendance of this date?")
                if not conf_:
                    return

            self.db_instance.cursor.execute("SELECT admission_no, student_name FROM students WHERE class=? AND section=?", cls, sec)
            db_resp = self.db_instance.cursor.fetchall()
            if not db_resp:
                MessageBox().show_message("Error", "Currently no student belongs to the selected class & section.\nError : Failed to load attendance sheet.", "error")
                return
            self.selected_cls = cls
            self.selected_sec = sec
            self.selected_date = date_
            self.marking_area.load_sheet(db_resp, date_)
        except BaseException as e:
            print(e)

    def on_save_attendance(self):
        try:
            to_mark = self.marking_area.get_new_attendance()
            for adm_no in to_mark:
                self.db_instance.cursor.execute("SELECT id FROM attendance WHERE admission_no=? AND mark_date=?", adm_no, self.selected_date)
                db_resp = self.db_instance.cursor.fetchone()
                if db_resp is not None:
                    self.db_instance.cursor.execute("UPDATE attendance SET status=? WHERE admission_no=? AND mark_date=?", to_mark[adm_no], adm_no, self.selected_date)
                else:
                    self.db_instance.cursor.execute("SELECT MAX(id) FROM attendance")
                    new_id = self.db_instance.cursor.fetchone()[0]
                    new_id = 0 if new_id is None else new_id
                    self.db_instance.cursor.execute("INSERT INTO attendance VALUES (?, ?, ?, ?)", new_id+1, adm_no, self.selected_date, to_mark[adm_no])
            self.db_instance.cursor.commit()
            MessageBox().show_message("Success", f"Attendance of '{self.selected_date.strftime('%d-%m-%Y')}' has been saved!", "info")
        except BaseException as e:
            MessageBox().show_message("Error", f"Unable to save attendance.\nError : {e}", "error")


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app_ = QApplication([])

    win_ = QMainWindow()
    ele_ = MarkAttendancePage()
    win_.setCentralWidget(ele_)
    win_.show()

    app_.exec()
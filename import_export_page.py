import os
from PyQt5.QtWidgets import *
from additional_widgets import *
from PyQt5.QtCore import Qt, QThread, QSize
from PyQt5.QtGui import QIntValidator, QIcon

from app_constants import AppConstant
from database_manager import MsAccessDriver, EncodeType
import pandas as pd
import datetime as real_datetime

class ImportStudentDataArea(QFrame):
    lbl_file_name = None
    file_df = None
    mapping_fields = None
    over_write = None
    skip_duplicates = None
    db_instance = None

    def __init__(self, db_instance: MsAccessDriver):
        super().__init__()
        self.db_instance = db_instance
        self.mapping_fields = []

        layout_ = QVBoxLayout(self)
        self.setObjectName("import_student_area")

        heading_ = QLabel("<h1>Import Student Data</h1>")
        heading_.setObjectName("heading_")
        layout_.addWidget(heading_)

        btn_select_file = QPushButton("Select File")
        btn_select_file.setFixedWidth(300)
        btn_select_file.setObjectName("ui_btn")
        btn_select_file.clicked.connect(self.on_select_file)
        layout_.addWidget(btn_select_file, alignment=Qt.AlignHCenter)

        self.bi_area = bi_area = QWidget()
        bi_area_layout = QHBoxLayout(bi_area)
        bi_area_layout.setContentsMargins(0, 0, 0, 0)
        bi_area.setVisible(False)

        mapping_area = QFrame()
        mapping_area.setObjectName("mapping_area")
        mapping_area_layout = QGridLayout(mapping_area)

        lbl_info = QLabel("*Please map the database column with your selected file's column.")
        lbl_info.setObjectName("mild_info_lbl")
        mapping_area_layout.addWidget(lbl_info, 0, 0, 1, 2)

        lbl_db_cols = QLabel("<b>Database Columns</b>")
        lbl_db_cols.setObjectName("normal_lbl")
        mapping_area_layout.addWidget(lbl_db_cols, 1, 0, 1, 1, Qt.AlignCenter)

        lbl_db_cols = QLabel("<b>File Columns</b>")
        lbl_db_cols.setObjectName("normal_lbl")
        mapping_area_layout.addWidget(lbl_db_cols, 1, 1, 1, 1, Qt.AlignCenter)

        field1 = QLabel("Admission no.")
        field1.setObjectName("normal_lbl")
        mapping_area_layout.addWidget(field1, 2, 0)
        select1 = QComboBox()
        select1.setObjectName("select_box")
        mapping_area_layout.addWidget(select1, 2, 1)

        field2 = QLabel("Student Name")
        field2.setObjectName("normal_lbl")
        mapping_area_layout.addWidget(field2, 3, 0)
        select2 = QComboBox()
        select2.setObjectName("select_box")
        mapping_area_layout.addWidget(select2, 3, 1)

        field3 = QLabel("Father Name")
        field3.setObjectName("normal_lbl")
        mapping_area_layout.addWidget(field3, 4, 0)
        select3 = QComboBox()
        select3.setObjectName("select_box")
        mapping_area_layout.addWidget(select3, 4, 1)

        field4 = QLabel("Mobile No.")
        field4.setObjectName("normal_lbl")
        mapping_area_layout.addWidget(field4, 5, 0)
        select4 = QComboBox()
        select4.setObjectName("select_box")
        mapping_area_layout.addWidget(select4, 5, 1)

        field5 = QLabel("Class")
        field5.setObjectName("normal_lbl")
        mapping_area_layout.addWidget(field5, 6, 0)
        select5 = QComboBox()
        select5.setObjectName("select_box")
        mapping_area_layout.addWidget(select5, 6, 1)

        field6 = QLabel("Section")
        field6.setObjectName("normal_lbl")
        mapping_area_layout.addWidget(field6, 7, 0)
        select6 = QComboBox()
        select6.setObjectName("select_box")
        mapping_area_layout.addWidget(select6, 7, 1)

        self.mapping_fields.extend([select1, select2, select3, select4, select5, select6])

        bi_area_layout.addWidget(mapping_area)

        proceed_area = QFrame()
        proceed_area.setObjectName("proceed_area")
        proceed_area_layout = QGridLayout(proceed_area)

        self.lbl_file_name = QLabel("Selected File : ")
        self.lbl_file_name.setObjectName("normal_lbl")
        proceed_area_layout.addWidget(self.lbl_file_name, 0, 0)

        self.auto_adm_no = QCheckBox("Auto-Admission Number")
        self.auto_adm_no.setChecked(True)
        select1.setEnabled(False)
        self.auto_adm_no.clicked.connect(lambda v: select1.setEnabled(not v))
        proceed_area_layout.addWidget(self.auto_adm_no, 1, 0)

        self.over_write = QRadioButton("Overwrite Duplicates", self)
        proceed_area_layout.addWidget(self.over_write, 2, 0)

        self.skip_duplicates = QRadioButton("Skip Duplicates", self)
        self.skip_duplicates.setChecked(True)
        proceed_area_layout.addWidget(self.skip_duplicates, 2, 1)
        proceed_area_layout.setRowStretch(3, 1)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("ui_btn")
        btn_cancel.setProperty("ui", "red")
        btn_cancel.clicked.connect(self.on_click_cancel)
        proceed_area_layout.addWidget(btn_cancel, 4, 0)

        btn_import = QPushButton("Import")
        btn_import.setObjectName("ui_btn")
        btn_import.clicked.connect(self.on_click_import)
        proceed_area_layout.addWidget(btn_import, 4, 1)

        bi_area_layout.addWidget(proceed_area)

        layout_.addWidget(bi_area)

    def on_select_file(self):
        file_, ext_ = QFileDialog.getOpenFileName(self, "Import student data", "", "*.csv;;*.xlsx")
        print(file_)
        if ext_ in ["*.xlsx", "*.csv"]:
            try:
                self.bi_area.setVisible(True)
                self.lbl_file_name.setText(f"<b>Selected File : {os.path.basename(file_)}</b>")
                if ext_ == "*.xlsx":
                    self.file_df = pd.read_excel(file_, dtype=str)

                elif ext_ == "*.csv":
                    self.file_df = pd.read_csv(file_, dtype=str)

                for item in self.mapping_fields:
                    item.clear()
                    for col_ in self.file_df.columns:
                        item.addItem(str(col_))
            except BaseException as e:
                MessageBox().show_message("Error", f"Failed to load selected file `{file_}`.\nError : {e}", "error")
                self.bi_area.setVisible(False)
        else:
            MessageBox().show_message("Error", "Unknown file selected, only excel (*.xlsx) and CSV (*.csv) files are allowd.", "error")

    def on_click_import(self):
        try:
            col_indexes = [item.currentIndex() for item in self.mapping_fields]
            if self.auto_adm_no.isChecked():
                added_count = 0
                failed_count = 0
                col_indexes = col_indexes[1:]
                df_to_save = self.file_df.iloc[:, col_indexes]
                for row_ in range(len(df_to_save.index)):
                    try:
                        self.db_instance.cursor.execute("SELECT MAX(admission_no) FROM students")
                        new_add_no = self.db_instance.cursor.fetchone()[0]
                        new_add_no = (0 if new_add_no is None else new_add_no) + 1

                        data_row = [new_add_no]+df_to_save.iloc[row_].tolist()+[""]

                        self.db_instance.cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)", *data_row)
                        added_count += 1
                    except BaseException as e:
                        print(e)
                        failed_count += 1
                self.db_instance.cursor.commit()
                MessageBox().show_message("Info", f"Successfully added {added_count} rows.\nFailed to add {failed_count} rows", "info")
            else:
                overwritten_count = 0
                insertion_count = 0
                skipped_count = 0
                failed_count = 0
                df_to_save = self.file_df.iloc[:, col_indexes]
                for row_ in range(len(df_to_save.index)):
                    try:
                        data_row = df_to_save.iloc[row_].tolist() + [""]

                        self.db_instance.cursor.execute("SELECT admission_no FROM students WHERE admission_no=?", data_row[0])
                        db_resp = self.db_instance.cursor.fetchone()
                        if not db_resp:
                            self.db_instance.cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)", *data_row)
                            insertion_count += 1
                        else:
                            if self.over_write.isChecked():
                                self.db_instance.cursor.execute("UPDATE students SET student_name=?, father_name=?, mobile_no=?, class=?, section=?, face_encoding_file=? WHERE admission_no=?", *data_row[1:], data_row[0])
                                overwritten_count += 1
                            else:
                                skipped_count += 1
                    except BaseException as e:
                        print(e)
                        failed_count += 1
                self.db_instance.cursor.commit()
                MessageBox().show_message("Info", f"Successfully inserted {insertion_count} rows and overwritten {overwritten_count} rows.\nskipped {skipped_count} rows.\nFailed to add {failed_count} rows.", "info")
            self.bi_area.setVisible(False)
            self.file_df = None
        except BaseException as err:
            MessageBox().show_message("Error", f"Error while importing data.\nError : {err}", "error")

    def on_click_cancel(self):
        self.file_df = None
        self.bi_area.setVisible(False)

class ExportAttendanceArea(QFrame):
    f_date_entries = None
    db_instance = None

    def __init__(self, db_instance:MsAccessDriver):
        super().__init__()
        self.db_instance = db_instance
        self.f_date_entries = []

        layout_ = QVBoxLayout(self)
        self.setObjectName("export_attendance_area")

        heading_ = QLabel("<h1>Export Attendance</h1>")
        heading_.setObjectName("heading_")
        layout_.addWidget(heading_)

        filter_area = QWidget()
        filter_area_layout = QHBoxLayout(filter_area)
        filter_area_layout.setContentsMargins(0, 0, 0, 0)

        date_filter = QGroupBox(self)
        date_filter.setObjectName("date_select_frame")
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
        for yr in range(cur_year - 25, cur_year + 25):
            year_entry.addItem(str(yr))
        date_filter_layout.addWidget(year_entry)
        self.f_date_entries.append(year_entry)
        filter_area_layout.addWidget(date_filter, alignment=Qt.AlignLeft)

        cls_sec_group = QGroupBox(self)
        cls_sec_group.setTitle("Select class & section")
        cls_sec_group_layout = QHBoxLayout(cls_sec_group)
        self.cls_sec_select = QComboBox()
        cls_sec_group_layout.addWidget(self.cls_sec_select)
        filter_area_layout.addWidget(cls_sec_group, stretch=1)
        self.load_cls_sec()

        export_type_group = QGroupBox(self)
        export_type_group.setTitle("Select export file type")
        export_type_group_layout = QHBoxLayout(export_type_group)
        self.export_type_select = export_type_select = QComboBox()
        export_type_select.addItem("Excel")
        export_type_select.addItem("CSV")
        export_type_group_layout.addWidget(export_type_select)
        filter_area_layout.addWidget(export_type_group, stretch=1)

        btn_export = QPushButton("Export")
        btn_export.setObjectName("ui_btn")
        btn_export.clicked.connect(self.on_export)
        filter_area_layout.addWidget(btn_export, stretch=1)

        layout_.addWidget(filter_area)

    def load_cls_sec(self):
        try:
            self.cls_sec_select.addItem("All")
            self.db_instance.cursor.execute("SELECT class, section FROM attendance INNER JOIN students ON attendance.admission_no = students.admission_no GROUP BY class, section")
            for item in self.db_instance.cursor.fetchall():
                self.cls_sec_select.addItem("-".join(item))
        except BaseException as e:
            print(e)

    def on_export(self):
        try:
            dates_ = [item.currentText() for item in self.f_date_entries]  # dd - mm - yyyy
            query_ = "SELECT students.admission_no, student_name, class, section, mark_date, status FROM students INNER JOIN attendance ON students.admission_no = attendance.admission_no"
            query_values = []
            claus_to_add = "WHERE"
            if self.cls_sec_select.currentText() != "All":
                query_ += f" {claus_to_add} class & ? & section=?"
                query_values.append("-")
                query_values.append(self.cls_sec_select.currentText())
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

            self.db_instance.cursor.execute(query_, *query_values)
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
                MessageBox().show_message("Error", "No attendance records were found with selected filters.", "error")
                return
            file_ = ""
            if self.export_type_select.currentText() == "Excel":
                file_, _ = QFileDialog.getSaveFileName(self, "Save As Excel File", "", "Excel Files (*.xlsx)")
                if not file_: return
                df1.to_excel(file_, index=False)
            elif self.export_type_select.currentText() == "CSV":
                file_, _ = QFileDialog.getSaveFileName(self, "Save As Excel File", "", "CSV Files (*.csv)")
                if not file_: return
                df1.to_csv(file_, index=False)
            MessageBox().show_message("Success", f"Successfully exported data at `{file_}`", "info")
        except BaseException as e:
            MessageBox().show_message("Error", f"Failed to export file.\nError : {e}", "error")


class ExportStudentData(QFrame):
    f_date_entries = None
    db_instance = None

    def __init__(self, db_instance:MsAccessDriver):
        super().__init__()
        self.db_instance = db_instance
        self.f_date_entries = []

        layout_ = QVBoxLayout(self)
        self.setObjectName("export_students_data")

        heading_ = QLabel("<h1>Export Students</h1>")
        heading_.setObjectName("heading_")
        layout_.addWidget(heading_)

        horizonal_holder = QWidget()
        horizonal_holder_layout = QHBoxLayout(horizonal_holder)
        horizonal_holder_layout.setContentsMargins(0, 0, 0, 0)

        cls_sec_group = QGroupBox(self)
        cls_sec_group.setTitle("Select class & section")
        cls_sec_group_layout = QHBoxLayout(cls_sec_group)
        self.cls_sec_select = QComboBox()
        cls_sec_group_layout.addWidget(self.cls_sec_select)
        horizonal_holder_layout.addWidget(cls_sec_group, stretch=1)
        self.load_cls_sec()

        export_type_group = QGroupBox(self)
        export_type_group.setTitle("Select export file type")
        export_type_group_layout = QHBoxLayout(export_type_group)
        self.export_type_select = export_type_select = QComboBox()
        export_type_select.addItem("Excel")
        export_type_select.addItem("CSV")
        export_type_group_layout.addWidget(export_type_select)
        horizonal_holder_layout.addWidget(export_type_group, stretch=1)

        btn_export = QPushButton("Export")
        btn_export.setObjectName("ui_btn")
        btn_export.clicked.connect(self.on_export)
        horizonal_holder_layout.addWidget(btn_export)

        layout_.addWidget(horizonal_holder)

    def load_cls_sec(self):
        try:
            self.cls_sec_select.addItem("All")
            self.db_instance.cursor.execute("SELECT class, section FROM students GROUP BY class, section")
            for item in self.db_instance.cursor.fetchall():
                self.cls_sec_select.addItem("-".join(item))
        except BaseException as e:
            print(e)

    def on_export(self):
        try:
            if self.cls_sec_select.currentText() != "All":
                self.db_instance.cursor.execute("SELECT * FROM students WHERE class & ? & section=?", "-", self.cls_sec_select.currentText())
            else:
                self.db_instance.cursor.execute("SELECT * FROM students")

            cols = [item[0] for item in self.db_instance.cursor.description]
            db_resp = self.db_instance.cursor.fetchall()
            conf_ = MessageBox.ask_question(f"{len(db_resp)} rows found would you like to save ?")
            if not conf_: return

            df1 = pd.DataFrame(columns=cols)
            for item in db_resp:
                df1.loc[len(df1.index)+1] = list(item)

            file_ = ""
            if self.export_type_select.currentText() == "Excel":
                file_, _ = QFileDialog.getSaveFileName(self, "Save As Excel File", "", "Excel Files (*.xlsx)")
                if not file_: return
                df1.to_excel(file_, index=False)
            elif self.export_type_select.currentText() == "CSV":
                file_, _ = QFileDialog.getSaveFileName(self, "Save As Excel File", "", "CSV Files (*.csv)")
                if not file_: return
                df1.to_csv(file_, index=False)
            MessageBox().show_message("Success", f"Successfully exported data at `{file_}`", "info")
        except BaseException as e:
            MessageBox().show_message("Error", f"Failed to export file.\nError : {e}", "error")

class InjectDatabase(QFrame):
    db_instance = None
    def __init__(self, db_instance: MsAccessDriver):
        super().__init__()
        self.db_instance = db_instance
        self.setObjectName("inject_db")

        layout_ = QVBoxLayout(self)

        heading_ = QLabel("<h1>Inject Database</h1>")
        heading_.setObjectName("heading_")
        layout_.addWidget(heading_)

        critical_info = QLabel("<h1>Export Students</h1>")
        critical_info.setObjectName("mild_info_lbl")
        critical_info.setText("⚠ Warning: Injecting an unknown or unverified database may lead to crashes, data corruption, or unexpected behavior.\nPlease ensure that the database you are importing was created and validated by this software before proceeding.")
        layout_.addWidget(critical_info)

        btn_inject = QPushButton("⚠ Inject")
        btn_inject.setFixedWidth(300)
        btn_inject.setObjectName("ui_btn")
        btn_inject.setProperty("ui", "red")
        btn_inject.clicked.connect(self.on_inject)
        layout_.addWidget(btn_inject)

    def on_inject(self):
        try:
            new_db_file, _ = QFileDialog.getOpenFileName(self, "Select database file to inject", "", "Ms Access Files (*.accdb)")
            if new_db_file:
                conf_ = MessageBox.ask_question("It's highly recommended that save current database before injecting new database.\nWould you like to export current database?")
                if conf_:
                    path_to_save, _ = QFileDialog.getSaveFileName(self, "Select path to save", "", "Ms Access Files (*.accdb)")
                    if path_to_save:
                        with open(path_to_save, "wb") as fp:
                            with open(self.db_instance.data_file_path, "rb") as fp2:
                                fp.write(fp2.read())

                        MessageBox().show_message("Info", f"Current database file has been save at `{path_to_save}`", "info")
                    self.db_instance.db.close()
                    with open(self.db_instance.data_file_path, "wb") as fp:
                        with open(new_db_file, "rb") as fp2:
                            fp.write(fp2.read())
                    self.db_instance.reconnect()
                    MessageBox().show_message("Info", "Successfully injected new database file.", "info")
        except BaseException as e:
            MessageBox().show_message("Error", f"Failed to inject new database.\nError : {e}", "error")

class ImportExportPage(QFrame):
    def __init__(self, db_instance:MsAccessDriver):
        super().__init__()

        with open("style_sheets/import_export_page.css", "r") as fp:
            self.setStyleSheet(fp.read())
        self.setObjectName("import_export_body")

        layout_ = QVBoxLayout(self)

        ui_holder = QWidget()
        ui_holder.setObjectName("ui_holder")
        ui_holder_layout = QVBoxLayout(ui_holder)
        ui_holder_layout.setContentsMargins(0, 0, 0, 0)
        ui_holder_layout.setSpacing(12)

        imp_data_area = ImportStudentDataArea(db_instance=db_instance)
        ui_holder_layout.addWidget(imp_data_area)

        exp_attendacne_area = ExportAttendanceArea(db_instance=db_instance)
        ui_holder_layout.addWidget(exp_attendacne_area)

        exp_student_data = ExportStudentData(db_instance=db_instance)
        ui_holder_layout.addWidget(exp_student_data)

        inject_db = InjectDatabase(db_instance=db_instance)
        ui_holder_layout.addWidget(inject_db)

        ui_holder_layout.addStretch(1)

        scrollable = QScrollArea()
        scrollable.setObjectName("scrollable")
        scrollable.setWidgetResizable(True)
        scrollable.setWidget(ui_holder)
        layout_.addWidget(scrollable)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow

    app_ = QApplication([])

    win_ = QMainWindow()
    ele_ = ImportExportPage()
    win_.setCentralWidget(ele_)
    win_.show()

    app_.exec()
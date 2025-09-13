import os
from PyQt5.QtWidgets import *
from additional_widgets import *
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QIntValidator, QIcon
from app_constants import AppConstant
from excel_functions import *
from qt_theading import ImageProcessingWorker
import pickle

class EntryField(QWidget):
    entry_input = None

    def __init__(self, lbl_text, placeholder="", input_type="string", select_items=None):
        super().__init__()
        self.setObjectName("entry_field")
        layout_ = QVBoxLayout(self)

        entry_lbl = QLabel(lbl_text)
        entry_lbl.setObjectName("entry_lbl")
        layout_.addWidget(entry_lbl)

        if input_type == "select":
            self.entry_input = QComboBox()
            self.entry_input.setObjectName("entry_input")
            self.entry_input.setProperty("type", input_type)
            self.entry_input.setEditable(True)
            for item in select_items:
                self.entry_input.addItem(item)
            layout_.addWidget(self.entry_input)
        else:
            self.entry_input = QLineEdit()
            self.entry_input.setObjectName("entry_input")
            self.entry_input.setPlaceholderText(placeholder)
            if input_type == "int":
                self.entry_input.setValidator(QIntValidator(0, int(2e+9)))
            layout_.addWidget(self.entry_input)

    def getValue(self):
        if isinstance(self.entry_input, QComboBox):
            return self.entry_input.currentText()
        return self.entry_input.text()

    def setValue(self, value_):
        if isinstance(self.entry_input, QComboBox):
            self.entry_input.setCurrentText(value_)
        else:
            self.entry_input.setText(value_)

    def setSelectItems(self, select_items):
        self.entry_input.clear()
        for item in select_items:
            self.entry_input.addItem(item)

class AddStudentForm(QFrame):
    name_entry = None
    father_name_entry = None
    mobile_no_entry = None
    class_entry = None
    section_entry = None
    user_face_encodings = None
    reload_table_callback = None
    std_db = None
    attndnc_db_manager = None
    td1 = None  # Thread 1
    img_capture_worker = None  # Worker running on Thread 1
    image_holder_layout = None

    def __init__(self, std_db:ExcelFileWorker, attndnc_db_manager:AttendanceDBManager):
        super().__init__()
        self.std_db = std_db
        self.attndnc_db_manager = attndnc_db_manager
        self.setObjectName("add_students_area")
        layout_ = QVBoxLayout(self)

        # ------------------------ HEADER ---------------------------
        header_ = QWidget()
        header_.setObjectName("header_")
        header_layout = QHBoxLayout(header_)
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.back_btn = QImageView("icons/arrow_left_icon.svg", (30, 30))
        self.back_btn.setObjectName("back_btn")
        self.back_btn.on_click = self.on_back
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setAlignment(Qt.AlignRight)
        self.back_btn.setVisible(False)
        header_layout.addWidget(self.back_btn, alignment=Qt.AlignVCenter)

        heading_ = QLabel("Add Students")
        heading_.setObjectName("heading_")
        header_layout.addWidget(heading_)

        header_layout.addStretch(1)

        self.drop_down = QImageView("icons/arrow_drop_down.svg", (40, 40))
        self.drop_down.on_click = self.on_dropdown_open
        self.drop_down.setCursor(Qt.PointingHandCursor)
        self.drop_down.setAlignment(Qt.AlignRight)
        header_layout.addWidget(self.drop_down)
        layout_.addWidget(header_)
        # ------------------------ HEADER END ---------------------------

        # ------------------------ FORM PART 1 ---------------------------
        self.form_ = form_ = QWidget()
        form_.setObjectName("add_student_form")
        form_.setVisible(False)
        form_layout = QGridLayout(form_)
        form_layout.setContentsMargins(0, 0, 0, 0)

        self.adm_no_entry = EntryField("Admission Number", input_type="int")
        form_layout.addWidget(self.adm_no_entry, 0, 0)

        self.name_entry = EntryField("Student Name")
        form_layout.addWidget(self.name_entry, 0, 1)

        self.father_name_entry = EntryField("Father Name")
        form_layout.addWidget(self.father_name_entry, 1, 0)

        self.mobile_no_entry = EntryField("Mobile Number")
        form_layout.addWidget(self.mobile_no_entry, 1, 1)

        self.class_entry = EntryField("Class", input_type="select", select_items=[])
        form_layout.addWidget(self.class_entry, 2, 0)

        self.section_entry= EntryField("Section", input_type="select", select_items=[])
        form_layout.addWidget(self.section_entry, 2, 1)
        self.auto_filler()

        next_btn = QPushButton("Next")
        next_btn.setObjectName("next_btn")
        next_btn.setFixedWidth(300)
        next_btn.clicked.connect(self.on_next_step)
        next_btn.setCursor(Qt.PointingHandCursor)
        form_layout.addWidget(next_btn, 3, 0, 1, 2, Qt.AlignCenter)
        layout_.addWidget(form_, stretch=1)


        # ------------------------ FORM PART 1 END ---------------------------

        # ------------------------ FORM PART 2 ---------------------------
        self.form_2 = QWidget()
        self.form_2.setObjectName("add_student_form")
        self.form_2.setProperty("part", "two")
        self.form_2.setVisible(False)
        form2_layout = QGridLayout(self.form_2)
        form2_layout.setContentsMargins(0, 12, 0, 0)

        # lbl_part2 = QLabel("Please provide your images")
        # lbl_part2.setObjectName("lbl_part2")
        # form2_layout.addWidget(lbl_part2, 0, 0)

        self.cam_preview = QPushButton("No preview available yet.")
        self.cam_preview.setObjectName("cam_preview")
        # self.cam_preview.setEnabled(False)
        self.cam_preview.setFlat(True)
        self.cam_preview.setFixedWidth(250)
        self.cam_preview.setFixedHeight(250)
        form2_layout.addWidget(self.cam_preview, 0, 0)

        self.capture_progress = QProgressBar()
        self.capture_progress.setObjectName("capture_progress")
        self.capture_progress.setValue(0)
        self.capture_progress.setFixedWidth(240)
        self.capture_progress.setAlignment(Qt.AlignCenter)
        form2_layout.addWidget(self.capture_progress, 1, 0, Qt.AlignHCenter)

        self.start_capture = QPushButton("Start Capturing")
        self.start_capture.setObjectName("start_capture")
        self.start_capture.setCursor(Qt.PointingHandCursor)
        self.start_capture.clicked.connect(self.onStartCapturing)
        form2_layout.addWidget(self.start_capture, 2, 0)

        self.stop_capture = QPushButton("Stop Capturing")
        self.stop_capture.setVisible(False)
        self.stop_capture.setObjectName("stop_capture")
        self.stop_capture.setCursor(Qt.PointingHandCursor)
        self.stop_capture.clicked.connect(self.onStopCapturing)
        form2_layout.addWidget(self.stop_capture, 2, 0)

        lbl_area = QWidget()
        lbl_area_layout = QVBoxLayout(lbl_area)
        self.lbl_instruction = QLabel("● Instruction : Please see in camera and keep changing your face expressions and face angle.")
        self.lbl_instruction.setObjectName("lbl_instruction")
        lbl_area_layout.addWidget(self.lbl_instruction)

        self.lbl_warning = QLabel("")
        self.lbl_warning.setObjectName("lbl_warning")
        lbl_area_layout.addWidget(self.lbl_warning)

        captured_holder = QGroupBox()
        captured_holder.setTitle("Captured Images")
        captured_holder.setObjectName("capture_holder")
        captured_holder_layout = QVBoxLayout(captured_holder)

        image_holder = QWidget()
        self.image_holder_layout = QGridLayout(image_holder)

        scrollable_ = QScrollArea(captured_holder)
        scrollable_.setWidget(image_holder)
        scrollable_.setWidgetResizable(True)
        captured_holder_layout.addWidget(scrollable_)
        lbl_area_layout.addWidget(captured_holder, stretch=1)

        form2_layout.addWidget(lbl_area, 0, 1, 2, 1)

        self.add_student_btn = add_student_btn = QPushButton("Add Student")
        add_student_btn.setVisible(False)
        add_student_btn.setObjectName("add_student_btn")
        add_student_btn.setFixedWidth(300)
        add_student_btn.clicked.connect(self.on_submit)
        add_student_btn.setCursor(Qt.PointingHandCursor)
        form2_layout.addWidget(add_student_btn, 2, 0, 1, 2, Qt.AlignCenter)

        layout_.addWidget(self.form_2, stretch=1)
        # ------------------------ FORM PART 2 END ---------------------------

    def on_back(self):
        self.form_2.setVisible(False)
        self.back_btn.setVisible(False)
        self.form_.setVisible(True)

    def on_dropdown_open(self):
        self.auto_filler()
        self.form_.setVisible(True)
        self.drop_down.setIcon("icons/arrow_drop_up.svg")
        self.form_2.setVisible(False)
        self.drop_down.on_click = self.on_dropdown_close
    def on_dropdown_close(self):
        self.back_btn.setVisible(False)
        self.form_.setVisible(False)
        self.form_2.setVisible(False)
        self.drop_down.setIcon("icons/arrow_drop_down.svg")
        self.drop_down.on_click = self.on_dropdown_open

    def auto_filler(self):
        self.adm_no_entry.setValue(str(safe_max(self.std_db.getColumnByIndex(0)) + 1))
        classes_ = []
        sections_ = []
        for cls_sec in os.listdir(AppConstant.CLASS_DIRECTORY):
            cls_sec = cls_sec.split("-")
            classes_.append(cls_sec[0])
            sections_.append(cls_sec[-1])
        self.class_entry.setSelectItems(set(classes_))
        self.section_entry.setSelectItems(set(sections_))

    def on_next_step(self):
        try:
            data_to_add = [self.adm_no_entry.getValue(), self.name_entry.getValue(), self.father_name_entry.getValue(), self.mobile_no_entry.getValue(), self.class_entry.getValue(), self.section_entry.getValue()]
            if '' in data_to_add:
                MessageBox().show_message("Error", "All entries are required please fill them all and try again.", "error")
                return
            data_to_add[0] = int(str(data_to_add[0]))
            assert data_to_add[0] not in self.std_db.getPrimaryColumnValues(), f"Admission no. '{data_to_add[0]}' already exists."  # Throws error as : [12 not in [11, 12, 13] -> False -> Assert Error]
            self.back_btn.setVisible(True)
            self.form_.setVisible(False)
            self.form_2.setVisible(True)
        except BaseException as e:
            MessageBox().show_message("Error", f"Can't proceed due to error.\nError : {e}", "error")

    def clear_all_form(self):
        self.name_entry.setValue("")
        self.father_name_entry.setValue("")
        self.mobile_no_entry.setValue("")
        self.class_entry.setValue("")
        self.section_entry.setValue("")
        self.cam_preview.setIcon(QIcon())
        self.capture_progress.setValue(0)
        self.start_capture.setVisible(True)
        clearLayout(self.image_holder_layout)
        self.add_student_btn.setVisible(False)
        self.lbl_instruction.setText("● Instruction : Please see in camera and keep changing your face expressions and face angle.")
        self.lbl_warning.setText("")
        try:
            self.img_capture_worker.stop()
            self.img_capture_worker = None
            self.td1.quit()
            self.td1.wait()
            self.td1.deleteLater()
            self.td1 = None
        except BaseException as e:
            print(e)
        self.on_back()

    def on_submit(self):
        try:
            data_to_add = [self.adm_no_entry.getValue(), self.name_entry.getValue(), self.father_name_entry.getValue(), self.mobile_no_entry.getValue(), self.class_entry.getValue(), self.section_entry.getValue()]
            data_to_add[0] = int(str(data_to_add[0]))
            cls_ = f"{self.class_entry.getValue()}-{self.section_entry.getValue()}"
            if cls_ not in os.listdir(AppConstant.CLASS_DIRECTORY):
                conf_ = MessageBox.ask_question(f"Class ‘{cls_}’ was not found. Would you like to create it so the student can be added?")
                if not conf_:
                    return
                if cls_.count("-") != 1:
                    MessageBox().show_message("Error", "class and section names must not contain '-'.\nClass creation cancelled - Failed to add student.", "error")
                    return
                os.mkdir(os.path.join(AppConstant.CLASS_DIRECTORY, cls_))
                self.attndnc_db_manager.createThisYearAttendanceSheet(cls_)
            enc_file_name = f"faceOf{data_to_add[0]}.pkl"
            data_to_add.append(enc_file_name)
            with open(os.path.join(AppConstant.ENCODINGS_DIRECTORY, enc_file_name), "wb") as fp:
                pickle.dump({"admission_no": data_to_add[0], "encodings": self.user_face_encodings}, fp)
            self.std_db.appendRow(data_to_add)
            self.auto_filler()
            self.attndnc_db_manager.insertNewStudent(cls_, data_to_add[0], data_to_add[1])
            if callable(self.reload_table_callback):
                self.reload_table_callback()
            self.user_face_encodings = None
            self.clear_all_form()
            MessageBox().show_message("Info", "Successfully added a student.", "info")
        except BaseException as e:
            MessageBox().show_message("Error", f"Failed to add student entry.\nError : {e}", "error")

    def onStartCapturing(self):
        def on_load_img_preview(png_data):
            pix_map = QPixmap()
            pix_map.loadFromData(png_data)
            self.cam_preview.setIcon(QIcon(pix_map))
            self.cam_preview.setIconSize(pix_map.size())

        def on_simple_messages(data_):
            if data_["type"] == "error":
                print(data_["msg"])
            elif data_["type"] == "warn":
                self.lbl_warning.setText(data_["msg"])
            elif data_["type"] == "info":
                self.lbl_instruction.setText(data_["msg"])

        i = j = 0
        img_to_be_capture = 10
        captured_ = 1
        def on_captured(img_):
            nonlocal  i, j, captured_
            iv = QImageView(size=(100, 100))
            iv.setFixedWidth(100)
            iv.setFixedHeight(100)
            iv.setIconFromBytes(img_)
            iv.setObjectName("image_view_icco")
            iv.setStyleSheet("#image_view_icco {border: 1px solid gray; border-radius: 3px;}")
            self.image_holder_layout.addWidget(iv, i, j)

            self.capture_progress.setValue(int((captured_/img_to_be_capture)*100))
            if captured_ == img_to_be_capture:
                self.lbl_instruction.setText("● Successfully captured all images.")
                self.img_capture_worker.stop()
                self.stop_capture.setVisible(False)
                self.add_student_btn.setVisible(True)
                return
            captured_ += 1
            if j == 4:
                i += 1
                j = 0
            else:
                j += 1

        def on_all_encodings(data_):
            self.user_face_encodings = data_

        try:
            self.td1 = QThread()
            self.img_capture_worker = ImageProcessingWorker()
            self.img_capture_worker.moveToThread(self.td1)
            self.td1.started.connect(self.img_capture_worker.run)
            self.img_capture_worker.msg_channel.connect(on_simple_messages)
            self.img_capture_worker.captured.connect(on_captured)
            self.img_capture_worker.preview_img_messaged.connect(on_load_img_preview)
            self.img_capture_worker.encodings_output.connect(on_all_encodings)
            # self.img_capture_worker.final_output.connect(print)
            self.td1.finished.connect(lambda : self.onStopCapturing(True))
            self.td1.start()
        except BaseException as e:
            print(e)
        self.start_capture.setVisible(False)
        self.stop_capture.setVisible(True)

    def onStopCapturing(self, only_ui_update=False):
        if not only_ui_update:
            self.img_capture_worker.stop()
            self.td1.quit()
        self.lbl_instruction.setText("● Instruction : Please see in camera and keep changing your face expressions and face angle.")
        self.lbl_warning.setText("")
        self.capture_progress.setValue(0)
        self.cam_preview.setIcon(QIcon())
        self.stop_capture.setVisible(False)
        self.start_capture.setVisible(True)
        clearLayout(self.image_holder_layout)

class StudentsTable(QFrame):
    std_db = None
    is_table_loading = False

    def __init__(self, std_db:ExcelFileWorker):
        super().__init__()
        self.std_db = std_db
        layout_ = QVBoxLayout(self)
        self.setObjectName("student_table_holder")

        self.lbl_no_data = QLabel("<h2>No students found.</h2>")
        self.lbl_no_data.setObjectName("lbl_no_data")
        self.lbl_no_data.setVisible(True)
        layout_.addWidget(self.lbl_no_data, alignment=Qt.AlignTop | Qt.AlignCenter)

        self.table_ = QTableWidget(self)
        self.table_.setVisible(False)
        self.table_.setObjectName("table_")
        self.table_.setShowGrid(False)
        self.load_data()
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
        table_header.setStretchLastSection(True)
        table_header.setSortIndicatorShown(True)
        table_header.setSectionsClickable(True)
        table_header.setSortIndicator(0, Qt.AscendingOrder)
        table_header.setSectionResizeMode(QHeaderView.Stretch)

        layout_.addWidget(self.table_)

    def load_data(self):
        self.table_.setSortingEnabled(False)
        self.table_.clear()
        total_rows = self.std_db.getNoOfRows()
        total_cols = self.std_db.getNoOfColumns()
        self.table_.setRowCount(total_rows-1)
        self.table_.setColumnCount(total_cols+1)

        self.table_.setHorizontalHeaderLabels(self.std_db.getHeaderLabels()+["Delete"])

        if total_rows-1 <= 0:
            self.table_.setVisible(False)
            self.lbl_no_data.setVisible(True)
            self.table_.setSortingEnabled(True)
            return
        self.is_table_loading = True

        self.lbl_no_data.setVisible(False)
        self.table_.setVisible(True)

        for x in range(total_rows-1):
            row_ = self.std_db.getRowByIndex(x+1)
            idx_ = 0
            for idx_, data_  in enumerate(row_):
                if idx_ == self.std_db.primary_column_idx:
                    data_item = QTableWidgetItem()
                    data_item.setData(Qt.DisplayRole, int(data_))
                else:
                    data_item = QTableWidgetItem(data_)
                if idx_ == 6:  # Disabled editing of Encoding file name column.
                    data_item.setFlags(data_item.flags() & ~Qt.ItemIsEditable)
                data_item.setTextAlignment(Qt.AlignCenter)
                self.table_.setItem(x, idx_, data_item)
            delete_btn = QImageView("icons/delete_icon.svg")
            delete_btn.setAlignment(Qt.AlignCenter)
            delete_btn.on_click = lambda x_copy=x: self.onDelete(x_copy)
            self.table_.setCellWidget(x, idx_+1, delete_btn)
        self.table_.setSortingEnabled(True)
        self.is_table_loading = False

    def onDelete(self, row_idx):
        conf_ = MessageBox.ask_question("Do you really want to permanently delete this entry?")
        if conf_:
            encoding_file_ = self.std_db.getRowByIndex(row_idx+1)
            encoding_file_path = os.path.join(AppConstant.ENCODINGS_DIRECTORY, encoding_file_[-1])
            if os.path.exists(encoding_file_path):
                os.remove(encoding_file_path)
            self.std_db.deleteRowByIndex(row_idx+1)
            self.load_data()

    def onEdit(self, row_, col_):
        if self.is_table_loading:
            return
        try:
            new_value = self.table_.item(row_, col_).text()
            if col_ == self.std_db.primary_column_idx:
                if not new_value.isnumeric():
                    MessageBox().show_message("Error", "Can't update value - Required type int.", "error")
                    self.table_.item(row_, col_).setText(self.table_.old_value)
                    self.table_.cellChanged.connect(self.onEdit)
                    return
                self.std_db.updateByLocation(row_+2, col_+1, int(new_value))
            else:
                self.std_db.updateByLocation(row_+2, col_+1, new_value)
        except BaseException as e:
            MessageBox().show_message("Error", f"Can't update value.\nError : {e}", "error")

class StudentsPage(QFrame):
    def __init__(self):
        super().__init__()
        with open("style_sheets/students_page.css", "r") as fp:
            self.setStyleSheet(fp.read())
        self.setObjectName("student_main_body")

        layout_ = QVBoxLayout(self)

        student_file_driver = ExcelFileWorker(AppConstant.STUDENTS_FILE, 0)
        attendance_db_manager = AttendanceDBManager()

        add_students_area = AddStudentForm(std_db=student_file_driver, attndnc_db_manager=attendance_db_manager)
        layout_.addWidget(add_students_area)

        student_table = StudentsTable(std_db=student_file_driver)
        layout_.addWidget(student_table, stretch=1)

        add_students_area.reload_table_callback = student_table.load_data

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app_ = QApplication([])

    win_ = QMainWindow()
    ele_ = StudentsPage()
    win_.setCentralWidget(ele_)
    win_.show()

    app_.exec()
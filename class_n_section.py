import os
from PyQt5.QtWidgets import *
from additional_widgets import *
from PyQt5.QtCore import Qt
from app_constants import AppConstant


class ClassElement(QFrame):
    drop_down = None
    hidden_element = None
    cls_name = None

    def __init__(self, cls_name, cls_files):
        super().__init__()
        self.setObjectName("class_element")
        self.cls_name = cls_name

        layout_ = QVBoxLayout(self)

        main_element = QWidget()
        main_element_layout = QHBoxLayout(main_element)
        main_element_layout.setContentsMargins(0, 0, 0, 0)

        cls_name_lbl = QLabel("➤  "+cls_name)
        cls_name_lbl.setObjectName("class_label")
        main_element_layout.addWidget(cls_name_lbl)
        main_element_layout.addStretch(1)

        self.drop_down = drop_down = QImageView("icons/arrow_drop_down.svg")
        drop_down.on_click = self.on_click_dropdown
        drop_down.setCursor(Qt.PointingHandCursor)
        main_element_layout.addWidget(drop_down)
        layout_.addWidget(main_element)

        self.hidden_element = hidden_element = QWidget()
        hidden_element.setVisible(False)
        hidden_element.setObjectName("hidden_element")
        hidden_element_layout = QVBoxLayout(hidden_element)
        hidden_element_layout.setContentsMargins(0, 5, 0, 0)

        delete_icon = QImageView("icons/delete_icon.svg", (25, 25))
        delete_icon.setObjectName("delete_btn")
        delete_icon.setAlignment(Qt.AlignRight)
        delete_icon.setCursor(Qt.PointingHandCursor)
        delete_icon.on_click = self.on_delete_cls
        hidden_element_layout.addWidget(delete_icon, alignment=Qt.AlignRight)

        under_line = QFrame()
        under_line.setFixedHeight(1)
        under_line.setObjectName("under_line")
        hidden_element_layout.addWidget(under_line)

        if not cls_files:
            lbl_ = QLabel("No attendance record!")
            lbl_.setObjectName("no_record")
            lbl_.setAlignment(Qt.AlignCenter)
            hidden_element_layout.addWidget(lbl_)

        for item in cls_files:
            lbl_ = QLabel("●  "+item)
            lbl_.setObjectName("cls_file_name")
            lbl_.setCursor(Qt.PointingHandCursor)
            hidden_element_layout.addWidget(lbl_)
        layout_.addWidget(hidden_element)

    def on_click_dropdown(self):
        if self.hidden_element.isVisible():
            self.hidden_element.setVisible(False)
            self.drop_down.setIcon("icons/arrow_drop_down.svg")
        else:
            self.hidden_element.setVisible(True)
            self.drop_down.setIcon("icons/arrow_drop_up.svg")

    def on_delete_cls(self):
        confirm_ = MessageBox.ask_question("Do you really want to delete whole class with all its attendance records?")
        if confirm_:
            try:
                out_ = os.popen(f"rmdir /s /q {os.path.join(AppConstant.CLASS_DIRECTORY, self.cls_name)}").read()
                assert out_ == "", out_
                self.deleteLater()
                MessageBox().show_message("Info", f"Class '{self.cls_name}' has been deleted successfully.", "info")
            except BaseException as e:
                MessageBox().show_message("Error", f"Failed to delete.\nError : {e}", "error")


class ClassList(QFrame):
    cls_list_holder = None
    cls_list_holder_layout = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("class_list")
        self.setMinimumWidth(250)

        layout_ = QVBoxLayout(self)

        area_heading = QLabel("Classes")
        area_heading.setObjectName("class_list_heading")
        area_heading.setAlignment(Qt.AlignCenter)
        layout_.addWidget(area_heading)

        scroll_area1 = QScrollArea(self)
        scroll_area1.setObjectName("list_scrollable")
        scroll_area1.setWidgetResizable(True)
        scroll_area1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.cls_list_holder = cls_list_holder = QWidget()
        cls_list_holder.setObjectName("list_holder")
        self.cls_list_holder_layout = cls_list_holder_layout = QVBoxLayout()
        cls_list_holder_layout.setContentsMargins(0, 0, 0, 0)

        self.load_classes()

        cls_list_holder.setLayout(cls_list_holder_layout)
        scroll_area1.setWidget(cls_list_holder)
        layout_.addWidget(scroll_area1)

    def load_classes(self):
        classes_ = os.listdir(AppConstant.CLASS_DIRECTORY)
        if not classes_:
            lbl_ = QLabel("No attendance record!")
            lbl_.setObjectName("no_record")
            lbl_.setAlignment(Qt.AlignCenter)
            self.cls_list_holder_layout.addWidget(lbl_)
            return

        clearLayout(self.cls_list_holder_layout)

        for dir_ in classes_:
            attendance_records = os.listdir(os.path.join(AppConstant.CLASS_DIRECTORY, dir_))
            cls_element = ClassElement(dir_, attendance_records)
            self.cls_list_holder_layout.addWidget(cls_element)
        self.cls_list_holder_layout.addStretch(1)


class AddClassForm(QFrame):
    cls_name_entry = None
    cls_sec_entry = None
    reload_classes_callback = None

    def __init__(self, reload_class_callback, parent=None):
        super().__init__(parent)
        self.reload_classes_callback = reload_class_callback

        self.setObjectName("add_class_form")

        layout_ = QVBoxLayout(self)
        lbl_add_class = QLabel("Add Class")
        lbl_add_class.setObjectName("add_class_lbl")
        layout_.addWidget(lbl_add_class)

        self.cls_name_entry = class_name = QLineEdit()
        class_name.setPlaceholderText("Enter class name")
        class_name.setObjectName("entry")
        layout_.addWidget(class_name)

        self.cls_sec_entry = sec_name = QLineEdit()
        sec_name.setPlaceholderText("Enter section name")
        sec_name.setObjectName("entry")
        layout_.addWidget(sec_name)

        btn_add = QPushButton("Add Class")
        btn_add.setObjectName("add_cls_btn")
        btn_add.setFixedWidth(200)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self.on_click_add_class)
        layout_.addWidget(btn_add, alignment=Qt.AlignCenter)

        layout_.addStretch(1)

    def on_click_add_class(self):
        if not self.cls_name_entry.text() or not self.cls_sec_entry.text():
            MessageBox().show_message("Warning", f"All entries are required, please fill and retry.\nCREATION_FAILED", "warn")
            return
        try:
            dir_name = f"{self.cls_name_entry.text()}-{self.cls_sec_entry.text()}"
            assert dir_name.count("-") == 1, "'-' is not allowed in class and section names please use '_' or ' ' instead."
            os.mkdir(os.path.join(AppConstant.CLASS_DIRECTORY, dir_name))
            self.reload_classes_callback()
            MessageBox().show_message("Info", f"Class '{dir_name}' created successfully.", "info")
        except BaseException as e:
            MessageBox().show_message("Error", f"Failed to create class.\nError : {e}", "error")


class AttendanceSheetPreview(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("attendance_sheet_preview")
        layout_ = QVBoxLayout(self)

        lbl1 = QLabel("Hello World")
        layout_.addWidget(lbl1)


class ClassNSectionPage(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("classNsec_body")
        with open("style_sheets/class_n_section.css", "r") as fp:
            self.setStyleSheet(fp.read())

        layout_ = QHBoxLayout(self)  # no need to call setLayout() when passing a parent.

        bi_area = QSplitter()
        bi_area.setObjectName("bi_area")
        bi_area.setOrientation(Qt.Horizontal)
        cls_list = ClassList()
        bi_area.addWidget(cls_list)
        bi_area.setStretchFactor(0, 1)

        vertical_area = QWidget()
        vertical_area_layout = QVBoxLayout(vertical_area)
        vertical_area_layout.setContentsMargins(0, 0, 0, 0)

        add_class_form = AddClassForm(reload_class_callback=cls_list.load_classes)
        vertical_area_layout.addWidget(add_class_form)

        sheet_preview = AttendanceSheetPreview()
        vertical_area_layout.addWidget(sheet_preview, stretch=1)

        bi_area.addWidget(vertical_area)

        bi_area.setStretchFactor(1, 3)
        layout_.addWidget(bi_area)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app_ = QApplication([])

    win_ = QMainWindow()
    ele_ = ClassNSectionPage()
    win_.setCentralWidget(ele_)
    win_.show()

    app_.exec()
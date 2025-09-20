from PyQt5.QtWidgets import QLabel, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

def clearLayout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

class QImageView(QLabel):
    size = (32, 32)
    on_click = None

    def __init__(self, icon_path=None, size=(32, 32), parent=None):
        super().__init__(parent)
        self.size = size
        icon_ = QPixmap(icon_path)
        self.setPixmap(icon_.scaled(*size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def setIcon(self, icon_path):
        icon_ = QPixmap(icon_path)
        self.setPixmap(icon_.scaled(*self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def setIconFromBytes(self, image_bytes):
        icon_ = QPixmap()
        icon_.loadFromData(image_bytes)
        self.setIcon(icon_.scaled(*self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def mousePressEvent(self, ev):
        if callable(self.on_click):
            self.on_click()

class MessageBox:
    _type_map = {
        "info": QMessageBox.Information,
        "warn": QMessageBox.Warning,
        "error": QMessageBox.Critical,
    }

    def __init__(self):
        pass

    def show_message(self, title, msg_, type_):
        msg_b = QMessageBox()
        msg_b.setWindowIcon(QIcon("icons/circle_blue.svg"))
        msg_b.setIcon(self._type_map[type_])
        msg_b.setWindowTitle(title)
        msg_b.setText(msg_)
        msg_b.setStandardButtons(QMessageBox.Close)
        msg_b.exec()

    @staticmethod
    def ask_question(msg_):
        msg_b = QMessageBox()
        msg_b.setWindowIcon(QIcon("icons/circle_blue.svg"))
        msg_b.setWindowTitle("Question")
        msg_b.setIcon(QMessageBox.Question)
        msg_b.setText(msg_)
        msg_b.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return msg_b.exec() == QMessageBox.Ok


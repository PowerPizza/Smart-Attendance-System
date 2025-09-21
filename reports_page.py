import os

from PyQt5.QtWidgets import *

from additional_widgets import *
from PyQt5.QtCore import Qt, QThread, QSize, QDate
from PyQt5.QtGui import QIntValidator, QIcon
from database_manager import MsAccessDriver, EncodeType
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolor
import calendar
import numpy as np
from uuid import uuid4
from qt_theading import UIBlockingTaskRunner

class PieChartHolder(QFrame):
    def __init__(self, db_instance: MsAccessDriver):
        super().__init__()
        self.db_instance = db_instance
        layout_ = QVBoxLayout(self)

        lbl_title = QLabel("<h2>Attendance Distribution</h2>")
        lbl_title.setObjectName("lbl_title")
        layout_.addWidget(lbl_title, alignment=Qt.AlignTop | Qt.AlignHCenter)

        self.no_found_lbl = QLabel("")
        self.no_found_lbl.setStyleSheet("font-size: 14px; color: white;")
        self.no_found_lbl.setVisible(False)
        layout_.addWidget(self.no_found_lbl, alignment=Qt.AlignCenter)

        self.pie_chart_holder = QImageView("", size=(300, 300))
        layout_.addWidget(self.pie_chart_holder)

        self.date_selection = date_selection = QDateEdit()
        date_selection.setObjectName("date_selection")
        date_selection.setDisplayFormat("dd-MM-yyyy")
        date_selection.setDate(QDate.currentDate())
        date_selection.setCalendarPopup(True)
        date_selection.dateChanged.connect(self.load_pie_chart)
        layout_.addWidget(date_selection, alignment=Qt.AlignBottom)
        self.load_pie_chart(date_selection.date())

    def load_pie_chart(self, date_):
        self.no_found_lbl.setVisible(False)
        self.pie_chart_holder.setVisible(True)

        # self.pie_chart_holder.setIcon("")
        self.db_instance.cursor.execute("SELECT status FROM attendance WHERE mark_date=?", date_.toPyDate())
        db_resp = [item[0] for item in self.db_instance.cursor.fetchall()]
        if not db_resp:
            self.pie_chart_holder.setVisible(False)
            self.no_found_lbl.setText(f"No. attendance records were\nfound on date `{date_.toString()}`")
            self.no_found_lbl.setVisible(True)
            return

        plot_titles = ["", "", ""]
        p_perc = (db_resp.count("P") / len(db_resp)) * 100
        a_perc = (db_resp.count("A") / len(db_resp)) * 100
        na_perc = (db_resp.count("N/A") / len(db_resp)) * 100
        x_axis = [p_perc, a_perc, na_perc]

        wedges, texts, autotexts = plt.pie(x_axis, labels=plot_titles,
                colors=["#39c75c", "#fe6b66", "#4b92e3"], autopct="%1.1f%%", explode=(0.05, 0.07, 0.08),
                shadow=True, startangle=90, radius=1.4,
                textprops={"fontsize": 18, "color": "white", "fontweight": 800}, pctdistance=0.4)

        for idx_, item in enumerate(x_axis):
            if item == 0:
                autotexts[idx_].remove()

        for autotext, wedge in zip(autotexts, wedges):
            angle = (wedge.theta2 + wedge.theta1) / 2
            x, y = autotext.get_position()
            autotext.set_position((1.2 * x, 1.2 * y))
            autotext.set_rotation(angle)
            autotext.set_rotation_mode("anchor")
        legends_ = plt.legend(["Present", "Absent", "N/A"], loc=(-0.37, 0.9), facecolor="#1f2121", prop={'size': 14, 'weight': 'bold'})
        for item in legends_.get_texts():
            item.set_color("#ffffff")
        img_path = os.path.join(os.getenv("TEMP"), f"{uuid4()}.png".replace("-", ""))
        plt.savefig(img_path, facecolor="#262828")
        plt.close("all")
        self.pie_chart_holder.setIcon(img_path)
        os.remove(img_path)

class ClassWiseAttendanceGraph(QFrame):
    db_instance = None
    cls_sec_filter = "All"
    is_filters_loaded = False

    def __init__(self, db_instance: MsAccessDriver):
        super().__init__()
        self.db_instance = db_instance

        layout_ = QVBoxLayout(self)

        header_ = QWidget()
        header_layout = QHBoxLayout(header_)
        header_layout.setContentsMargins(0, 0, 0, 0)
        lbl_title = QLabel("<h2>Class-Wise Attendance Trend</h2>")
        lbl_title.setObjectName("lbl_title")
        header_layout.addWidget(lbl_title, alignment=Qt.AlignHCenter)

        cls_sec_group = QGroupBox()
        cls_sec_group.setTitle("class-section")
        cls_sec_select_layout = QHBoxLayout(cls_sec_group)
        cls_sec_select_layout.setContentsMargins(0, 0, 0, 0)
        self.cls_sec_select = cls_sec_select = QComboBox()
        cls_sec_select.setMinimumWidth(100)
        cls_sec_select.addItem("All")
        cls_sec_select.currentTextChanged.connect(self.on_cls_sec_filter)
        cls_sec_select_layout.addWidget(cls_sec_select)
        header_layout.addWidget(cls_sec_group, alignment=Qt.AlignRight)

        layout_.addWidget(header_)

        self.graph_holder = graph_holder = QLabel("")
        self.graph_holder.setObjectName("graph_holder")
        self.graph_holder.setScaledContents(True)
        layout_.addWidget(graph_holder, stretch=1)

        self.load_chart()

    def on_cls_sec_filter(self, value_):
        self.cls_sec_filter = value_
        self.load_chart()

    def load_chart(self):
        try:
            self.db_instance.cursor.execute("SELECT class, section, MONTH(mark_date), ROUND((SUM(IIF(status=?, 1, 0))/count(status)) * 100, 2) FROM attendance INNER JOIN students ON students.admission_no = attendance.admission_no WHERE YEAR(mark_date)=? GROUP BY class, section, MONTH(mark_date)", "P", QDate.currentDate().year())
            db_resp = self.db_instance.cursor.fetchall()
            db_resp = [item for item in db_resp]
            months_ = ["Jan", "Feb", "Mar", "Apr", 'May', "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", 'Dec']

            class_count_map = {}
            for item in db_resp:
                key_name = f"{item[0]}-{item[1]}"
                if key_name in class_count_map:
                    class_count_map[key_name][item[2]-1] = item[3]
                else:
                    if not self.is_filters_loaded:
                        self.cls_sec_select.addItem(key_name)
                    class_count_map[key_name] = [0]*12
                    class_count_map[key_name][item[2]-1] = item[3]
            self.is_filters_loaded = True

            if self.cls_sec_filter != "All":
                plt.plot(class_count_map[self.cls_sec_filter], marker="o")
                plt.legend([self.cls_sec_filter])
            else:
                for val_ in class_count_map.values():
                    plt.plot(val_, marker="o")
                plt.legend(list(class_count_map.keys()))

            plt.tick_params("both", colors="white", labelsize=12)

            plt.xticks(list(range(len(months_))), months_)
            plt.xlabel(f"Months of {QDate.currentDate().year()}", fontdict={"fontsize": 12, "color": "#ff00f7"})
            plt.tick_params("x", colors="#ff00f7")

            y_axis = list(range(0, 101, 20))
            plt.yticks(y_axis, [f"{item}%" for item in y_axis])
            plt.ylabel(f"Attendance", fontdict={"fontsize": 12, "color": "#00fbff"})
            plt.tick_params("y", colors="#00fbff")

            img_path = os.path.join(os.getenv("TEMP"), f"{uuid4()}.png".replace("-", ""))
            plt.grid(axis="y")
            fig = plt.figure(1)
            fig.set_size_inches(11, 3)
            ax = fig.gca()
            ax.set_facecolor("#262828")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#00fbff")
            ax.spines["left"].set_linewidth(2)
            ax.spines["bottom"].set_color("#ff00f7")
            ax.spines["bottom"].set_linewidth(2)
            plt.savefig(img_path, facecolor="#262828", bbox_inches="tight")
            plt.close("all")
            self.graph_holder.setPixmap(QPixmap(img_path))
            os.remove(img_path)
        except BaseException as e:
            print(e)

class ClassSecCompairGraph(QFrame):
    color_list = None
    months = None
    db_instance = None
    cls_sec_select = None
    heatmap_holder_layout = None
    is_laoding = False
    td1 = None
    worker1 = None

    def __init__(self, db_instance:MsAccessDriver):
        super().__init__()
        self.db_instance = db_instance
        self.color_list = mcolor.ListedColormap([
            "#001f4d", "#003f8c", "#005fbf", "#3399ff", "#99ccff",
            "#ffb366", "#ff944d", "#ff5c33", "#e62e00", "#990000"
        ])
        self.months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

        layout_ = QVBoxLayout(self)

        header_ = QWidget()
        header_layout = QHBoxLayout(header_)
        header_layout.setContentsMargins(0, 0, 0, 0)
        lbl_title = QLabel("<h2>Monthly Attendance Heatmaps</h2>")
        lbl_title.setObjectName("lbl_title")
        header_layout.addWidget(lbl_title)

        self.lbl_perc = QLabel("")
        self.lbl_perc.setStyleSheet("font-size: 14px; color: white;")
        self.lbl_perc.setObjectName("lbl_title")
        header_layout.addWidget(self.lbl_perc, alignment=Qt.AlignCenter)

        cls_sec_group = QGroupBox()
        cls_sec_group.setTitle("class-section")
        cls_sec_select_layout = QHBoxLayout(cls_sec_group)
        cls_sec_select_layout.setContentsMargins(0, 0, 0, 0)
        self.cls_sec_select = cls_sec_select = QComboBox()
        cls_sec_select.setMinimumWidth(100)
        cls_sec_select.setStyleSheet("border: 0;")
        cls_sec_select.currentTextChanged.connect(self.on_cls_sec_filter)
        cls_sec_select_layout.addWidget(cls_sec_select)
        header_layout.addWidget(cls_sec_group, alignment=Qt.AlignRight)
        self.load_class_list()

        layout_.addWidget(header_)

        self.heatmap_holder = QFrame()
        self.heatmap_holder.setObjectName("heatmap_holder")
        self.heatmap_holder_layout = QHBoxLayout(self.heatmap_holder)

        scroll_area = QScrollArea()
        scroll_area.setObjectName("scroll_area")
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.heatmap_holder)
        layout_.addWidget(scroll_area)
        self.on_cls_sec_filter(self.cls_sec_select.currentText())

    def load_class_list(self):
        try:
            self.is_laoding = True
            self.db_instance.cursor.execute("SELECT class, section FROM attendance INNER JOIN students ON attendance.admission_no = students.admission_no GROUP BY class, section")
            for item in self.db_instance.cursor.fetchall():
                self.cls_sec_select.addItem("-".join(item))
            self.is_laoding = False
        except BaseException as e:
            print(e)

    def stop_td1(self):
        try:
            self.worker1 = None
            self.td1.quit()
            self.td1.wait()
            self.td1 = None
        except BaseException as e:
            print(e)

    def on_cls_sec_filter(self, value_):
        if self.is_laoding or not value_:
            return

        self.stop_td1()

        clearLayout(self.heatmap_holder_layout)

        def task_(progress_callback):
            try:
                heat_maps = []
                for x in range(1, 13):
                    if self.worker1 is None:
                        break
                    cls, sec = value_.split("-")
                    heat_maps.append(self.yearly_map_maker(2025, x, cls, sec))
                    if callable(progress_callback):
                        progress_callback(round((x/12)*100, 2))
                return heat_maps
            except BaseException as e:
                print(e)

        def task_resp(resp_body):
            resp_body = resp_body.getResponseBody()
            for item in resp_body:
                map_ = QLabel(self.heatmap_holder)
                map_.setObjectName("map")
                map_.setMaximumWidth(400)
                map_.setMaximumHeight(350)
                map_.setScaledContents(True)
                pm = QPixmap()
                pm.loadFromData(item)
                map_.setPixmap(pm)
                self.heatmap_holder_layout.addWidget(map_)
            self.cls_sec_select.setEnabled(True)
            self.stop_td1()

        def live_progress_reader(prog_):
            self.lbl_perc.setText(f"Loading ({prog_})%")
            if str(prog_).startswith("100"):
                self.lbl_perc.setText("")

        self.cls_sec_select.setEnabled(False)

        self.td1 = QThread(self)
        self.worker1 = UIBlockingTaskRunner(task_)
        self.worker1.moveToThread(self.td1)
        self.td1.started.connect(self.worker1.run)
        self.worker1.task_response.connect(task_resp)
        self.worker1.live_progress.connect(live_progress_reader)
        self.td1.start()

    def yearly_map_maker(self, year, month, cls, sec):
        self.db_instance.cursor.execute("SELECT DAY(mark_date), MONTH(mark_date), ROUND((SUM(IIF(status=?, 1, 0))/count(status)) * 100, 2) FROM attendance INNER JOIN students ON students.admission_no = attendance.admission_no WHERE class=? AND section=? AND MONTH(mark_date)=? GROUP BY MONTH(mark_date), DAY(mark_date)", "P", cls, sec, month)
        db_resp = self.db_instance.cursor.fetchall()

        calendar_arr = self.getCalenderAsArray(year, month)

        attendance_perc = np.zeros(calendar_arr.size)
        for d in db_resp:
            attendance_perc[calendar_arr == d[0]] = d[2]

        calendar_arr = calendar_arr.reshape((5, 7))
        attendance_perc = attendance_perc.reshape((5, 7))

        plt.imshow(attendance_perc, cmap=self.color_list, interpolation='nearest', vmin=0, vmax=100)
        plt.title(f"{self.months[month-1]}, {year}", fontdict={"color": "white", "fontweight": 800})
        cbar = plt.colorbar()
        cbar.set_ticks([-1, 0, 50, 100])
        cbar.set_ticklabels(["", "Low (0%)", "Mid (50%)", "High (100%)"], color="white")
        ax_ = cbar.ax
        pos = ax_.get_position()
        ax_.tick_params(labelsize=9)
        ax_.set_position([pos.x0, pos.y0 + pos.height * 0.25, pos.width, pos.height * 0.5])

        for x in range(calendar_arr.shape[0]):
            for y in range(calendar_arr.shape[1]):
                text_ = str(calendar_arr[x, y])
                plt.text(y, x, "" if text_ == "0" else text_, ha="center", va="center", color="#f0f0f0",
                         fontdict={"fontsize": 14, "fontweight": 700})
        plt.xticks(list(range(0, 7)), ["sun", "mon", "tue", "wed", "thu", "fri", "sat"])
        plt.yticks([], [])
        plt.tick_params("both", colors="white", labelsize=10)

        img_path = os.path.join(os.getenv("TEMP"), f"{uuid4()}.png".replace("-", ""))
        fig1 = plt.figure(1)
        fig1.set_size_inches(5, 4)
        plt.savefig(img_path, facecolor="#1f2121", bbox_inches="tight")
        plt.close("all")

        with open(img_path, "rb") as fp:
            to_ret = fp.read()
        os.remove(img_path)
        return to_ret

    def getCalenderAsArray(self, year, month):
        # returns an 7*5=35 element numpy array which can be reshaped in (5x7) to get calender shape.
        my_cal = calendar.month(year, month)
        my_cal = my_cal.replace("  ", " ")
        parts_ = my_cal.split("\n")[2:]
        new_list = []
        i = 0
        for item in parts_:
            item = item.replace("  ", " ")
            if i == 0:
                for day_ in item.split(" "):
                    new_list.append(int(day_.zfill(2)))
            else:
                item = item.strip(" ").split(" ")
                for day_ in item:
                    new_list.append(int(day_.zfill(2)))
            i += 1
        sample_ = new_list + [0] * (35 - len(new_list))
        sample_ = sample_[:35]
        return np.array(sample_)

class ReportsPage(QFrame):
    def __init__(self, db_instance: MsAccessDriver):
        super().__init__()
        with open("style_sheets/reports_page.css", "r") as fp:
            self.setStyleSheet(fp.read())
        self.setObjectName("report_page_body")

        layout_ = QVBoxLayout(self)

        fig_holder = QWidget(self)
        fig_holder.setObjectName("fig_holder")
        fig_holder_layout = QGridLayout(fig_holder)
        fig_holder_layout.setContentsMargins(0, 0, 5, 0)
        pie_chart = PieChartHolder(db_instance=db_instance)
        pie_chart.setObjectName("pie_chart")
        pie_chart.setMinimumWidth(300)
        pie_chart.setMinimumHeight(320)
        fig_holder_layout.addWidget(pie_chart, 0, 0, 1, 1)

        cwa_trend_graph = ClassWiseAttendanceGraph(db_instance=db_instance)
        cwa_trend_graph.setObjectName("cwa_trend_graph")
        cwa_trend_graph.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        cwa_trend_graph.setMinimumHeight(320)
        fig_holder_layout.addWidget(cwa_trend_graph, 0, 1, 1, 1, Qt.AlignTop)

        self.cs_compair_graphs = cs_compair_graphs = ClassSecCompairGraph(db_instance=db_instance)
        cs_compair_graphs.setObjectName("cs_compair_graphs")
        cs_compair_graphs.setMinimumHeight(400)
        fig_holder_layout.addWidget(cs_compair_graphs, 1, 0, 1, 2, Qt.AlignTop)

        scrollable = QScrollArea(self)
        scrollable.setWidgetResizable(True)
        scrollable.setWidget(fig_holder)

        layout_.addWidget(scrollable)

    def deleteLater(self):
        self.cs_compair_graphs.stop_td1()
        super().deleteLater()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow
    app_ = QApplication([])

    win_ = QMainWindow()
    ele_ = ReportsPage()
    win_.setCentralWidget(ele_)
    win_.show()

    app_.exec()
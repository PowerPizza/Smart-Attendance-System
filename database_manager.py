import os.path
import pyodbc
from app_constants import AppConstant

class MsAccessDriver:
    data_file_path = None
    def __init__(self):
        self.data_file_path = os.path.join(AppConstant.DATA_DIRECTORY, "database.accdb")

        conn_str = (
            r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
            f"DBQ={self.data_file_path};"
        )

        if os.path.exists(self.data_file_path):
            self.db = pyodbc.connect(conn_str)
            self.cursor = self.db.cursor()

        else:
            os.system(f"copy \"empty_db.accdb\" \"{self.data_file_path}\"")
            self.db = pyodbc.connect(conn_str)
            self.cursor = self.db.cursor()

        if "students" not in self.get_table_names():
            self.createStudentsTable()
        if "attendance" not in self.get_table_names():
            self.createAttendanceTable()


    def get_table_names(self):
        self.cursor.tables()
        return [item.table_name for item in self.cursor.tables() if item.table_type == "TABLE"]

    def createStudentsTable(self):
        self.cursor.execute("""CREATE TABLE students (
            admission_no INTEGER PRIMARY KEY,
            student_name TEXT(150),
            father_name TEXT(150),
            mobile_no TEXT(30),
            class TEXT(20),
            section TEXT(20),
            face_encoding_file TEXT(100))
        """)
        self.cursor.commit()

    def createAttendanceTable(self):
        self.cursor.execute("""CREATE TABLE attendance (
            id INTEGER PRIMARY KEY,
            admission_no INTEGER,
            mark_date DATE,
            status TEXT(10),
            CONSTRAINT fk_admission_no FOREIGN KEY (admission_no) REFERENCES students (admission_no))
        """)
        self.cursor.commit()

if __name__ == '__main__':
    db_ = MsAccessDriver()
    print(db_.get_table_names())
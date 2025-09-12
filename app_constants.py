import os

class AppConstant:
    DATA_DIRECTORY = os.path.join(os.getenv("appdata"), "SmartAttendance")
    CLASS_DIRECTORY = os.path.join(DATA_DIRECTORY, "classes")
    STUDENTS_DIRECTORY = os.path.join(DATA_DIRECTORY, "students")
    ENCODINGS_DIRECTORY = os.path.join(DATA_DIRECTORY, "face_encodings")
    STUDENTS_FILE = os.path.join(STUDENTS_DIRECTORY, "students_data.xlsx")

if __name__ == '__main__':
    print(AppConstant.DATA_DIRECTORY)
    print(AppConstant.CLASS_DIRECTORY)

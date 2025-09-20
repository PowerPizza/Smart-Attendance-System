echo off

rmdir /s /q dist
myenv\Scripts\python.exe -m PyInstaller --noconfirm -i "software_icon.ico" main.py --add-data "E:\SCIHACK\PYCHARM PROJECTS\Attendance Software\myenv\Lib\site-packages\face_recognition_models\models;face_recognition_models\models"
xcopy "icons" "dist/main/icons" /E /I
xcopy "style_sheets" "dist/main/style_sheets" /E /I
copy "empty_db.accdb" "dist/main"
copy "software_icon.png" "dist/main"
copy "software_icon.ico" "dist/main"
copy "installer_icon.png" "dist/main"
copy "installer_icon.ico" "dist/main"
echo EXE Created!!! [Press enter to exit...]
pause
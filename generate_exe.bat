echo off

rmdir /s /q dist
myenv\Scripts\python.exe -m PyInstaller --noconfirm main.py --add-data "E:\SCIHACK\PYCHARM PROJECTS\Attendance Software\myenv\Lib\site-packages\face_recognition_models\models;face_recognition_models\models"
xcopy "icons" "dist/main/icons" /E /I
xcopy "style_sheets" "dist/main/style_sheets" /E /I
echo EXE Created!!! [Press enter to exit...]
pause
from openpyxl import Workbook
import openpyxl
import datetime

wb = openpyxl.open("File.xlsx")

ws = wb.active

for item in ws.iter_rows(0, 1, 0, 0):
    for c in item:
        print(c.value, end=" | ")
    print()

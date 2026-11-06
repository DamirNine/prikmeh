@echo off
cd /d "%~dp0"
"C:\Users\terek\AppData\Local\Programs\Python\Python312\python.exe" kompas_animation.py --play
if errorlevel 1 pause

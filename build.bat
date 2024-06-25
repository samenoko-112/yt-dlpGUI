@echo off
call venv\Scripts\activate
nuitka --windows-console-mode=disable --standalone --onefile --output-filename=yt-dlpGUI.exe main.py
pause
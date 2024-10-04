@echo off
nuitka --mingw64 --windows-console-mode=disable --standalone --onefile --output-filename=yt-dlpGUI.exe --nofollow-import-to=yt_dlp.extractor.lazy_extractors --jobs=4 main_re.py
pause
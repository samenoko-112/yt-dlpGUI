@echo off

REM バージョン番号を入力
set /p version="Enter the version number (e.g., 2.3): "

REM LGPLビルドのFFmpegダウンロードURL
set ffmpeg_url=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-lgpl.zip

REM ダウンロード先と展開先の設定
set ffmpeg_zip=ffmpeg.zip
set ffmpeg_dir=ffmpeg

REM FFmpegをダウンロード
echo Downloading FFmpeg...
curl -L "%ffmpeg_url%" -o "%ffmpeg_zip%" || (echo Failed to download FFmpeg && exit /b)

REM FFmpegを展開
echo Extracting FFmpeg...
if exist "%ffmpeg_dir%" rmdir /s /q "%ffmpeg_dir%"
mkdir "%ffmpeg_dir%"
tar -xf "%ffmpeg_zip%" -C "%ffmpeg_dir%" --strip-components=1

if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM flet pack コマンドを実行（バージョン番号を設定）
flet pack main.py --add-data "locale;locale" --product-name "yt-dlpGUI" --name "yt-dlpGUI" --product-version "%version%" --copyright "samenoko-112" --icon .\assets\icon.png

REM issファイルを更新
call :update_iss "%version%" "%cd%\%ffmpeg_dir%"

REM Inno Setupでコンパイル
echo Compiling installer with Inno Setup...
set iss_compiler="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %iss_compiler% (
    echo Inno Setup Compiler not found at %iss_compiler%.
    echo Please install Inno Setup 6 and try again.
    exit /b
)

%iss_compiler% yt-dlp.iss || (echo Failed to compile installer && exit /b)

REM FFmpegフォルダとZIPを削除
echo Cleaning up FFmpeg files...
if exist "%ffmpeg_zip%" del "%ffmpeg_zip%"
if exist "%ffmpeg_dir%" rmdir /s /q "%ffmpeg_dir%"

echo Installer created successfully!
pause
exit /b

:update_iss
REM バージョン番号とFFmpegをissに追加
set iss_file=yt-dlp.iss
set temp_file=%iss_file%.tmp

(for /f "usebackq delims=" %%a in (`type "%iss_file%"`) do (
    echo %%a | findstr /i "AppVersion=" >nul && (
        echo AppVersion=%~1
    ) || echo %%a
)) > "%temp_file%"

REM 元のissファイルを置き換える
move /y "%temp_file%" "%iss_file%" >nul

exit /b

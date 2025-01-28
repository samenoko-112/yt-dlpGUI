[Setup]
AppName=yt-dlpGUI
AppVersion=2.3.5
DefaultDirName={pf}\yt-dlpGUI
DefaultGroupName=yt-dlpGUI
OutputBaseFilename=yt-dlpGUI_Installer
Compression=lzma
SolidCompression=yes
LicenseFile="ffmpeg\LICENSE.txt"
[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
[Files]
Source: "dist\yt-dlpGUI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
Source: "ffmpeg\bin\ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "ffmpeg\bin\ffprobe.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\yt-dlpGUI"; Filename: "{app}\yt-dlpGUI.exe"
Name: "{commondesktop}\yt-dlpGUI"; Filename: "{app}\yt-dlpGUI.exe"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional Icons"; Flags: unchecked
[Run]
Filename: "{app}\yt-dlpGUI.exe"; Description: "Launch yt-dlpGUI"; Flags: nowait postinstall skipifsilent

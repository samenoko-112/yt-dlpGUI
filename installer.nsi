LoadLanguageFile "${NSISDIR}\Contrib\Language files\Japanese.nlf"
Name "yt-dlpGUI" ;
OutFile "yt-dlpGUI_setup.exe" ; 
InstallDir "$PROGRAMFILES\yt-dlpGUI" ;

Section "Install"
    SetOutPath "$INSTDIR" ;
    File "dist\yt-dlpGUI.exe" ;
    CreateShortcut "$DESKTOP\yt-dlpGUI.lnk" "$INSTDIR\yt-dlpGUI.exe" ;
    WriteUninstaller "$INSTDIR\uninstall.exe" ;
    CreateDirectory "$SMPROGRAMS\yt-dlpGUI" ;
    CreateShortcut "$SMPROGRAMS\yt-dlpGUI\yt-dlpGUI.lnk" "$INSTDIR\yt-dlpGUI.exe" ;
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\uninstall.exe" ;
    Delete "$INSTDIR\yt-dlpGUI.exe" ;
    Delete "$DESKTOP\yt-dlpGUI.lnk" ;
    RMDir "$INSTDIR" ;
SectionEnd

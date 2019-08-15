; assroids.nsi
;
; This script is based on example1.nsi, but it remember the directory, 
; has uninstall support and (optionally) installs start menu shortcuts.
;
; It will install example2.nsi into a directory that the user selects,

;--------------------------------

; The name of the installer
Name "assroids installer"

Caption "NSIS Big Test"
Icon "C:\pythonGames\assroids\assroidsIcon.ico"

; The file to write
OutFile "assroids_installer.exe"

; The default installation directory
InstallDir $PROGRAMFILES\assroids

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\NSIS_assroids" "Install_Dir"

; Request application privileges for Windows Vista
RequestExecutionLevel none

;--------------------------------

; Pages

Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

;--------------------------------

; The stuff to install
Section "assroids (required)"

  SectionIn RO
  
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put file there
  File "assroids.exe"
  File "assroids_script.py"
  File "assroidsIcon.ico"
  File "scores.txt"
  File "assroids_NSIS.nsi"
  
  
  CreateDirectory "$INSTDIR\__pycache__"
  SetOutPath $INSTDIR\__pycache__
  File "__pycache__\*"
  
  CreateDirectory "$INSTDIR\music"
  SetOutPath $INSTDIR\music
  File "music\*"
  
  CreateDirectory "$INSTDIR\sounds"
  SetOutPath $INSTDIR\sounds
  File "sounds\*"
  
  CreateDirectory "$INSTDIR\ships"
  SetOutPath $INSTDIR\ships
  File "ships\*"
  
  SetOutPath $INSTDIR 
  
  
  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\NSIS_assroids "Install_Dir" "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\assroids" "DisplayName" "NSIS assroids"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\assroids" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\assroids" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\assroids" "NoRepair" 1
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
SectionEnd

; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"

  CreateShortcut "$SMPROGRAMS\assroids\assriods.lnk" "$INSTDIR\assroids.exe" "" "$INSTDIR\assroidsIcon.ico"
  CreateShortcut "$SMPROGRAMS\assroids\uninstall.lnk" "$INSTDIR\uninstall.exe"
  
SectionEnd

;create a desktop shortcut
Section "Desktop Shortcut"

	SetShellVarContext current
	CreateShortcut "$DESKTOP\assriods.lnk" "$INSTDIR\assroids.exe" "" "$INSTDIR\assroidsIcon.ico"
SectionEnd
;--------------------------------

; Uninstaller

Section "Uninstall"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\assroids"
  DeleteRegKey HKLM SOFTWARE\NSIS_assroids

  ; Remove files and uninstaller
  Delete "$INSTDIR\assroids.exe"
  Delete "$INSTDIR\assroids_NSIS.nsi"
  Delete "$INSTDIR\assroids_script.py"
  Delete "$INSTDIR\assroidsIcon.ico"
  Delete "$INSTDIR\scores.txt"
  Delete "$INSTDIR\__pycache__\*"
  Delete "$INSTDIR\music\*"
  Delete "$INSTDIR\ships\*"
  Delete "$INSTDIR\sounds\*.*"
  Delete "$INSTDIR\uninstall.exe"

  ; Remove directories used
  RMDir "$INSTDIR\__pycache__"
  RMDir "$INSTDIR\music"
  RMDir "$INSTDIR\ships"
  RMDir "$INSTDIR\sounds"
  RMDir "$INSTDIR"
  RMDir /r "$SMPROGRAMS\assroids\assriods.lnk"
  RMDir /r "$SMPROGRAMS\assroids\uninstall.lnk"

SectionEnd

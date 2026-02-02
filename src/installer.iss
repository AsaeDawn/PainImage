[Setup]
AppName=PainImage
AppVersion=0.1.0
DefaultDirName={pf}\PainImage
DefaultGroupName=PainImage
OutputBaseFilename=PainImage-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=src\gui\app.ico

[Files]
Source: "src\dist\PainImage.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\PainImage"; Filename: "{app}\PainImage.exe"
Name: "{commondesktop}\PainImage"; Filename: "{app}\PainImage.exe"

[Run]
Filename: "{app}\PainImage.exe"; Description: "Launch PainImage"; Flags: nowait postinstall

[Setup]
AppName=PainImage
AppVersion=0.1.0
DefaultDirName={pf}\PainImage
DefaultGroupName=PainImage
OutputBaseFilename=PainImage-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=gui\app.ico

[Files]
Source: "dist\PainImage\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PainImage"; Filename: "{app}\PainImage.exe"
Name: "{commondesktop}\PainImage"; Filename: "{app}\PainImage.exe"

[Run]
Filename: "{app}\vc_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "Installing Visual C++ Runtime..."; Flags: waituntilterminated skipifnotexist
Filename: "{app}\PainImage.exe"; Description: "Launch PainImage"; Flags: nowait postinstall

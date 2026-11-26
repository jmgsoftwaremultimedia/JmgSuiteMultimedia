; Jmg SuiteMultimedia - instalador (Inno Setup 6 o 7): Jmg AudioProcesador y Jmg VideoEncoder con un solo FFmpeg
; Lo compila construir_suite.py (construir_suite.bat). Antes hay que construir los programas (lo hace ese mismo script).

#define MyAppName "Jmg SuiteMultimedia"
#define MyAppVersion "1.2.1"
#define AP "Jmg AudioProcesador"
#define VE "Jmg VideoEncoder"
#define MyAppId "4E7B1C2D-9A3F-4B6E-8D1C-5F2A7E9B3C61"

[Setup]
; AppId propio de la suite (no cambiarlo: las versiones nuevas se instalan encima de esta)
AppId={{{#MyAppId}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher=Jmg Software
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany=Jmg Software
VersionInfoDescription=Jmg SuiteMultimedia Setup
DefaultDirName={autopf}\Jmg Software
DefaultGroupName=Jmg Software
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\JmgSuite.ico
SetupIconFile=JmgSuite.ico
LicenseFile=dist\Jmg Software\LICENSE.txt
OutputDir=salida
OutputBaseFilename=JmgSuiteMultimedia_{#MyAppVersion}_setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ChangesAssociations=yes
CloseApplications=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"; LicenseFile: "build\LICENCIA_es.txt"
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
spanish.VerLeeme=Ver el LEEME
english.VerLeeme=View the README (LEEME)
spanish.TipoTodo=Los dos programas (recomendado)
english.TipoTodo=Both programs (recommended)
spanish.TipoElegir=Elegir qué programas instalar
english.TipoElegir=Choose which programs to install
spanish.CompAP=Jmg AudioProcesador 5.1: audio multicanal, normalizar, upmix y Combinar doblajes
english.CompAP=Jmg AudioProcesador 5.1: multichannel audio, normalization, upmix and Combine dubs
spanish.CompVE=Jmg VideoEncoder: comprimir y convertir vídeo (H.264, H.265, AV1...), con su audio y subtítulos
english.CompVE=Jmg VideoEncoder: compress and convert video (H.264, H.265, AV1...), with its audio and subtitles
spanish.Ninguno=Elige al menos uno de los dos programas.
english.Ninguno=Choose at least one of the two programs.
spanish.Suelto=%1 está instalado por separado.%n%nAhora va dentro de Jmg SuiteMultimedia. ¿Quitar la instalación anterior? (tus ajustes se conservan)
spanish.DesTit=Desinstalar Jmg SuiteMultimedia
english.DesTit=Uninstall Jmg SuiteMultimedia
spanish.DesQue=¿Qué programas quieres desinstalar?
english.DesQue=Which programs do you want to uninstall?
spanish.DesNota=El que quede sigue funcionando, con el FFmpeg común. Tus ajustes se conservan.
english.DesNota=The one that stays keeps working, with the shared FFmpeg. Your settings are kept.
spanish.DesBoton=Desinstalar
english.DesBoton=Uninstall
spanish.DesCancelar=Cancelar
english.DesCancelar=Cancel
spanish.DesAbierto=%1 está abierto. Ciérralo y vuelve a desinstalar.
english.DesAbierto=%1 is open. Close it and uninstall again.
spanish.DesHecho=%1 se ha desinstalado.%n%n%2 sigue instalado.
english.DesHecho=%1 has been uninstalled.%n%n%2 is still installed.
spanish.MenuExtraer=Extraer con Jmg VideoEncoder
english.MenuExtraer=Extract with Jmg VideoEncoder
spanish.MenuRipear=Ripear con Jmg VideoEncoder
english.MenuRipear=Rip with Jmg VideoEncoder
spanish.MenuImagen=Crear imagen ISO con Jmg VideoEncoder
english.MenuImagen=Create ISO image with Jmg VideoEncoder
english.Suelto=%1 is installed separately.%n%nIt now comes inside Jmg SuiteMultimedia. Remove the previous installation? (your settings are kept)

[Types]
Name: "todo"; Description: "{cm:TipoTodo}"
Name: "elegir"; Description: "{cm:TipoElegir}"; Flags: iscustom

[Components]
Name: "ap"; Description: "{cm:CompAP}"; Types: todo
Name: "ve"; Description: "{cm:CompVE}"; Types: todo

[Tasks]
; (JMG, 13-11) un solo icono en el escritorio, el de la suite: al abrirlo se elige el programa
Name: "escsuite"; Description: "{cm:CreateDesktopIcon}: {#MyAppName}"; GroupDescription: "{cm:AdditionalIcons}"

[InstallDelete]
; (JMG, 13-11) los iconos de escritorio de cada programa que ponían las versiones de antes
Type: files; Name: "{autodesktop}\{#AP} 5.1.lnk"
Type: files; Name: "{autodesktop}\{#VE}.lnk"

[Files]
; FFmpeg una sola vez, para los dos (bin común)
Source: "dist\Jmg Software\bin\*"; DestDir: "{app}\bin"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\Jmg Software\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Jmg Software\LEEME.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "JmgSuite.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Jmg Software\{#MyAppName}\*"; DestDir: "{app}\{#MyAppName}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\Jmg Software\{#AP}\*"; DestDir: "{app}\{#AP}"; Components: ap; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\Jmg Software\{#VE}\*"; DestDir: "{app}\{#VE}"; Components: ve; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppName}\{#MyAppName}.exe"
Name: "{group}\{#AP} 5.1"; Filename: "{app}\{#AP}\{#AP}.exe"; Components: ap
Name: "{group}\{#VE}"; Filename: "{app}\{#VE}\{#VE}.exe"; Components: ve
Name: "{group}\LEEME"; Filename: "{app}\LEEME.txt"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppName}\{#MyAppName}.exe"; Tasks: escsuite

[Registry]
; «Abrir con»: cada programa aparece en el menú «Abrir con» de sus tipos de archivo (no cambia el programa predeterminado)
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "Jmg AudioProcesador 5.1"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\DefaultIcon"; ValueType: string; ValueData: "{app}\Jmg AudioProcesador\Jmg AudioProcesador.exe,0"; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\shell\open\command"; ValueType: string; ValueData: """{app}\Jmg AudioProcesador\Jmg AudioProcesador.exe"" ""%1"""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".mkv"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".mka"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".mk3d"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".mp4"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".m4a"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".m4v"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".mov"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".avi"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".ts"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".m2ts"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".mts"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".vob"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".webm"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".wav"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".w64"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".flac"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".ac3"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".eac3"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".ec3"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".dts"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".thd"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".truehd"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".mlp"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".aac"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".mp3"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".ogg"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".opus"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg AudioProcesador.exe\SupportedTypes"; ValueType: string; ValueName: ".wma"; ValueData: ""; Components: ap
Root: HKA; Subkey: "Software\Classes\.mkv\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.mka\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.mk3d\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.mp4\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.m4a\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.m4v\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.mov\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.avi\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.ts\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.m2ts\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.mts\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.vob\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.webm\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.wav\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.w64\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.flac\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.ac3\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.eac3\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.ec3\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.dts\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.thd\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.truehd\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.mlp\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.aac\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.mp3\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.ogg\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.opus\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\.wma\OpenWithList\Jmg AudioProcesador.exe"; Flags: uninsdeletekey; Components: ap
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "Jmg VideoEncoder"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\DefaultIcon"; ValueType: string; ValueData: "{app}\Jmg VideoEncoder\Jmg VideoEncoder.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\shell\open\command"; ValueType: string; ValueData: """{app}\Jmg VideoEncoder\Jmg VideoEncoder.exe"" ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\SupportedTypes"; ValueType: string; ValueName: ".mkv"; ValueData: ""; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\SupportedTypes"; ValueType: string; ValueName: ".mk3d"; ValueData: ""; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\SupportedTypes"; ValueType: string; ValueName: ".mp4"; ValueData: ""; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\SupportedTypes"; ValueType: string; ValueName: ".m4v"; ValueData: ""; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\SupportedTypes"; ValueType: string; ValueName: ".mov"; ValueData: ""; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\SupportedTypes"; ValueType: string; ValueName: ".avi"; ValueData: ""; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\SupportedTypes"; ValueType: string; ValueName: ".ts"; ValueData: ""; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\SupportedTypes"; ValueType: string; ValueName: ".m2ts"; ValueData: ""; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\SupportedTypes"; ValueType: string; ValueName: ".mts"; ValueData: ""; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\SupportedTypes"; ValueType: string; ValueName: ".vob"; ValueData: ""; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\SupportedTypes"; ValueType: string; ValueName: ".webm"; ValueData: ""; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\SupportedTypes"; ValueType: string; ValueName: ".mpg"; ValueData: ""; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\SupportedTypes"; ValueType: string; ValueName: ".mpeg"; ValueData: ""; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\SupportedTypes"; ValueType: string; ValueName: ".wmv"; ValueData: ""; Components: ve
Root: HKA; Subkey: "Software\Classes\Applications\Jmg VideoEncoder.exe\SupportedTypes"; ValueType: string; ValueName: ".flv"; ValueData: ""; Components: ve
Root: HKA; Subkey: "Software\Classes\.mkv\OpenWithList\Jmg VideoEncoder.exe"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\.mk3d\OpenWithList\Jmg VideoEncoder.exe"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\.mp4\OpenWithList\Jmg VideoEncoder.exe"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\.m4v\OpenWithList\Jmg VideoEncoder.exe"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\.mov\OpenWithList\Jmg VideoEncoder.exe"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\.avi\OpenWithList\Jmg VideoEncoder.exe"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\.ts\OpenWithList\Jmg VideoEncoder.exe"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\.m2ts\OpenWithList\Jmg VideoEncoder.exe"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\.mts\OpenWithList\Jmg VideoEncoder.exe"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\.vob\OpenWithList\Jmg VideoEncoder.exe"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\.webm\OpenWithList\Jmg VideoEncoder.exe"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\.mpg\OpenWithList\Jmg VideoEncoder.exe"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\.mpeg\OpenWithList\Jmg VideoEncoder.exe"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\.wmv\OpenWithList\Jmg VideoEncoder.exe"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\.flv\OpenWithList\Jmg VideoEncoder.exe"; Flags: uninsdeletekey; Components: ve
; (JMG, 15-11) botón derecho en los archivos de vídeo: «Extraer con Jmg VideoEncoder» (la Extracción de ese vídeo)
; (revisión, 17-11) su clave «shell», fuera si queda vacía al desinstalar
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mkv\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mk3d\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mp4\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.m4v\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mov\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.avi\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.ts\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.m2ts\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mts\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.vob\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.webm\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mpg\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mpeg\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.wmv\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.flv\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mkv\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuExtraer}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mkv\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mkv\shell\JmgVideoEncoderExtraer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --extraer ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mk3d\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuExtraer}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mk3d\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mk3d\shell\JmgVideoEncoderExtraer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --extraer ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mp4\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuExtraer}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mp4\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mp4\shell\JmgVideoEncoderExtraer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --extraer ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.m4v\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuExtraer}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.m4v\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.m4v\shell\JmgVideoEncoderExtraer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --extraer ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mov\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuExtraer}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mov\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mov\shell\JmgVideoEncoderExtraer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --extraer ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.avi\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuExtraer}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.avi\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.avi\shell\JmgVideoEncoderExtraer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --extraer ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.ts\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuExtraer}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.ts\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.ts\shell\JmgVideoEncoderExtraer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --extraer ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.m2ts\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuExtraer}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.m2ts\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.m2ts\shell\JmgVideoEncoderExtraer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --extraer ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mts\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuExtraer}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mts\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mts\shell\JmgVideoEncoderExtraer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --extraer ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.vob\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuExtraer}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.vob\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.vob\shell\JmgVideoEncoderExtraer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --extraer ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.webm\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuExtraer}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.webm\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.webm\shell\JmgVideoEncoderExtraer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --extraer ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mpg\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuExtraer}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mpg\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mpg\shell\JmgVideoEncoderExtraer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --extraer ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mpeg\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuExtraer}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mpeg\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.mpeg\shell\JmgVideoEncoderExtraer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --extraer ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.wmv\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuExtraer}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.wmv\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.wmv\shell\JmgVideoEncoderExtraer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --extraer ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.flv\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuExtraer}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.flv\shell\JmgVideoEncoderExtraer"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.flv\shell\JmgVideoEncoderExtraer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --extraer ""%1"""; Components: ve
; (JMG, 16-11) botón derecho en el lector con un DVD o un Blu-ray de vídeo: «Ripear» y «Crear imagen ISO»
Root: HKA; Subkey: "Software\Classes\DVD"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\DVD\shell"; Flags: uninsdeletekeyifempty; Components: ve
Root: HKA; Subkey: "Software\Classes\DVD\shell\JmgVideoEncoderRipear"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuRipear}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\DVD\shell\JmgVideoEncoderRipear"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\DVD\shell\JmgVideoEncoderRipear\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --ripear ""%1"""; Components: ve
Root: HKA; Subkey: "Software\Classes\DVD\shell\JmgVideoEncoderImagen"; ValueType: string; ValueName: ""; ValueData: "{cm:MenuImagen}"; Flags: uninsdeletekey; Components: ve
Root: HKA; Subkey: "Software\Classes\DVD\shell\JmgVideoEncoderImagen"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\{#VE}\{#VE}.exe,0"; Components: ve
Root: HKA; Subkey: "Software\Classes\DVD\shell\JmgVideoEncoderImagen\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#VE}\{#VE}.exe"" --imagen ""%1"""; Components: ve

[Run]
Filename: "{app}\{#MyAppName}\{#MyAppName}.exe"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
; (JMG, 16-11) al terminar, «Ver el LEEME», desmarcada
Filename: "{app}\LEEME.txt"; Description: "{cm:VerLeeme}"; Flags: postinstall shellexec skipifsilent unchecked nowait

[Code]
{ las instalaciones sueltas de antes (cada programa con su propio FFmpeg): se ofrece quitarlas para que no queden repetidas }
procedure QuitarSuelto(const Id, Nombre: String);
var S: String; R: Integer;
begin
  if not RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\' + Id + '_is1', 'UninstallString', S) then
    if not RegQueryStringValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\' + Id + '_is1', 'UninstallString', S) then exit;
  if SuppressibleMsgBox(FmtMessage(CustomMessage('Suelto'), [Nombre]), mbConfirmation, MB_YESNO, IDYES) = IDYES then
    Exec(RemoveQuotes(S), '/VERYSILENT /NORESTART /SUPPRESSMSGBOXES', '', SW_HIDE, ewWaitUntilTerminated, R);
end;

function InitializeSetup(): Boolean;
begin
  QuitarSuelto('{8F3C2A51-6B7D-4E2A-9C1E-5A4D3B2F1E60}', 'Jmg AudioProcesador 5.1');
  QuitarSuelto('{A9B82996-493D-46C1-A467-E41998E78950}', 'Jmg VideoEncoder');
  Result := True;
end;

{ ---------- desinstalar: los dos o solo uno (JMG, 8-11) ---------- }
const
  EXT_AP = '.mkv .mka .mk3d .mp4 .m4a .m4v .mov .avi .ts .m2ts .mts .vob .webm .wav .w64 .flac .ac3 .eac3 .ec3 .dts .thd .truehd .mlp .aac .mp3 .ogg .opus .wma';
  EXT_VE = '.mkv .mk3d .mp4 .m4v .mov .avi .ts .m2ts .mts .vob .webm .mpg .mpeg .wmv .flv';

function ClaveDesinstalar(): String;
begin
  Result := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{' + '{#MyAppId}' + '}_is1';
end;

{ quita un programa y deja el otro: su carpeta, sus accesos directos, su «Abrir con» y lo apuntado de la instalación }
function QuitarUno(const Comp, Nom, Icono, Exts, Queda, NomQueda: String): Boolean;
var Dir, E, R: String; P: Integer;
begin
  Result := False;
  Dir := ExpandConstant('{app}\') + Nom;
  if FileExists(Dir + '\' + Nom + '.exe') and not DeleteFile(Dir + '\' + Nom + '.exe') then
  begin
    SuppressibleMsgBox(FmtMessage(CustomMessage('DesAbierto'), [Nom]), mbError, MB_OK, IDOK);
    exit;
  end;
  DelTree(Dir, True, True, True);
  DeleteFile(ExpandConstant('{group}\') + Icono + '.lnk');
  DeleteFile(ExpandConstant('{commondesktop}\') + Icono + '.lnk');
  DeleteFile(ExpandConstant('{userdesktop}\') + Icono + '.lnk');
  RegDeleteKeyIncludingSubkeys(HKA, 'Software\Classes\Applications\' + Nom + '.exe');
  R := Exts + ' ';
  while Length(R) > 1 do
  begin
    P := Pos(' ', R); E := Copy(R, 1, P - 1); R := Copy(R, P + 1, Length(R));
    if E <> '' then RegDeleteKeyIncludingSubkeys(HKA, 'Software\Classes\' + E + '\OpenWithList\' + Nom + '.exe');
    if (E <> '') and (Comp = 've') then
    begin
      RegDeleteKeyIncludingSubkeys(HKA, 'Software\Classes\SystemFileAssociations\' + E + '\shell\JmgVideoEncoderExtraer');   { (JMG, 15-11) su «Extraer» }
      RegDeleteKeyIfEmpty(HKA, 'Software\Classes\SystemFileAssociations\' + E + '\shell');
    end;
  end;
  if Comp = 've' then   { (JMG, 16-11) su «Ripear» y «Crear imagen ISO» del lector }
  begin
    RegDeleteKeyIncludingSubkeys(HKA, 'Software\Classes\DVD\shell\JmgVideoEncoderRipear');
    RegDeleteKeyIncludingSubkeys(HKA, 'Software\Classes\DVD\shell\JmgVideoEncoderImagen');
    RegDeleteKeyIfEmpty(HKA, 'Software\Classes\DVD\shell');
    RegDeleteKeyIfEmpty(HKA, 'Software\Classes\DVD');
  end;
  RegWriteStringValue(HKA, ClaveDesinstalar(), 'Inno Setup: Selected Components', Queda);
  RegWriteStringValue(HKA, ClaveDesinstalar(), 'Inno Setup: Deselected Components', Comp);
  RegWriteStringValue(HKA, ClaveDesinstalar(), 'Inno Setup: Setup Type', 'elegir');
  SuppressibleMsgBox(FmtMessage(CustomMessage('DesHecho'), [Nom, NomQueda]), mbInformation, MB_OK, IDOK);
  Result := True;
end;

function InitializeUninstall(): Boolean;
var F: TSetupForm; L, N: TNewStaticText; CA, CV: TNewCheckBox; BOk, BCan: TNewButton; Q: String;
begin
  Result := True;
  if not (FileExists(ExpandConstant('{app}\{#AP}\{#AP}.exe')) and FileExists(ExpandConstant('{app}\{#VE}\{#VE}.exe'))) then exit;
  Q := ExpandConstant('{param:QUITAR|}');   { para pruebas o sin ventana: /QUITAR=ap, /QUITAR=ve o /QUITAR=todo }
  if (Q = '') and UninstallSilent then exit;
  if Q = '' then
  begin
    F := CreateCustomForm(ScaleX(440), ScaleY(190), False, True);
    try
      F.Caption := CustomMessage('DesTit');
      L := TNewStaticText.Create(F); L.Parent := F; L.Left := ScaleX(18); L.Top := ScaleY(16); L.Caption := CustomMessage('DesQue'); L.Font.Style := [fsBold];
      CA := TNewCheckBox.Create(F); CA.Parent := F; CA.Left := ScaleX(18); CA.Top := ScaleY(46); CA.Width := ScaleX(400); CA.Height := ScaleY(20); CA.Caption := '{#AP} 5.1'; CA.Checked := True;
      CV := TNewCheckBox.Create(F); CV.Parent := F; CV.Left := ScaleX(18); CV.Top := ScaleY(72); CV.Width := ScaleX(400); CV.Height := ScaleY(20); CV.Caption := '{#VE}'; CV.Checked := True;
      N := TNewStaticText.Create(F); N.Parent := F; N.Left := ScaleX(18); N.Top := ScaleY(104); N.Width := ScaleX(404); N.WordWrap := True; N.Caption := CustomMessage('DesNota');
      BOk := TNewButton.Create(F); BOk.Parent := F; BOk.Caption := CustomMessage('DesBoton'); BOk.Width := ScaleX(110); BOk.Height := ScaleY(26);
      BOk.Left := F.ClientWidth - ScaleX(244); BOk.Top := F.ClientHeight - ScaleY(42); BOk.ModalResult := mrOk; BOk.Default := True;
      BCan := TNewButton.Create(F); BCan.Parent := F; BCan.Caption := CustomMessage('DesCancelar'); BCan.Width := ScaleX(110); BCan.Height := ScaleY(26);
      BCan.Left := F.ClientWidth - ScaleX(126); BCan.Top := F.ClientHeight - ScaleY(42); BCan.ModalResult := mrCancel; BCan.Cancel := True;
      F.ActiveControl := BOk;
      if F.ShowModal() <> mrOk then begin Result := False; exit; end;
      if CA.Checked and CV.Checked then Q := 'todo'
      else if CA.Checked then Q := 'ap'
      else if CV.Checked then Q := 've'
      else begin Result := False; exit; end;
    finally
      F.Free();
    end;
  end;
  if Q = 'ap' then Result := not QuitarUno('ap', '{#AP}', '{#AP} 5.1', EXT_AP, 've', '{#VE}')
  else if Q = 've' then Result := not QuitarUno('ve', '{#VE}', '{#VE}', EXT_VE, 'ap', '{#AP} 5.1');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if (CurPageID = wpSelectComponents) and not (WizardIsComponentSelected('ap') or WizardIsComponentSelected('ve')) then
  begin
    MsgBox(CustomMessage('Ninguno'), mbError, MB_OK);
    Result := False;
  end;
end;

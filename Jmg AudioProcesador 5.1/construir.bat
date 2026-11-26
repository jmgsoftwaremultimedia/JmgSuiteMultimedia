@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
set "APP=Jmg AudioProcesador"
set "VER=1.6.1"
echo.
echo  ==============================================================
echo    %APP% %VER%  -  crear instalador y version portable
echo  ==============================================================
echo.

rem ---- comprobaciones ----
set "PY=python"
where py >nul 2>nul && set "PY=py -3"
%PY% --version >nul 2>nul || (echo [ERROR] No se encuentra Python. & goto :fallo)
if not exist "main.pyw" (echo [ERROR] Falta main.pyw en esta carpeta. & goto :fallo)
if not exist "AudioProcesador.ico" (echo [ERROR] Falta AudioProcesador.ico en esta carpeta. & goto :fallo)
if not exist "bin\ffmpeg.exe" (echo [ERROR] Falta bin\ffmpeg.exe & goto :fallo)
if not exist "bin\ffprobe.exe" (echo [ERROR] Falta bin\ffprobe.exe & goto :fallo)
if not exist "bin\ffplay.exe" (echo [ERROR] Falta bin\ffplay.exe ^(para revisar la sincronizacion^) & goto :fallo)
if not exist "bin\LICENSE.txt" (echo [ERROR] Falta bin\LICENSE.txt ^(licencia GPL v3^) & goto :fallo)

echo [1/5] Instalando / actualizando PyInstaller y tkinterdnd2...
%PY% -m pip install --upgrade --quiet pyinstaller tkinterdnd2 || goto :fallo

echo [2/5] Creando el ejecutable (tarda un par de minutos)...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
%PY% -m PyInstaller --noconfirm --clean --windowed --onedir --name "%APP%" ^
  --icon "AudioProcesador.ico" --add-data "AudioProcesador.ico;." ^
  --collect-all tkinterdnd2 --version-file "version_info.txt" ^
  "main.pyw" || goto :fallo

echo [3/5] Copiando FFmpeg, licencias y LEEME...
xcopy /e /i /y /q "bin" "dist\%APP%\bin" >nul || goto :fallo
copy /y "bin\LICENSE.txt" "dist\%APP%\LICENSE.txt" >nul
if exist "LEEME.txt" copy /y "LEEME.txt" "dist\%APP%\LEEME.txt" >nul
if exist "presets" xcopy /e /i /y /q "presets" "dist\%APP%\presets" >nul

echo [4/5] Creando la version portable (.zip)...
if not exist "salida" mkdir "salida"
if exist "salida\JmgAudioProcesador_%VER%_portable.zip" del /q "salida\JmgAudioProcesador_%VER%_portable.zip"
powershell -NoProfile -Command "Compress-Archive -Path 'dist\%APP%' -DestinationPath 'salida\JmgAudioProcesador_%VER%_portable.zip' -Force" || goto :fallo

echo [5/5] Creando el instalador con Inno Setup...
set "ISCC="
for %%V in (6 7) do (
  if exist "%ProgramFiles(x86)%\Inno Setup %%V\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup %%V\ISCC.exe"
  if exist "%ProgramFiles%\Inno Setup %%V\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup %%V\ISCC.exe"
  if exist "%LocalAppData%\Programs\Inno Setup %%V\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup %%V\ISCC.exe"
)
if not defined ISCC for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do set "ISCC=%%I"
if not defined ISCC (
  echo [AVISO] No se encuentra Inno Setup ^(6 o 7^). El portable ya esta hecho; para el instalador
  echo         abre instalador.iss con Inno Setup y pulsa Compile.
  goto :fin
)
echo         usando "%ISCC%"
"%ISCC%" /Q "instalador.iss" || goto :fallo

:fin
echo.
echo  LISTO. Mira la carpeta "salida":
echo    - JmgAudioProcesador_%VER%_setup.exe     (instalador)
echo    - JmgAudioProcesador_%VER%_portable.zip  (portable)
echo.
start "" "salida"
pause
exit /b 0

:fallo
echo.
echo  [ERROR] Algo ha fallado. Lee los mensajes de arriba.
echo.
pause
exit /b 1

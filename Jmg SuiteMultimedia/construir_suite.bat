@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
echo.
echo  ==============================================================
echo    Jmg SuiteMultimedia  -  instalador, portable y paquetes de Linux
echo  ==============================================================
echo.
set "PY=python"
where py >nul 2>nul && set "PY=py -3"
%PY% --version >nul 2>nul || (echo [ERROR] No se encuentra Python. & goto :fallo)
%PY% construir_suite.py || goto :fallo
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

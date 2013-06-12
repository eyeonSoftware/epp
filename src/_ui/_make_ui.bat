REM @echo off
pushd %~dp0
pyside-uic.exe %1 -o ..\epp\ui\%~n1_ui.py

PAUSE

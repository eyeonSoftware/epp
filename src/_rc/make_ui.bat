REM @echo off
pushd %~dp0
C:\Python\27\Lib\site-packages\PySide\pyside-rcc %1 -o ..\epp\ui\%~n1_rc.py

PAUSE

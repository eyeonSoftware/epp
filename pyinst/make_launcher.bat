@echo off

pushd %~dp0
call ..\setenv.bat

rmdir /S /Q dist\epp_launcher
python %PYINSTALLER% epp_launcher.spec

popd
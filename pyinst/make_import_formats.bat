@echo off

pushd %~dp0
call ..\setenv.bat

rmdir /S /Q dist\epp_import_formats
python %PYINSTALLER% epp_import_formats.spec

popd
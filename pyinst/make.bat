@echo off

pushd %~dp0

call make_import_formats.bat
call make_launcher.bat
call combine.bat

popd
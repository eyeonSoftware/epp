@echo off

pushd %~dp0

rmdir /S /Q dist\epp\
xcopy /E /Y dist\epp_launcher dist\epp\
xcopy /E /Y dist\epp_import_formats dist\epp\
xcopy /E /Y _contrib dist\epp\
copy /Y ..\src\epp\bin\epp_install_menu.eyeonscript dist\epp\

md dist\epp\_scripts
md dist\epp\_templates

xcopy /E /Y "..\src\epp\_scripts" "dist\epp\_scripts\"
xcopy /E /Y "..\src\epp\_templates" "dist\epp\_templates\"

REM pushd dist
REM del epp.zip
REM %SEVENZIP% a epp.zip epp
REM popd

popd

@echo off

pushd %~dp0

call version_04_build_up.bat

call setenv.bat

call pyinst\make.bat

call innosetup\make.bat

popd

PAUSE
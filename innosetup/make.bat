@echo off
pushd %~dp0

call ..\setenv.bat

pushd %~dp0

%INNOSETUP% /cc epp_setup.iss

popd
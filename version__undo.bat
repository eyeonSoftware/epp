@echo off
pushd %~dp0

copy /Y __INFO__.py.bak src\epp\__INFO__.py

popd

PAUSE
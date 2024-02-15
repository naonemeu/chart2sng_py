@echo off
for /R %%f in ("*.chart") do (chart2sng.py "%%~f" )
pause
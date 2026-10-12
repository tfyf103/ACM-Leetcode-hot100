@echo off
setlocal
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
set "START_EXIT=%ERRORLEVEL%"
if not "%START_EXIT%"=="0" if not defined ACM_NO_PAUSE pause
exit /b %START_EXIT%

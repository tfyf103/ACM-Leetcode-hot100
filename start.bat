@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\start_windows.ps1" %*
set "ACM_EXIT_CODE=%errorlevel%"
if not "%ACM_EXIT_CODE%"=="0" pause
exit /b %ACM_EXIT_CODE%

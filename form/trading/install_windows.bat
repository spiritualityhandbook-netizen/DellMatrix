@echo off
REM Sister Dell Matrix trading — Windows bootstrap
set OWNER=Sister
if not "%~1"=="" set OWNER=%~1

echo === Dell Matrix Trading Setup for %OWNER% ===
where python >nul 2>&1
if errorlevel 1 (
  echo Python not found. Install Python 3 and check Add to PATH.
  pause
  exit /b 1
)

cd /d %~dp0\..\..
echo Working dir: %CD%

python -m form.give_blank --owner %OWNER% --empty
python -m form.trading.cli --owner %OWNER% daily
python -m form.trading.cli --owner %OWNER% status

echo.
echo Next: open PowerShell and run scheduled task register if desired:
echo   powershell -ExecutionPolicy Bypass -File form\trading\windows_register_task.ps1 -Owner %OWNER%
echo.
echo Daily command:
echo   python -m form.trading.cli --owner %OWNER% daily
echo.
echo NOT FINANCIAL ADVICE. Paper trading only until live is wired.
pause

@echo off
title DellMatrix
cd /d "%~dp0"
echo.
echo  DellMatrix — ready for anyone
echo  Offline. Type help for examples, or:
echo  create an idea called test
echo.
python -m form.repl --owner Operator
if errorlevel 1 (
  echo.
  echo  Python could not start.
  echo  Install Python 3 from python.org and check "Add to PATH".
  echo  See docs\INSTALL.md
  pause
)

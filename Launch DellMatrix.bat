@echo off
title DellMatrix
cd /d "%~dp0"
echo.
echo  Starting DellMatrix...
echo  Just talk normally. Type help if you need examples.
echo.
python -m form.repl --owner Ace
if errorlevel 1 (
  echo.
  echo  Python could not start. Make sure Python is installed.
  pause
)

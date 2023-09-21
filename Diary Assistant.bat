@echo off
cd %~dp0
:start
git pull
py "Diary Assistant.py"
pause
goto start
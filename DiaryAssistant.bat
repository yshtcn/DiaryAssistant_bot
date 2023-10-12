@echo off
cd %~dp0
:start
git pull
py DiaryAssistant.py
pause
goto start
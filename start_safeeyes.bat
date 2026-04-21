@echo off
cd /d "%~dp0.."

echo Installing dependencies...
pip install -r safeeyes_windows\requirements.txt

echo Starting SafeEyes...
start pythonw -m safeeyes_windows
exit

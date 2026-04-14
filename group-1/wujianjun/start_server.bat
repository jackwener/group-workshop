@echo off
cd /d "%~dp0\backend"
echo Starting Flask server...
python wsgi.py
pause

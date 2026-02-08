@echo off
echo ========================================
echo  Python Recommendation Engine Startup
echo ========================================
echo.
cd /d %~dp0\python_engine
echo Starting Python Flask Server (Port 5000)...
echo.
python app.py
pause

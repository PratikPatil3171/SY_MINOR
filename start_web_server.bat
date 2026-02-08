@echo off
echo ========================================
echo   Career Advisor - Server Startup
echo ========================================
echo.
echo Starting Node.js Web Server (Port 3000)...
echo.
start cmd /k "cd /d %~dp0 && npm start"
echo.
echo ========================================
echo   IMPORTANT: Start Python Engine Too!
echo ========================================
echo.
echo To start the Python recommendation engine:
echo 1. Open a new terminal
echo 2. Navigate to: python_engine folder
echo 3. Run: python app.py
echo.
echo OR manually run: start_python_engine.bat
echo.
echo ========================================
echo Web server starting...
echo Visit: http://localhost:3000
echo ========================================
pause

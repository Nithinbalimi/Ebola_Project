@echo off
title Ebola Disease Prediction Server
color 0A

echo ========================================================
echo        EBOLA DISEASE PREDICTION SYSTEM
echo   Starting Clean, Error-Free HTTP Development Server
echo ========================================================
echo.

cd /d "n:\movies\ebola_project\Ebola_UI\Ebola_UI\ebola_disease"

echo [INFO] Project directory: %CD%
echo.
echo [INFO] Accessible URLs:
echo        Local PC     : http://127.0.0.1:8000/
echo        Other Devices: http://10.53.255.177:8000/
echo.
echo [INFO] No "Unsafe" certificate warnings! Opens smoothly everywhere.
echo [INFO] Press CTRL+C to stop the server anytime.
echo ========================================================
echo.

start "" cmd /c "timeout /t 5 /nobreak >nul && start http://127.0.0.1:8000/"

python manage.py runserver 0.0.0.0:8000

echo.
echo [INFO] Server stopped.
pause

@echo off
echo ========================================
echo Starting Whistleblowing App
echo ========================================
echo.

:: Start Backend in new window
echo Starting Backend (port 3001)...
start "Backend Server" cmd /k "cd /d %~dp0app\backend && node src/server-simple.js"

:: Wait for backend to start
timeout /t 3 /nobreak > nul

:: Start Frontend in new window
echo Starting Frontend (port 5173)...
start "Frontend Server" cmd /k "cd /d %~dp0app\frontend && npx vite --port 5173"

:: Wait for frontend
timeout /t 3 /nobreak > nul

:: Open browser
echo Opening browser...
start http://localhost:5173

echo.
echo ========================================
echo App Started!
echo ========================================
echo Backend:  http://localhost:3001
echo Frontend: http://localhost:5173
echo.
echo Login Credentials:
echo   Auditor: auditor / changeme123
echo   CEO:     ceo / changeme123
echo.
echo Close both terminal windows to stop.
pause

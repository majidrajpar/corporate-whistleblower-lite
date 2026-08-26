@echo off
REM Quick Start Script for Whistleblowing App (Windows Batch Version)
REM Usage: start-app.bat [setup|docker|help]

setlocal enabledelayedexpansion

if /I "%1"=="help" goto :Help
if /I "%1"=="-h" goto :Help
if /I "%1"=="/?" goto :Help

if /I "%1"=="docker" goto :Docker
if /I "%1"=="setup" goto :Setup

REM Default: Full start
goto :FullStart

:Help
echo Whistleblowing App - Quick Start Script
echo =======================================
echo.
echo Usage: start-app.bat [Option]
echo.
echo Options:
echo   (none)    Full setup and start
echo   setup     Setup only, don't start servers
echo   docker    Start using Docker Compose
echo   help      Show this help message
echo.
echo Examples:
echo   start-app.bat          ^# Full setup and start
echo   start-app.bat setup    ^# Just setup dependencies
echo   start-app.bat docker   ^# Use Docker instead
echo.
goto :End

:Docker
echo Starting with Docker Compose...
cd /d "%~dp0"
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Failed to start Docker containers.
    exit /b 1
)
echo.
echo Docker containers started successfully!
echo.
echo Application is running at:
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:3001
echo.
echo To stop: docker-compose down
goto :End

:Setup
REM Setup only mode
call :SetupBackend
if errorlevel 1 goto :Error

call :SetupFrontend
if errorlevel 1 goto :Error

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Run the following commands to start the app:
echo   Backend:  cd app\backend ^&^& npm run dev
echo   Frontend: cd app\frontend ^&^& npm run dev
echo.
echo Then open: http://localhost:5173
goto :End

:FullStart
REM Full start
call :SetupBackend
if errorlevel 1 goto :Error

call :SetupFrontend
if errorlevel 1 goto :Error

echo.
echo ========================================
echo Starting Application...
echo ========================================
echo.

REM Start backend in background
echo Starting backend server...
start "Backend Server" cmd /k "cd /d %~dp0app\backend ^&^& npm run dev"

REM Wait for backend
echo Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

REM Start frontend
echo Starting frontend server...
start "Frontend Server" cmd /k "cd /d %~dp0app\frontend ^&^& npm run dev"

REM Wait for frontend
timeout /t 5 /nobreak > nul

REM Open browser
echo Opening browser...
start http://localhost:5173

echo.
echo ========================================
echo Application Started!
echo ========================================
echo.
echo Backend:  http://localhost:3001
echo Frontend: http://localhost:5173
echo.
echo Default Login Credentials:
echo   Auditor: username=auditor, password=changeme123
echo   CEO:     username=ceo, password=changeme123
echo.
echo Close the backend and frontend terminal windows to stop.
goto :End

:SetupBackend
echo.
echo Setting up backend...
cd /d "%~dp0app\backend"

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing backend dependencies...
    call npm install
    if errorlevel 1 goto :Error
)

REM Check .env
if not exist ".env" (
    echo Creating .env file...
    copy ".env.example" ".env" > nul
    echo WARNING: Please edit .env and set JWT_SECRET and IP_HASH_PEPPER
)

REM Generate Prisma client
echo Generating Prisma client...
call npx prisma generate
if errorlevel 1 goto :Error

REM Check if database needs migration
if not exist "prisma\dev.db" (
    echo Running database migration...
    call npx prisma migrate dev --name init
    if errorlevel 1 goto :Error
)

REM Seed users
echo Seeding initial users...
node prisma/seed.js

echo Backend setup complete!
exit /b 0

:SetupFrontend
echo.
echo Setting up frontend...
cd /d "%~dp0app\frontend"

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
    if errorlevel 1 goto :Error
)

echo Frontend setup complete!
exit /b 0

:Error
echo.
echo ERROR: Setup failed!
exit /b 1

:End
endlocal

# Quick Start Script for Whistleblowing App
# Run this script to automatically set up and start the application

param(
    [switch]$SetupOnly,
    [switch]$Docker,
    [switch]$Help
)

function Show-Help {
    Write-Host @"
Whistleblowing App - Quick Start Script
========================================

Usage: .\start-app.ps1 [Options]

Options:
    -SetupOnly    Run setup steps only (install deps, create env, init DB)
    -Docker       Start using Docker Compose instead of npm
    -Help         Show this help message

Examples:
    .\start-app.ps1              # Full setup and start
    .\start-app.ps1 -SetupOnly   # Just setup, don't start servers
    .\start-app.ps1 -Docker      # Use Docker instead

"@
    exit 0
}

if ($Help) {
    Show-Help
}

$ErrorActionPreference = "Stop"

# Colors
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"

function Write-Status($Message, $Color = $Green) {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor $Color
}

function Test-Command($Command) {
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Get-ProjectRoot {
    $scriptPath = $PSScriptRoot
    if (-not $scriptPath) {
        $scriptPath = (Get-Location).Path
    }
    return $scriptPath
}

$ProjectRoot = Get-ProjectRoot
$BackendDir = Join-Path $ProjectRoot "app\backend"
$FrontendDir = Join-Path $ProjectRoot "app\frontend"

Write-Status "Starting Whistleblowing App Setup..." $Cyan
Write-Status "Project root: $ProjectRoot"

# Check prerequisites
Write-Status "Checking prerequisites..." $Yellow

if (-not (Test-Command "node")) {
    Write-Status "ERROR: Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/" $Red
    exit 1
}

$nodeVersion = (node --version) -replace 'v',''
Write-Status "Node.js version: $nodeVersion"

if (-not (Test-Command "npm")) {
    Write-Status "ERROR: npm is not installed." $Red
    exit 1
}

if ($Docker) {
    if (-not (Test-Command "docker")) {
        Write-Status "ERROR: Docker is not installed. Please install Docker Desktop." $Red
        exit 1
    }
    if (-not (Test-Command "docker-compose")) {
        Write-Status "WARNING: docker-compose not found. Trying 'docker compose'..." $Yellow
    }
}

# Docker mode
if ($Docker) {
    Write-Status "Starting with Docker Compose..." $Cyan
    Set-Location $ProjectRoot
    
    try {
        docker-compose up -d
        Write-Status "Docker containers started successfully!" $Green
        Write-Status ""
        Write-Status "Application is running at:" $Cyan
        Write-Status "  Frontend: http://localhost:5173" $Green
        Write-Status "  Backend API: http://localhost:3001" $Green
        Write-Status ""
        Write-Status "To stop: docker-compose down" $Yellow
    } catch {
        Write-Status "ERROR: Failed to start Docker containers: $_" $Red
        exit 1
    }
    exit 0
}

# Backend setup
Write-Status "Setting up backend..." $Cyan
Set-Location $BackendDir

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Status "Installing backend dependencies..." $Yellow
    npm install
    Write-Status "Backend dependencies installed." $Green
} else {
    Write-Status "Backend dependencies already installed." $Green
}

# Check .env file
if (-not (Test-Path ".env")) {
    Write-Status "Creating .env file from template..." $Yellow
    Copy-Item ".env.example" ".env"
    
    # Generate random secrets
    $jwtSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object { [char]$_ })
    $pepper = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object { [char]$_ })
    
    # Update .env with generated secrets
    $envContent = Get-Content ".env" -Raw
    $envContent = $envContent -replace 'JWT_SECRET="your-super-secret-jwt-key-change-this-in-production"', "JWT_SECRET=`"$jwtSecret`""
    $envContent = $envContent -replace 'IP_HASH_PEPPER="another-random-string-here"', "IP_HASH_PEPPER=`"$pepper`""
    Set-Content ".env" $envContent -NoNewline
    
    Write-Status ".env file created with auto-generated secrets." $Green
    Write-Status "You can edit .env to customize settings." $Yellow
} else {
    Write-Status ".env file already exists." $Green
}

# Generate Prisma client
Write-Status "Generating Prisma client..." $Yellow
npx prisma generate

# Check if database exists
$dbFile = Join-Path $BackendDir "prisma" "dev.db"
$needsMigration = $true

if (Test-Path $dbFile) {
    Write-Status "Database file found. Checking if migration is needed..." $Yellow
    # Try a simple query to check if tables exist
    try {
        $testResult = node -e @"
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();
prisma.user.count().then(() => {
  console.log('DB_OK');
  process.exit(0);
}).catch(() => {
  console.log('DB_NEEDS_MIGRATION');
  process.exit(0);
});
"@
        if ($testResult -eq "DB_OK") {
            $needsMigration = $false
            Write-Status "Database is ready." $Green
        }
    } catch {
        # If test fails, we need migration
    }
}

if ($needsMigration) {
    Write-Status "Running database migration..." $Yellow
    npx prisma migrate dev --name init
    Write-Status "Database migration complete." $Green
}

# Seed initial users
Write-Status "Seeding initial users..." $Yellow
node prisma/seed.js
Write-Status "Initial users created." $Green

Write-Status "Backend setup complete!" $Green

# Frontend setup
Write-Status "Setting up frontend..." $Cyan
Set-Location $FrontendDir

if (-not (Test-Path "node_modules")) {
    Write-Status "Installing frontend dependencies..." $Yellow
    npm install
    Write-Status "Frontend dependencies installed." $Green
} else {
    Write-Status "Frontend dependencies already installed." $Green
}

Write-Status "Frontend setup complete!" $Green

if ($SetupOnly) {
    Write-Status ""
    Write-Status "Setup complete! Run the following to start the app:" $Cyan
    Write-Status "  Backend:  cd app/backend && npm run dev" $Green
    Write-Status "  Frontend: cd app/frontend && npm run dev" $Green
    Write-Status ""
    Write-Status "Then open: http://localhost:5173" $Green
    exit 0
}

# Start backend in background
Write-Status "Starting backend server..." $Cyan
Set-Location $BackendDir

$backendJob = Start-Job -ScriptBlock {
    param($Dir)
    Set-Location $Dir
    npm run dev
} -ArgumentList $BackendDir

Write-Status "Backend server starting in background (Job ID: $($backendJob.Id))" $Green

# Wait a moment for backend to start
Write-Status "Waiting for backend to initialize..." $Yellow
Start-Sleep -Seconds 5

# Check if backend is running
$backendRunning = $false
$retries = 0
while (-not $backendRunning -and $retries -lt 10) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3001/api/health" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $backendRunning = $true
            Write-Status "Backend is running on http://localhost:3001" $Green
        }
    } catch {
        $retries++
        Write-Status "Backend not ready yet (attempt $retries/10)..." $Yellow
        Start-Sleep -Seconds 2
    }
}

if (-not $backendRunning) {
    Write-Status "WARNING: Could not confirm backend is running. Check logs with: Get-Job $($backendJob.Id) | Receive-Job" $Yellow
}

# Start frontend
Write-Status "Starting frontend server..." $Cyan
Set-Location $FrontendDir

Write-Status ""
Write-Status "========================================" $Cyan
Write-Status "Application Starting!" $Cyan
Write-Status "========================================" $Cyan
Write-Status ""
Write-Status "Backend:  http://localhost:3001" $Green
Write-Status "Frontend: http://localhost:5173" $Green
Write-Status ""
Write-Status "Default Login Credentials:" $Yellow
Write-Status "  Auditor: username=auditor, password=changeme123" $Green
Write-Status "  CEO:     username=ceo, password=changeme123" $Green
Write-Status ""
Write-Status "The frontend will open automatically..." $Cyan
Write-Status ""

# Try to open browser
Start-Process "http://localhost:5173"

# Start frontend (this will block)
npm run dev

# Cleanup on exit
Write-Status ""
Write-Status "Shutting down..." $Yellow
Stop-Job $backendJob
Remove-Job $backendJob
Write-Status "Backend stopped." $Green
Write-Status "Goodbye!" $Green

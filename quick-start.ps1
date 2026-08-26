# Test Start Script - Quick verification of the app setup

$ErrorActionPreference = "Stop"

Write-Host "=== Whistleblowing App - Quick Start ===" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version
Write-Host "  Node.js: $nodeVersion" -ForegroundColor Green

# Backend
Write-Host ""
Write-Host "Setting up backend..." -ForegroundColor Cyan
Set-Location $PSScriptRoot\app\backend

if (-not (Test-Path "node_modules")) {
    Write-Host "  Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Generate Prisma client
Write-Host "  Generating Prisma client..." -ForegroundColor Yellow
npx prisma generate

# Push database schema
Write-Host "  Pushing database schema..." -ForegroundColor Yellow
npx prisma db push

# Seed users
Write-Host "  Seeding users..." -ForegroundColor Yellow
node prisma/seed.js

Write-Host "  Backend ready!" -ForegroundColor Green

# Frontend
Write-Host ""
Write-Host "Setting up frontend..." -ForegroundColor Cyan
Set-Location $PSScriptRoot\app\frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "  Installing dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host "  Frontend ready!" -ForegroundColor Green

# Start both servers
Write-Host ""
Write-Host "=== Starting Servers ===" -ForegroundColor Cyan
Write-Host ""

# Start backend in background
Write-Host "Starting backend on port 3001..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    param($Dir)
    Set-Location $Dir
    npm run dev
} -ArgumentList (Join-Path $PSScriptRoot "app\backend")

Start-Sleep -Seconds 3

# Start frontend (this will block)
Write-Host "Starting frontend on port 5173..." -ForegroundColor Yellow
Write-Host ""
Set-Location $PSScriptRoot\app\frontend
npm run dev

# Cleanup
Write-Host ""
Write-Host "Shutting down..." -ForegroundColor Yellow
Stop-Job $backendJob
Remove-Job $backendJob
Write-Host "Done!" -ForegroundColor Green

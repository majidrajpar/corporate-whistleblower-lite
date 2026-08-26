#!/bin/bash
# Quick Start Script for Whistleblowing App (Linux/Mac Version)
# Usage: ./start-app.sh [setup|docker|help]

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/app/backend"
FRONTEND_DIR="$SCRIPT_DIR/app/frontend"

print_status() {
    echo -e "${2:-$GREEN}[$(date +%H:%M:%S)] $1${NC}"
}

show_help() {
    cat << EOF
Whistleblowing App - Quick Start Script
=======================================

Usage: ./start-app.sh [Option]

Options:
    (none)    Full setup and start
    setup     Setup only, don't start servers
    docker    Start using Docker Compose
    help      Show this help message

Examples:
    ./start-app.sh          # Full setup and start
    ./start-app.sh setup    # Just setup dependencies
    ./start-app.sh docker   # Use Docker instead

EOF
    exit 0
}

check_prerequisites() {
    print_status "Checking prerequisites..." "$YELLOW"
    
    if ! command -v node &> /dev/null; then
        print_status "ERROR: Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/" "$RED"
        exit 1
    fi
    
    NODE_VERSION=$(node --version | sed 's/v//')
    print_status "Node.js version: $NODE_VERSION"
    
    if ! command -v npm &> /dev/null; then
        print_status "ERROR: npm is not installed." "$RED"
        exit 1
    fi
}

setup_backend() {
    print_status "Setting up backend..." "$CYAN"
    cd "$BACKEND_DIR"
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing backend dependencies..." "$YELLOW"
        npm install
    else
        print_status "Backend dependencies already installed." "$GREEN"
    fi
    
    # Create .env if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..." "$YELLOW"
        cp .env.example .env
        
        # Generate random secrets
        JWT_SECRET=$(openssl rand -base64 32)
        PEPPER=$(openssl rand -base64 32)
        
        # Update .env (macOS compatible)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/JWT_SECRET=.*/JWT_SECRET=\"$JWT_SECRET\"/" .env
            sed -i '' "s/IP_HASH_PEPPER=.*/IP_HASH_PEPPER=\"$PEPPER\"/" .env
        else
            sed -i "s/JWT_SECRET=.*/JWT_SECRET=\"$JWT_SECRET\"/" .env
            sed -i "s/IP_HASH_PEPPER=.*/IP_HASH_PEPPER=\"$PEPPER\"/" .env
        fi
        
        print_status ".env file created with auto-generated secrets." "$GREEN"
    fi
    
    # Generate Prisma client
    print_status "Generating Prisma client..." "$YELLOW"
    npx prisma generate
    
    # Run migration if database doesn't exist
    if [ ! -f "prisma/dev.db" ]; then
        print_status "Running database migration..." "$YELLOW"
        npx prisma migrate dev --name init
    fi
    
    # Seed users
    print_status "Seeding initial users..." "$YELLOW"
    node prisma/seed.js
    
    print_status "Backend setup complete!" "$GREEN"
}

setup_frontend() {
    print_status "Setting up frontend..." "$CYAN"
    cd "$FRONTEND_DIR"
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..." "$YELLOW"
        npm install
    else
        print_status "Frontend dependencies already installed." "$GREEN"
    fi
    
    print_status "Frontend setup complete!" "$GREEN"
}

start_servers() {
    print_status "Starting servers..." "$CYAN"
    
    # Start backend in background
    print_status "Starting backend server..." "$YELLOW"
    cd "$BACKEND_DIR"
    npm run dev &
    BACKEND_PID=$!
    
    # Wait for backend
    print_status "Waiting for backend to initialize..." "$YELLOW"
    sleep 5
    
    # Check if backend is running
    if ! curl -s http://localhost:3001/api/health > /dev/null 2>&1; then
        print_status "WARNING: Backend may not be ready yet. Continuing..." "$YELLOW"
    fi
    
    # Start frontend in background
    print_status "Starting frontend server..." "$YELLOW"
    cd "$FRONTEND_DIR"
    npm run dev &
    FRONTEND_PID=$!
    
    # Wait for frontend
    sleep 5
    
    print_status ""
    print_status "========================================" "$CYAN"
    print_status "Application Started!" "$CYAN"
    print_status "========================================" "$CYAN"
    print_status ""
    print_status "Backend:  http://localhost:3001" "$GREEN"
    print_status "Frontend: http://localhost:5173" "$GREEN"
    print_status ""
    print_status "Default Login Credentials:" "$YELLOW"
    print_status "  Auditor: username=auditor, password=changeme123" "$GREEN"
    print_status "  CEO:     username=ceo, password=changeme123" "$GREEN"
    print_status ""
    print_status "Opening browser..." "$CYAN"
    
    # Try to open browser
    if command -v open > /dev/null; then
        open "http://localhost:5173"
    elif command -v xdg-open > /dev/null; then
        xdg-open "http://localhost:5173"
    fi
    
    print_status ""
    print_status "Press Ctrl+C to stop both servers." "$YELLOW"
    
    # Wait for interrupt
    wait
}

docker_mode() {
    print_status "Starting with Docker Compose..." "$CYAN"
    cd "$SCRIPT_DIR"
    
    if ! command -v docker > /dev/null 2>&1; then
        print_status "ERROR: Docker is not installed." "$RED"
        exit 1
    fi
    
    docker-compose up -d
    
    print_status ""
    print_status "Docker containers started successfully!" "$GREEN"
    print_status ""
    print_status "Application is running at:" "$CYAN"
    print_status "  Frontend: http://localhost:5173" "$GREEN"
    print_status "  Backend:  http://localhost:3001" "$GREEN"
    print_status ""
    print_status "To stop: docker-compose down" "$YELLOW"
}

# Main script logic
case "${1:-}" in
    help|--help|-h)
        show_help
        ;;
    docker)
        docker_mode
        ;;
    setup)
        check_prerequisites
        setup_backend
        setup_frontend
        print_status ""
        print_status "========================================" "$CYAN"
        print_status "Setup Complete!" "$CYAN"
        print_status "========================================" "$CYAN"
        print_status ""
        print_status "Run the following commands to start the app:" "$CYAN"
        print_status "  Backend:  cd app/backend && npm run dev" "$GREEN"
        print_status "  Frontend: cd app/frontend && npm run dev" "$GREEN"
        print_status ""
        print_status "Then open: http://localhost:5173" "$GREEN"
        ;;
    *)
        check_prerequisites
        setup_backend
        setup_frontend
        start_servers
        ;;
esac

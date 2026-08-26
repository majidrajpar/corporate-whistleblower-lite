# Quick Start Scripts

One-command scripts to get the whistleblowing app running instantly.

## 🚀 Fastest Way to Start

### Windows (PowerShell)
```powershell
# Full setup + start (opens browser automatically)
.\start-app.ps1

# Or with options:
.\start-app.ps1 -SetupOnly    # Just install deps, don't start
.\start-app.ps1 -Docker       # Use Docker instead
.\start-app.ps1 -Help          # Show help
```

### Windows (Command Prompt)
```cmd
:: Full setup + start
start-app.bat

:: Or with options:
start-app.bat setup    :: Just install deps
start-app.bat docker   :: Use Docker
start-app.bat help     :: Show help
```

### Linux / Mac
```bash
# Make executable (first time only)
chmod +x start-app.sh

# Full setup + start (opens browser automatically)
./start-app.sh

# Or with options:
./start-app.sh setup    # Just install deps
./start-app.sh docker   # Use Docker
./start-app.sh help     # Show help
```

## 📋 What the Scripts Do

1. **Check Prerequisites** - Verify Node.js is installed
2. **Install Dependencies** - Run `npm install` for both backend and frontend
3. **Create .env** - Generate `.env` file with random JWT_SECRET and IP_HASH_PEPPER
4. **Setup Database** - Run Prisma migrations and generate client
5. **Seed Users** - Create default auditor and CEO accounts
6. **Start Servers** - Launch backend (port 3001) and frontend (port 5173)
7. **Open Browser** - Automatically open http://localhost:5173

## 🔑 Default Login Credentials

After running the script, log in with:

| Role | Username | Password |
|------|----------|----------|
| Internal Audit | `auditor` | `changeme123` |
| CEO | `ceo` | `changeme123` |

> **Note:** Change these passwords in your `.env` file before deploying to production!

## 🐳 Docker Alternative

```bash
# Start everything with one command
./start-app.sh docker   # or start-app.bat docker / start-app.ps1 -Docker
```

This uses Docker Compose to run both backend and frontend in containers.

## ⚙️ Manual Setup (If Scripts Fail)

If the scripts don't work, follow these manual steps:

### Backend
```bash
cd app/backend
npm install
cp .env.example .env
# Edit .env with your settings
npx prisma generate
npx prisma migrate dev --name init
node prisma/seed.js
npm run dev
```

### Frontend
```bash
cd app/frontend
npm install
npm run dev
```

Then open: http://localhost:5173

## 🛠️ Prerequisites

- **Node.js 18+** - Download from https://nodejs.org/
- **npm 9+** (comes with Node.js)
- **Docker Desktop** (optional, for Docker mode)

## 📁 Project Structure

```
dilp/
├── start-app.ps1       # PowerShell script (Windows)
├── start-app.bat       # Batch script (Windows)
├── start-app.sh        # Bash script (Linux/Mac)
├── app/
│   ├── backend/        # Node.js + Express + Prisma
│   └── frontend/       # React + Vite
└── ...
```

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Node.js not found" | Install Node.js 18+ from https://nodejs.org/ |
| "npm install fails" | Check internet connection, try `npm cache clean` |
| "Port 3001 in use" | Kill process on port 3001 or change PORT in .env |
| "Port 5173 in use" | Kill process on port 5173 or change vite.config.js |
| "Database locked" | Delete `prisma/dev.db` and rerun |

## 📞 Need Help?

- Check the main README: [../README.md](../README.md)
- Review the setup instructions: [../README.md#quick-start](../README.md#quick-start)
- Report issues in the project repository

---

**Status:** ✅ Ready to run

# KSA Whistleblowing Portal

A lightweight, open-source, self-hosted whistleblowing web application designed for organizations in Saudi Arabia and beyond. Deploy in minutes — not hours.

Employees can report wrongdoing anonymously, and internal audit staff can review, investigate, and escalate reports to executive leadership — all while maintaining complete data privacy and control.

## Features

- **Anonymous Reporting**: Submit reports without any identifying information — no accounts, no IP tracking
- **File Attachments**: Upload evidence (JPG, PNG, PDF up to 5MB) with UUID filenames and EXIF stripping
- **Rate Limiting**: 5 reports per hour per IP to prevent abuse
- **Internal Audit Dashboard**: View all reports, filter by status/category, update status, escalate to CEO
- **CEO Dashboard**: Separate view for escalated reports with summary statistics
- **Audit Trail**: Track who viewed/escalated/resolved reports (reporter remains anonymous)
- **Role-Based Access**: JWT authentication for Internal Audit and CEO roles
- **Security**: Helmet.js, CORS, input validation, file upload security, bcrypt hashing
- **Self-Hosted**: Complete data control — no external APIs or cloud dependencies
- **Data Residency**: All data stored locally on your server

## Why This Project?

Unlike existing solutions ([SecureDrop](https://github.com/freedomofpress/securedrop), [GlobaLeaks](https://github.com/globaleaks/globaleaks-whistleblowing-software)) which are designed for journalists and require complex infrastructure, this project is:

- **Lightweight**: Runs on a single server with SQLite — no separate database server needed
- **Easy to Deploy**: `npm install` and you're running in minutes, not hours
- **Corporate-Focused**: Built for internal organizational use with role-based access (Internal Audit & CEO)
- **Modern Stack**: React 18 + Vite + Express + Prisma (not Python/Django)
- **KSA-Ready**: Designed for Saudi Arabian compliance requirements and data residency

| Feature | SecureDrop | GlobaLeaks | **This Project** |
|---------|------------|------------|------------------|
| Setup Time | Hours | Hours | **Minutes** |
| Database | PostgreSQL | PostgreSQL | **SQLite** |
| Stack | Python/Flask | Python | **Node.js/React** |
| Target Users | Journalists | Media Orgs | **Companies** |
| Deployment | Tor + Servers | Multi-service | **Single Server** |

## Technology Stack

### Backend
- **Node.js** + **Express.js**
- **Prisma ORM** + **SQLite**
- **JWT** authentication
- **Multer** for file uploads
- **Helmet** + **express-rate-limit** for security

### Frontend
- **React 18**
- **Vite** (build tool)
- **React Router** (navigation)
- **CSS Modules** (styling)

## Quick Start

### Prerequisites
- Node.js 18+ (check with `node --version`)
- npm 9+ (check with `npm --version`)

### 1. Clone and Setup

```bash
git clone https://github.com/your-org/ksa-whistleblowing.git
cd ksa-whistleblowing
```

### 2. Backend Setup

```bash
cd app/backend

# Install dependencies
npm install

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Generate Prisma client
npm run db:generate

# Run database migrations
npm run db:migrate

# Seed initial users (from env vars)
npm run db:seed

# Start server
npm run dev
```

The backend will be available at `http://localhost:3001`

### 3. Frontend Setup

```bash
cd app/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 4. Login Credentials

Default users are created from environment variables:
- **Auditor**: Set `INITIAL_AUDITOR_USER` and `INITIAL_AUDITOR_PASS` in `.env`
- **CEO**: Set `INITIAL_CEO_USER` and `INITIAL_CEO_PASS` in `.env`

## Docker Deployment (Optional)

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL="file:./dev.db"

# JWT Secret (minimum 32 characters)
JWT_SECRET="your-super-secret-jwt-key-change-this"

# IP Hash Pepper (for rate limiting)
IP_HASH_PEPPER="another-random-string-here"

# Initial Users
INITIAL_AUDITOR_USER="auditor"
INITIAL_AUDITOR_PASS="changeme123"
INITIAL_CEO_USER="ceo"
INITIAL_CEO_PASS="changeme123"

# Server
PORT=3001
NODE_ENV="production"

# CORS (frontend URL)
CORS_ORIGIN="http://localhost:5173"
```

## Security Considerations

- **Data Residency**: All data is stored locally on your server. No external APIs or cloud storage.
- **Anonymity**: The system does not track IP addresses (only hashes them for rate limiting).
- **File Uploads**: Files are stored with UUID filenames, outside the web root. Only authenticated auditors can download.
- **Authentication**: JWT tokens expire after 1 hour. Login is rate-limited (5 attempts per 15 minutes).
- **Company Responsibility**: The deploying company is responsible for:
  - Hosting and data residency
  - Regular backups
  - Server hardening (firewall, SSL/TLS)
  - Compliance with KSA regulations

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Support

For issues and feature requests, please open an issue on GitHub.

---

**Note**: This application is designed for laptop/desktop use and is optimized for internal organizational use.

# Corporate Whistleblower Lite

A lightweight, open-source, self-hosted whistleblowing web application for organizations of all sizes — companies, NGOs, municipalities, schools, and more. Deploy in minutes — not hours.

Enable anyone to report wrongdoing anonymously, while internal teams review, investigate, and escalate reports — all while maintaining complete data privacy and control.

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
- **Compliance-Ready**: Designed for data residency and privacy requirements worldwide

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

## Project Structure

```
corporate-whistleblower-lite/
├── app/
│   ├── backend/          # Express.js API server
│   │   ├── src/
│   │   │   ├── server.js           # Main server entry
│   │   │   ├── routes/
│   │   │   │   ├── auth.js         # Login / JWT
│   │   │   │   ├── reports.js      # Report CRUD + escalation
│   │   │   │   ├── upload.js       # File upload (Multer)
│   │   │   │   └── audit-log.js    # Audit trail
│   │   │   ├── middleware/
│   │   │   │   └── auth.js         # JWT verification + role checks
│   │   │   └── utils/
│   │   │       └── prisma.js       # Prisma client singleton
│   │   ├── prisma/
│   │   │   ├── schema.prisma       # Database schema
│   │   │   └── seed.js             # Seed initial users
│   │   ├── Dockerfile
│   │   ├── .env.example
│   │   └── package.json
│   └── frontend/         # React + Vite SPA
│       ├── src/
│       │   ├── App.jsx
│       │   ├── main.jsx
│       │   ├── pages/
│       │   │   ├── HomePage.jsx        # Anonymous report form
│       │   │   ├── LoginPage.jsx       # Internal login
│       │   │   ├── DashboardPage.jsx   # Auditor dashboard
│       │   │   └── CEOPage.jsx         # CEO dashboard
│       │   ├── components/
│       │   │   ├── Navbar.jsx
│       │   │   └── ReportForm.jsx
│       │   ├── context/
│       │   │   └── AuthContext.jsx     # Auth state + localStorage
│       │   └── utils/
│       │       └── api.js
│       ├── Dockerfile
│       ├── nginx.conf
│       ├── vite.config.js
│       └── package.json
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Quick Start (Local Development)

### Prerequisites
- **Node.js** 18+ (check with `node --version`)
- **npm** 9+ (check with `npm --version`)
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/majidrajpar/corporate-whistleblower-lite.git
cd corporate-whistleblower-lite
```

### 2. Backend Setup

Open a terminal in `app/backend`:

```bash
cd app/backend

# Install dependencies
npm install

# Create environment file from the example
cp .env.example .env

# IMPORTANT: Edit .env with your own secrets!
# On Windows:  notepad .env
# On macOS/Linux: nano .env
# See "Environment Variables" section below for details.

# Generate the Prisma client
npm run db:generate

# Run database migrations (creates the SQLite database)
npm run db:migrate

# Seed the database with the initial Auditor and CEO users
npm run db:seed

# Start the development server
npm run dev
```

The backend will be available at: **http://localhost:3001**

A quick health check:
```bash
curl http://localhost:3001/api/health
```

### 3. Frontend Setup

Open a **second terminal** in `app/frontend` (keep the backend running):

```bash
cd app/frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

The frontend will be available at: **http://localhost:5173**

### 4. Login and Use the App

Navigate to **http://localhost:5173** in your browser.

| Role | Username | Password |
|------|----------|----------|
| Auditor | `auditor` | Value of `INITIAL_AUDITOR_PASS` in `.env` (default: `changeme123`) |
| CEO | `ceo` | Value of `INITIAL_CEO_PASS` in `.env` (default: `changeme123`) |

**Important:** Change the default passwords in your `.env` file **before** running `npm run db:seed`.
If you already seeded with defaults, change `.env` then delete `app/backend/prisma/dev.db` and re-run `npm run db:generate`, `npm run db:migrate`, and `npm run db:seed`.

### 5. Submit an Anonymous Report

1. On the home page, select a category, enter a description (min 20 characters), and optionally attach a file.
2. Click **Submit Report Anonymously**.
3. Save the receipt code shown — it is your only way to reference the report later.

### 6. Review Reports as Auditor

1. Click **Internal Access** → log in with Auditor credentials.
2. Navigate to the **Dashboard** to view all reports.
3. Click a report to update its status or escalate it to the CEO.

### 7. Review Escalated Reports as CEO

1. Log in with CEO credentials.
2. Navigate to the **CEO Dashboard** to view escalated reports and summary statistics.

---

## Docker Deployment (Production)

For a containerized setup, use the provided `docker-compose.yml`.

### Prerequisites
- **Docker** + **Docker Compose**

### 1. Set Environment Variables

Create a `.env` file in the **project root** (not inside `app/backend`):

```bash
# Required secrets — CHANGE THESE!
JWT_SECRET="your-super-secret-jwt-key-minimum-32-chars-long"
IP_HASH_PEPPER="another-random-string-here"
INITIAL_AUDITOR_USER="auditor"
INITIAL_AUDITOR_PASS="your-strong-password"
INITIAL_CEO_USER="ceo"
INITIAL_CEO_PASS="your-strong-password"
```

### 2. Build and Run

```bash
docker-compose up -d
```

- **Backend**: http://localhost:3001
- **Frontend**: http://localhost:5173
- Data persists in Docker volumes (`backend-data`, `backend-uploads`)

### 3. Stop

```bash
docker-compose down
```

To remove data volumes (⚠️ deletes all reports and uploads):
```bash
docker-compose down -v
```

---

## Environment Variables

### Backend (`app/backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | SQLite path: `file:./prisma/dev.db` |
| `JWT_SECRET` | Yes | Min 32 characters. Generate with `openssl rand -base64 32` |
| `JWT_EXPIRES_IN` | No | Token expiry (default: `1h`) |
| `IP_HASH_PEPPER` | Yes | Random string for IP hashing. Generate with `openssl rand -base64 32` |
| `INITIAL_AUDITOR_USER` | Yes | Default auditor username |
| `INITIAL_AUDITOR_PASS` | Yes | Default auditor password |
| `INITIAL_CEO_USER` | Yes | Default CEO username |
| `INITIAL_CEO_PASS` | Yes | Default CEO password |
| `PORT` | No | Server port (default: `3001`) |
| `NODE_ENV` | No | `development` or `production` |
| `CORS_ORIGIN` | Yes | Frontend URL, e.g. `http://localhost:5173` |
| `UPLOAD_DIR` | No | Upload directory path (default: `./uploads`) |

**⚠️ Security Warning:**
- **Never** commit `.env` to Git (it is already in `.gitignore`).
- Use strong, unique passwords and secrets in production.
- Generate `JWT_SECRET` and `IP_HASH_PEPPER` with `openssl rand -base64 32`.

---

## Troubleshooting

### `Error: Cannot find module '@prisma/client'`
Run `npm run db:generate` in `app/backend`. This generates the Prisma client from the schema.

### `Database does not exist`
The SQLite database file is created by Prisma Migrate. Ensure you run:
```bash
npm run db:migrate
```

### `Users already exist, skipping seed`
If you need to re-seed with new passwords:
1. Delete `app/backend/prisma/dev.db`
2. Delete `app/backend/prisma/migrations/` (if migrations exist)
3. Re-run `npm run db:migrate` and `npm run db:seed`

### `Invalid credentials` after changing `.env`
The database stores hashed passwords at seed time. Changing `.env` after seeding does **not** update existing users. Re-seed the database (see above).

### Frontend shows `Failed to fetch` or CORS errors
- Ensure the backend is running on port `3001`.
- Ensure `CORS_ORIGIN` in `app/backend/.env` matches your frontend URL.
- The Vite dev server proxies `/api` to `localhost:3001` automatically.

### Docker: `prisma` command not found during build
The backend Dockerfile installs all dependencies (including `prisma`) so `npx prisma generate` works during the image build. Do not use `--only=production` in the backend Dockerfile.

---

## Security Considerations

- **Data Residency**: All data is stored locally on your server. No external APIs or cloud storage.
- **Anonymity**: The system does not track IP addresses (only hashes them for rate limiting).
- **File Uploads**: Files are stored with UUID filenames, outside the web root. Only authenticated users with Auditor or CEO roles can download.
- **Authentication**: JWT tokens expire after 1 hour. Login is rate-limited (5 attempts per 15 minutes).
- **EXIF Metadata**: The upload endpoint logs a warning that EXIF stripping should be enabled. For production, install `sharp` (`npm install sharp`) and replace the placeholder in `app/backend/src/routes/upload.js`.
- **Company Responsibility**: The deploying organization is responsible for:
  - Hosting and data residency
  - Regular backups
  - Server hardening (firewall, SSL/TLS)
  - Compliance with local regulations

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2026 [Majid Mumtaz](https://majidrajpar.github.io/portfolio_my/)

## Support

For issues and feature requests, please open an issue on GitHub.

---

**Note**: This application is designed for laptop/desktop use and is optimized for internal organizational use.

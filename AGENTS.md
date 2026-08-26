# Agent Instructions for KSA Whistleblowing Portal

## Project Overview

An open-source, self-hosted whistleblowing web application for organizations in Saudi Arabia. 
This project was built using a dual-AI-framework architecture (LangGraph + CrewAI) for rapid 
development and security review.

## Technology Stack

**Frontend:**
- React 18 + Vite
- React Router DOM
- CSS Modules (pure CSS, no framework)

**Backend:**
- Node.js + Express.js
- Prisma ORM + SQLite
- JWT authentication (jsonwebtoken)
- Multer for file uploads
- Helmet.js + express-rate-limit

**AI Frameworks:**
- LangGraph (main builder)
- CrewAI (external reviewer)
- Both use Ollama Cloud API with kimi-k2.6 model

## Directory Structure

```
dilp/
├── app/
│   ├── backend/          # Express.js API
│   │   ├── src/
│   │   │   ├── routes/   # API endpoints
│   │   │   ├── middleware/ # Auth & validation
│   │   │   └── utils/    # Helpers
│   │   ├── prisma/       # Database schema & seed
│   │   └── tests/        # Test suite
│   └── frontend/         # React SPA
│       ├── src/
│       │   ├── pages/    # Route components
│       │   ├── components/ # Reusable UI
│       │   └── context/  # React contexts
│       └── public/
├── framework/            # LangGraph AI framework
├── review_framework/     # CrewAI review framework
├── review_output/        # Generated review reports
├── workspace/            # Development artifacts
├── README.md             # Main documentation
├── QUICKSTART.md         # Quick start guide
├── LICENSE               # MIT License
└── .gitignore            # Git exclusions
```

## Build Commands

```bash
# Backend
cd app/backend
npm install
npm run db:generate    # Generate Prisma client
npm run db:migrate     # Run database migrations
npm run db:seed        # Create initial users
npm run dev            # Start development server

# Frontend
cd app/frontend
npm install
npm run dev            # Start Vite dev server
npm run build          # Production build

# Full test suite
cd app/backend
npm test
```

## Environment Variables

See `app/backend/.env.example` for required variables.

Key variables:
- `DATABASE_URL` - SQLite database path
- `JWT_SECRET` - Secret for JWT signing (min 32 chars)
- `IP_HASH_PEPPER` - Pepper for IP hash rate limiting
- `INITIAL_AUDITOR_USER/PASS` - First auditor credentials
- `INITIAL_CEO_USER/PASS` - First CEO credentials

## Security Model

- JWT authentication with 1-hour expiry
- bcrypt password hashing (12 rounds)
- Rate limiting: 5 reports/hour, 5 login attempts/15min
- File uploads: JPG/PNG/PDF only, 5MB max, UUID filenames
- No IP storage (hashed only for rate limiting)
- Helmet.js for security headers

## Testing

```bash
cd app/backend
npm test              # Run Jest tests with coverage
```

## License

MIT License - See LICENSE file

## Notes for AI Agents

- This project was generated with AI assistance using LangGraph and CrewAI
- The `framework/` and `review_framework/` directories contain the AI tools used
- These are optional and can be removed if you only want the application code
- All application code in `app/` is production-ready and fully functional

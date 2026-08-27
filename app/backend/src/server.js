require('dotenv').config();

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const path = require('path');
const { verifyToken, requireRole } = require('./middleware/auth');

// ── Environment Validation ───────────────────────────────
const REQUIRED_ENV = ['DATABASE_URL', 'JWT_SECRET', 'IP_HASH_PEPPER'];
for (const key of REQUIRED_ENV) {
  if (!process.env[key]) {
    console.error(`FATAL: Missing required environment variable "${key}"`);
    process.exit(1);
  }
}

if (!process.env.JWT_SECRET || process.env.JWT_SECRET.length < 32) {
  console.error('FATAL: JWT_SECRET must be at least 32 characters long');
  process.exit(1);
}

const app = express();
const PORT = process.env.PORT || 3001;

// ── Security Middleware ──────────────────────────────────
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "blob:"],
    },
  },
}));

// CORS configuration
const allowedOrigins = (process.env.CORS_ORIGIN || 'http://localhost:5173').split(',');
// Validate origins - reject wildcards and empty values
const validatedOrigins = allowedOrigins.filter(origin => {
  const trimmed = origin.trim();
  return trimmed && trimmed !== '*' && trimmed.startsWith('http');
});
if (validatedOrigins.length === 0) {
  console.error('FATAL: CORS_ORIGIN must contain valid HTTP origins');
  process.exit(1);
}
app.use(cors({
  origin: validatedOrigins,
  credentials: true
}));

app.use(express.json({ limit: '1mb' }));

// ── Rate Limiting ────────────────────────────────────────
// General rate limiter
// General rate limiter
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
  message: { error: 'Too many requests, please try again later.' },
  standardHeaders: true,
  legacyHeaders: false,
});

// Auth rate limiter - stricter
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5,
  skipSuccessfulRequests: true,
  message: { error: 'Too many login attempts. Please try again later.' },
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => {
    const username = req.body?.username || 'unknown';
    return `${req.ip}:${username}`;
  }
});

// Anonymous report rate limiter
const reportLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 5,
  message: { error: 'Rate limit exceeded. Maximum 5 reports per hour.' },
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => req.ip
});

app.use(generalLimiter);

// ── Routes ───────────────────────────────────────────────
const authRoutes = require('./routes/auth');
const reportRoutes = require('./routes/reports');
const uploadRoutes = require('./routes/upload');
const auditLogRoutes = require('./routes/audit-log');

app.use('/api/auth/login', authLimiter);
app.use('/api/auth', authRoutes);
app.use('/api/reports', reportLimiter, reportRoutes);
app.use('/api/upload', reportLimiter, uploadRoutes);
app.use('/api/audit-log', auditLogRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// ── File Download (Authenticated) ────────────────────────────────
// Files are served through authenticated endpoint, not static
const ALLOWED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png'];

app.get('/api/files/:filename', verifyToken, requireRole(['AUDITOR', 'CEO']), (req, res) => {
  const filename = req.params.filename;
  // Sanitize filename - only allow UUID format with safe extensions
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.[a-z]{3,4}$/i;
  if (!uuidRegex.test(filename)) {
    return res.status(400).json({ error: 'Invalid filename' });
  }
  
  const ext = path.extname(filename).toLowerCase();
  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    return res.status(400).json({ error: 'File type not allowed' });
  }
  
  const filePath = path.join(__dirname, '../uploads', filename);
  const resolvedPath = path.resolve(filePath);
  const resolvedUploads = path.resolve(path.join(__dirname, '../uploads'));
  
  if (!resolvedPath.startsWith(resolvedUploads)) {
    return res.status(403).json({ error: 'Access denied' });
  }
  
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Content-Disposition', 'attachment');
  res.sendFile(filePath);
});

// ── Global Error Handler ────────────────────────────────
app.use((err, req, res, next) => {
  console.error('Error:', err);
  
  const isProduction = process.env.NODE_ENV === 'production';
  
  res.status(err.status || 500).json({
    error: isProduction ? 'Internal Server Error' : err.message
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// ── Start Server ─────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`🚀 Whistleblowing backend running on port ${PORT}`);
  console.log(`📊 Environment: ${process.env.NODE_ENV || 'development'}`);
});

module.exports = app;

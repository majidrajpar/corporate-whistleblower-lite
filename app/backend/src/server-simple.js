const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const path = require('path');

const app = express();
const PORT = 3001;

// Basic middleware
app.use(express.json({ limit: '1mb' }));
app.use(cors({ origin: 'http://localhost:5173', credentials: true }));
app.use(helmet());

// Rate limiting
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: { error: 'Too many requests' },
});

app.use(generalLimiter);

// Import routes
const authRoutes = require('./routes/auth');
const reportRoutes = require('./routes/reports');
const uploadRoutes = require('./routes/upload');
const auditLogRoutes = require('./routes/audit-log');

// Apply routes
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: { error: 'Too many login attempts' },
});

const reportLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,
  max: 5,
  message: { error: 'Rate limit exceeded. Max 5 reports/hour' },
});

app.use('/api/auth/login', authLimiter);
app.use('/api/auth', authRoutes);
app.use('/api/reports', reportLimiter, reportRoutes);
app.use('/api/upload', reportLimiter, uploadRoutes);
app.use('/api/audit-log', auditLogRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Internal Server Error' });
});

app.listen(PORT, () => {
  console.log(`🚀 Backend running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
});

module.exports = app;

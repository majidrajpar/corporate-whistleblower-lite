const express = require('express');
const crypto = require('crypto');
const prisma = require('../utils/prisma');
const { verifyToken, requireRole } = require('../middleware/auth');
const router = express.Router();

// POST /api/reports - Anonymous report creation (no auth required)
// SECURITY: Rate limiting handled by express-rate-limit middleware in server.js
// We do NOT store any IP-derived data with the report to preserve anonymity
router.post('/', async (req, res) => {
  try {
    const { category, message, uploadToken } = req.body;

    // Validation
    if (!category || !message) {
      return res.status(400).json({ error: 'Category and message are required' });
    }

    const validCategories = ['FINANCIAL_MISCONDUCT', 'FRAUD_CORRUPTION', 'HARASSMENT_WORKPLACE_MISCONDUCT', 'HEALTH_SAFETY_VIOLATION', 'OTHER'];
    if (!validCategories.includes(category)) {
      return res.status(400).json({ error: 'Invalid category' });
    }

    // Validate message length
    if (message.trim().length < 20) {
      return res.status(400).json({ error: 'Please provide more details (at least 20 characters)' });
    }
    if (message.length > 10000) {
      return res.status(400).json({ error: 'Message too long (maximum 10,000 characters)' });
    }

    // Validate uploadToken if provided (must be a UUID from our upload endpoint)
    let filePath = null;
    if (uploadToken) {
      // uploadToken should be the UUID filename returned by /api/upload
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.[a-z]{3,4}$/i;
      if (!uuidRegex.test(uploadToken)) {
        return res.status(400).json({ error: 'Invalid upload token format' });
      }
      
      // Verify file exists in uploads directory
      const fs = require('fs');
      const path = require('path');
      const uploadDir = process.env.UPLOAD_DIR || './uploads';
      const expectedPath = path.join(uploadDir, uploadToken);
      const resolvedPath = path.resolve(expectedPath);
      const resolvedUploads = path.resolve(uploadDir);
      
      // Path traversal protection
      if (!resolvedPath.startsWith(resolvedUploads)) {
        return res.status(400).json({ error: 'Invalid file path' });
      }
      
      if (!fs.existsSync(expectedPath)) {
        return res.status(400).json({ error: 'Uploaded file not found' });
      }
      
      filePath = uploadToken;
    }

    // Create report - NO IP data stored (anonymity preserved)
    const report = await prisma.report.create({
      data: {
        category,
        description: message,
        filePath,
        status: 'NEW',
        receiptCode: crypto.randomBytes(8).toString('hex').toUpperCase()
      }
    });

    res.status(201).json({
      id: report.id,
      message: 'Report submitted successfully',
      receiptCode: report.receiptCode
    });
  } catch (error) {
    console.error('Report creation error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/reports - Get all reports (auditor only)
router.get('/', verifyToken, requireRole('AUDITOR'), async (req, res) => {
  try {
    const { status, category } = req.query;
    const where = {};

    if (status) where.status = status;
    if (category) where.category = category;

    const reports = await prisma.report.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      include: {
        auditLogs: {
          include: { user: { select: { email: true, name: true, role: true } } },
          orderBy: { createdAt: 'desc' },
          take: 5
        }
      }
    });

    res.json(reports);
  } catch (error) {
    console.error('Get reports error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// PUT /api/reports/:id/status - Update report status (auditor only)
router.put('/:id/status', verifyToken, requireRole('AUDITOR'), async (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;

    const validStatuses = ['NEW', 'IN_REVIEW', 'ESCALATED', 'RESOLVED'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ error: 'Invalid status' });
    }

    const oldReport = await prisma.report.findUnique({ where: { id } });
    if (!oldReport) {
      return res.status(404).json({ error: 'Report not found' });
    }

    const updated = await prisma.report.update({
      where: { id },
      data: { status }
    });

    // Log action
    await prisma.auditLog.create({
      data: {
        userId: req.user.userId,
        reportId: id,
        action: status === 'RESOLVED' ? 'RESOLVED' : 'STATUS_CHANGED',
        details: `Status: ${oldReport.status} -> ${status}`
      }
    });

    res.json(updated);
  } catch (error) {
    console.error('Status update error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/reports/:id/escalate - Escalate report to CEO (auditor only)
router.post('/:id/escalate', verifyToken, requireRole('AUDITOR'), async (req, res) => {
  try {
    const { id } = req.params;

    const report = await prisma.report.findUnique({ where: { id } });
    if (!report) {
      return res.status(404).json({ error: 'Report not found' });
    }

    const updated = await prisma.report.update({
      where: { id },
      data: { status: 'ESCALATED' }
    });

    // Log action
    await prisma.auditLog.create({
      data: {
        userId: req.user.userId,
        reportId: id,
        action: 'ESCALATED',
        details: 'Report escalated to CEO'
      }
    });

    res.json(updated);
  } catch (error) {
    console.error('Escalation error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/reports/escalated - Get escalated reports (CEO only)
router.get('/escalated', verifyToken, requireRole('CEO'), async (req, res) => {
  try {
    const reports = await prisma.report.findMany({
      where: { status: 'ESCALATED' },
      orderBy: { createdAt: 'desc' },
      include: {
        auditLogs: {
          include: { user: { select: { email: true, name: true, role: true } } },
          orderBy: { createdAt: 'desc' },
          take: 5
        }
      }
    });

    // Get summary stats
    const stats = await prisma.report.groupBy({
      by: ['category'],
      _count: { id: true }
    });

    res.json({ reports, stats });
  } catch (error) {
    console.error('Get escalated reports error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;

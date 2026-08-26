const express = require('express');
const prisma = require('../utils/prisma');
const { verifyToken, requireRole } = require('../middleware/auth');
const router = express.Router();

// GET /api/audit-log - View audit logs (auditor and CEO only)
router.get('/', verifyToken, requireRole('AUDITOR'), async (req, res) => {
  try {
    const logs = await prisma.auditLog.findMany({
      orderBy: { createdAt: 'desc' },
      take: 100,
      include: {
        user: { select: { email: true, name: true, role: true } },
        report: { select: { id: true, category: true, status: true } }
      }
    });

    res.json(logs);
  } catch (error) {
    console.error('Get audit logs error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/audit-log - Create audit log entry (REMOVED - internal middleware only)
// Audit logs should only be created by internal service functions, not via HTTP API
// This prevents log poisoning by privileged users

module.exports = router;

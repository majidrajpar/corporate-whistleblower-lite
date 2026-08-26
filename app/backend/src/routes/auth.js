const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const prisma = require('../utils/prisma');
const router = express.Router();

// Input validation helper
function validateInput(input, field, min = 1, max = 100) {
  if (!input || typeof input !== 'string') {
    return `${field} is required`;
  }
  if (input.length < min) {
    return `${field} must be at least ${min} characters`;
  }
  if (input.length > max) {
    return `${field} must be at most ${max} characters`;
  }
  // Allow only alphanumeric and common username characters
  if (field === 'username' && !/^[a-zA-Z0-9_-]+$/.test(input)) {
    return `${field} contains invalid characters`;
  }
  return null;
}

// POST /api/auth/login
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    // Validate inputs - username is used as email prefix
    const usernameError = validateInput(username, 'username', 3, 50);
    if (usernameError) {
      return res.status(400).json({ error: usernameError });
    }

    const passwordError = validateInput(password, 'password', 1, 128);
    if (passwordError) {
      return res.status(400).json({ error: passwordError });
    }

    // Construct email from username (matching seed format)
    const email = `${username}@company.com`;

    // Find user by email
    const user = await prisma.user.findUnique({
      where: { email }
    });

    // Constant-time comparison to prevent timing attacks
    let isValid = false;
    if (user) {
      isValid = await bcrypt.compare(password, user.passwordHash);
    } else {
      // Perform dummy comparison to prevent timing-based enumeration
      await bcrypt.compare(password, '$2a$12$dummyhashfordummyhashfordummyhashfordummyhashfor');
    }

    if (!isValid) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Update last login
    await prisma.user.update({
      where: { id: user.id },
      data: { lastLoginAt: new Date() }
    });

    // Generate JWT with shorter expiry (1 hour)
    const token = jwt.sign(
      { userId: user.id, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: '1h', algorithm: 'HS256' }
    );

    res.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;

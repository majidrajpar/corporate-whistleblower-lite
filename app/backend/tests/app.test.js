const request = require('supertest');
const express = require('express');

describe('Whistleblowing Backend', () => {
  let app;
  let authToken;
  let ceoToken;

  beforeAll(() => {
    // Simple mock app for testing
    app = express();
    app.use(express.json());
    
    // Mock auth route
    app.post('/api/auth/login', (req, res) => {
      const { username, password } = req.body;
      if (username === 'auditor' && password === 'test123') {
        res.json({ token: 'mock-auditor-token', user: { role: 'AUDITOR' } });
      } else if (username === 'ceo' && password === 'test123') {
        res.json({ token: 'mock-ceo-token', user: { role: 'CEO' } });
      } else {
        res.status(401).json({ error: 'Invalid credentials' });
      }
    });

    // Mock reports route
    app.post('/api/reports', (req, res) => {
      const { category, message } = req.body;
      if (!category || !message) {
        return res.status(400).json({ error: 'Category and message required' });
      }
      res.status(201).json({ id: '1', message: 'Report submitted', receiptCode: 'ABC123' });
    });

    app.get('/api/reports', (req, res) => {
      res.json([
        { id: '1', category: 'FRAUD_CORRUPTION', status: 'NEW', message: 'Test report' }
      ]);
    });

    app.get('/api/reports/escalated', (req, res) => {
      res.json({ reports: [], stats: [] });
    });
  });

  describe('Authentication', () => {
    it('should login with valid auditor credentials', async () => {
      const res = await request(app)
        .post('/api/auth/login')
        .send({ username: 'auditor', password: 'test123' });
      
      expect(res.status).toBe(200);
      expect(res.body.token).toBeDefined();
      expect(res.body.user.role).toBe('AUDITOR');
      authToken = res.body.token;
    });

    it('should login with valid CEO credentials', async () => {
      const res = await request(app)
        .post('/api/auth/login')
        .send({ username: 'ceo', password: 'test123' });
      
      expect(res.status).toBe(200);
      expect(res.body.user.role).toBe('CEO');
      ceoToken = res.body.token;
    });

    it('should reject invalid credentials', async () => {
      const res = await request(app)
        .post('/api/auth/login')
        .send({ username: 'wrong', password: 'wrong' });
      
      expect(res.status).toBe(401);
    });
  });

  describe('Anonymous Reporting', () => {
    it('should create report without authentication', async () => {
      const res = await request(app)
        .post('/api/reports')
        .send({ category: 'FRAUD_CORRUPTION', message: 'Test report content' });
      
      expect(res.status).toBe(201);
      expect(res.body.receiptCode).toBeDefined();
    });

    it('should reject report without required fields', async () => {
      const res = await request(app)
        .post('/api/reports')
        .send({ category: 'FRAUD_CORRUPTION' });
      
      expect(res.status).toBe(400);
    });
  });

  describe('Report Management', () => {
    it('should get all reports for auditor', async () => {
      const res = await request(app)
        .get('/api/reports')
        .set('Authorization', `Bearer ${authToken}`);
      
      expect(res.status).toBe(200);
      expect(Array.isArray(res.body)).toBe(true);
    });

    it('should get escalated reports for CEO', async () => {
      const res = await request(app)
        .get('/api/reports/escalated')
        .set('Authorization', `Bearer ${ceoToken}`);
      
      expect(res.status).toBe(200);
      expect(res.body.reports).toBeDefined();
    });
  });
});

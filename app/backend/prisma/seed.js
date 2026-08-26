const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcryptjs');

const prisma = new PrismaClient();

async function seed() {
  console.log('Starting database seed...');

  try {
    // Check if users already exist
    const existingUsers = await prisma.user.count();
    if (existingUsers > 0) {
      console.log('Users already exist, skipping seed.');
      return;
    }

    // Create initial auditor user
    const auditorUser = process.env.INITIAL_AUDITOR_USER || 'auditor';
    const auditorPass = process.env.INITIAL_AUDITOR_PASS || 'changeme123';

    await prisma.user.create({
      data: {
        email: `${auditorUser}@company.com`,
        passwordHash: await bcrypt.hash(auditorPass, 12),
        name: 'Internal Auditor',
        role: 'AUDITOR'
      }
    });
    console.log(`Created auditor user: ${auditorUser}@company.com`);

    // Create initial CEO user
    const ceoUser = process.env.INITIAL_CEO_USER || 'ceo';
    const ceoPass = process.env.INITIAL_CEO_PASS || 'changeme123';

    await prisma.user.create({
      data: {
        email: `${ceoUser}@company.com`,
        passwordHash: await bcrypt.hash(ceoPass, 12),
        name: 'Chief Executive Officer',
        role: 'CEO'
      }
    });
    console.log(`Created CEO user: ${ceoUser}@company.com`);

    console.log('Seed completed successfully.');
  } catch (error) {
    console.error('Seed error:', error);
  } finally {
    await prisma.$disconnect();
  }
}

seed();

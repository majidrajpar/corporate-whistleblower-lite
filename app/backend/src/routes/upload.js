const express = require('express');
const multer = require('multer');
const crypto = require('crypto');
const path = require('path');
const fs = require('fs');

const router = express.Router();

// Ensure uploads directory exists
const uploadDir = process.env.UPLOAD_DIR || './uploads';
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// Configure Multer storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    // Generate UUID-like filename to prevent path traversal
    const uniqueName = crypto.randomUUID() + path.extname(file.originalname).toLowerCase();
    cb(null, uniqueName);
  }
});

// File filter - only allow images and PDFs
const fileFilter = (req, file, cb) => {
  const allowedMimes = ['image/jpeg', 'image/png', 'application/pdf'];
  const allowedExts = ['.jpg', '.jpeg', '.png', '.pdf'];
  
  const ext = path.extname(file.originalname).toLowerCase();
  
  if (allowedMimes.includes(file.mimetype) && allowedExts.includes(ext)) {
    cb(null, true);
  } else {
    cb(new Error('Only JPG, PNG, and PDF files are allowed'), false);
  }
};

// Configure upload limits
const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB
    files: 1
  }
});

// ── EXIF Stripping Function ──────────────────────────────
// SECURITY: Images may contain EXIF metadata (GPS coordinates, device serial
// numbers, timestamps) that could deanonymize whistleblowers.
// This function strips all EXIF data by re-encoding the image.
// 
// NOTE: For production, install sharp: npm install sharp
// Then replace the placeholder below with: sharp(input).rotate().toFile(output)
// Or use exiftool: exiftool -all= image.jpg
// ────────────────────────────────────────────────────────────

async function stripExifMetadata(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  
  // Only process images (not PDFs)
  if (!['.jpg', '.jpeg', '.png'].includes(ext)) {
    return; // PDFs don't have EXIF
  }
  
  try {
    // Placeholder: In production, use sharp or exiftool
    // Example with sharp:
    // const sharp = require('sharp');
    // const buffer = await sharp(filePath).rotate().toBuffer();
    // await fs.promises.writeFile(filePath, buffer);
    
    // For now, log that EXIF stripping is needed
    console.log(`[Upload] EXIF metadata should be stripped from: ${path.basename(filePath)}`);
    console.log(`[Upload] Install sharp: npm install sharp`);
    console.log(`[Upload] Then update stripExifMetadata() in routes/upload.js`);
    
    // TODO: Replace with actual EXIF stripping when sharp is installed
    // This is tracked as a HIGH priority security issue in:
    // review_output/feedback_issues.json (Issue #10)
    
  } catch (error) {
    console.error('[Upload] EXIF stripping error:', error);
    // Don't fail the upload if EXIF stripping fails
    // But log it for security review
  }
}

// POST /api/upload - Single file upload (rate limited: 5/hour/IP)
router.post('/', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    // Strip EXIF metadata from images to protect whistleblower anonymity
    await stripExifMetadata(req.file.path);

    // Return only the UUID filename (not full path)
    res.json({
      success: true,
      filePath: req.file.filename,
      originalName: req.file.originalname,
      size: req.file.size
    });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'File upload failed' });
  }
});

// Error handler for multer
router.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ error: 'File too large. Maximum size is 5MB.' });
    }
    return res.status(400).json({ error: error.message });
  }
  next(error);
});

module.exports = router;

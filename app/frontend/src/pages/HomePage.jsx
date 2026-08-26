import React, { useState } from 'react';
import ReportForm from '../components/ReportForm';

function HomePage() {
  const [submitted, setSubmitted] = useState(false);
  const [receiptCode, setReceiptCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async ({ category, message, file }) => {
    setLoading(true);
    setError('');

    try {
      let uploadToken = null;

      // Upload file if present
      if (file) {
        const formData = new FormData();
        formData.append('file', file);

        const uploadResponse = await fetch('/api/upload', {
          method: 'POST',
          body: formData
        });

        if (!uploadResponse.ok) {
          if (uploadResponse.status === 429) {
            throw new Error('Rate limit exceeded. Maximum 5 uploads per hour.');
          }
          throw new Error('File upload failed');
        }

        const uploadData = await uploadResponse.json();
        uploadToken = uploadData.filePath; // UUID filename from server
      }

      // Submit report with upload token (not file path)
      const reportResponse = await fetch('/api/reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category, message, uploadToken })
      });

      if (!reportResponse.ok) {
        if (reportResponse.status === 429) {
          throw new Error('Rate limit exceeded. Please try again later.');
        }
        throw new Error('Failed to submit report');
      }

      const data = await reportResponse.json();
      setReceiptCode(data.receiptCode);
      setSubmitted(true);
    } catch (err) {
      setError(err.message || 'Failed to submit report. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      <div className="hero-section">
        <h1>Report Safely and Anonymously</h1>
        <p className="hero-subtitle">
          Report concerns confidentially and securely. Your identity remains completely anonymous.
        </p>
        
        <div className="trust-badges">
          <div className="badge">
            <svg className="badge-icon" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <span>100% Anonymous</span>
          </div>
          <div className="badge">
            <svg className="badge-icon" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
            <span>Secure Transmission</span>
          </div>
          <div className="badge">
            <svg className="badge-icon" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
            <span>No Tracking</span>
          </div>
        </div>
        
        <div className="trust-details">
          <details>
            <summary>How we protect your identity</summary>
            <ul>
              <li>We do not collect your name, email, employee ID, or any identifying information.</li>
              <li>Your IP address is never stored or logged in our database.</li>
              <li>All data is transmitted over encrypted HTTPS connections.</li>
              <li>Uploaded files are renamed with random IDs and stripped of metadata.</li>
              <li>Only authorized Internal Audit personnel can access reports.</li>
              <li>Reports are stored on your company's own servers, not in the cloud.</li>
            </ul>
          </details>
        </div>
      </div>

      {submitted ? (
        <div className="success-section">
          <div className="success-icon">✓</div>
          <h2>Report Submitted Successfully</h2>
          <p>Thank you for your report. It has been forwarded to Internal Audit.</p>
          
          <div className="receipt-code">
            <p>Your receipt code:</p>
            <code>{receiptCode}</code>
            <p className="receipt-note">Please save this code for your records.</p>
          </div>

          <button className="btn-secondary" onClick={() => { setSubmitted(false); setReceiptCode(''); }}>
            Submit Another Report
          </button>
        </div>
      ) : (
        <div className="form-section">
          {error && <div className="error-message">{error}</div>}
          
          <ReportForm onSubmit={handleSubmit} loading={loading} />
          
          <div className="form-footer">
            <p>
              <strong>Note:</strong> This form is completely anonymous. 
              We do not collect any identifying information.
            </p>
            <p>
              For internal access, <a href="/login">click here</a>.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default HomePage;

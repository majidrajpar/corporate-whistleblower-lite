import React, { useState } from 'react';

function ReportForm({ onSubmit, loading }) {
  const [category, setCategory] = useState('');
  const [message, setMessage] = useState('');
  const [file, setFile] = useState(null);
  const [errors, setErrors] = useState({});

  const categories = [
    { value: 'FINANCIAL_MISCONDUCT', label: 'Financial Misconduct' },
    { value: 'FRAUD_CORRUPTION', label: 'Fraud / Corruption' },
    { value: 'HARASSMENT_WORKPLACE_MISCONDUCT', label: 'Harassment / Workplace Misconduct' },
    { value: 'HEALTH_SAFETY_VIOLATION', label: 'Health & Safety Violation' },
    { value: 'OTHER', label: 'Other' }
  ];

  const validate = () => {
    const newErrors = {};
    if (!category) newErrors.category = 'Please select a category';
    if (!message.trim()) newErrors.message = 'Please describe the incident';
    if (message.trim().length < 20) newErrors.message = 'Please provide more details (at least 20 characters)';
    if (file) {
      const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
      if (!allowedTypes.includes(file.type)) {
        newErrors.file = 'Only JPG, PNG, and PDF files are allowed';
      }
      if (file.size > 5 * 1024 * 1024) {
        newErrors.file = 'File must be smaller than 5MB';
      }
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      onSubmit({ category, message, file });
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setErrors({ ...errors, file: '' });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="report-form">
      <div className="form-group">
        <label htmlFor="category">Report Category *</label>
        <select
          id="category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className={errors.category ? 'error' : ''}
        >
          <option value="">Select a category...</option>
          {categories.map(cat => (
            <option key={cat.value} value={cat.value}>{cat.label}</option>
          ))}
        </select>
        {errors.category && <span className="error-text">{errors.category}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="message">Description *</label>
        <textarea
          id="message"
          rows="6"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Please describe the incident in detail..."
          className={errors.message ? 'error' : ''}
        />
        {errors.message && <span className="error-text">{errors.message}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="file">Attachment (optional)</label>
        <input
          type="file"
          id="file"
          accept=".jpg,.jpeg,.png,.pdf"
          onChange={handleFileChange}
        />
        <small>Accepted: JPG, PNG, PDF. Max size: 5MB</small>
        {errors.file && <span className="error-text">{errors.file}</span>}
        {file && <span className="file-selected">Selected: {file.name}</span>}
      </div>

      <button type="submit" className="btn-primary" disabled={loading}>
        {loading ? 'Submitting...' : 'Submit Report Anonymously'}
      </button>
    </form>
  );
}

export default ReportForm;

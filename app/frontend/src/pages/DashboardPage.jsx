import React, { useState, useEffect } from 'react';

function DashboardPage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [selectedReport, setSelectedReport] = useState(null);

  const categories = [
    { value: '', label: 'All Categories' },
    { value: 'FINANCIAL_MISCONDUCT', label: 'Financial Misconduct' },
    { value: 'FRAUD_CORRUPTION', label: 'Fraud / Corruption' },
    { value: 'HARASSMENT_WORKPLACE_MISCONDUCT', label: 'Harassment / Workplace Misconduct' },
    { value: 'HEALTH_SAFETY_VIOLATION', label: 'Health & Safety Violation' },
    { value: 'OTHER', label: 'Other' }
  ];

  const statuses = [
    { value: '', label: 'All Statuses' },
    { value: 'NEW', label: 'New' },
    { value: 'IN_REVIEW', label: 'In Review' },
    { value: 'ESCALATED', label: 'Escalated' },
    { value: 'RESOLVED', label: 'Resolved' }
  ];

  useEffect(() => {
    fetchReports();
  }, [filterStatus, filterCategory]);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const params = new URLSearchParams();
      if (filterStatus) params.append('status', filterStatus);
      if (filterCategory) params.append('category', filterCategory);

      const response = await fetch(`/api/reports?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to fetch reports');
      
      const data = await response.json();
      setReports(data);
    } catch (err) {
      setError('Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (reportId, newStatus) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/reports/${reportId}/status`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
      });

      if (!response.ok) throw new Error('Failed to update status');
      
      fetchReports();
      setSelectedReport(null);
    } catch (err) {
      setError('Failed to update status');
    }
  };

  const escalateReport = async (reportId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/reports/${reportId}/escalate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to escalate');
      
      fetchReports();
      setSelectedReport(null);
    } catch (err) {
      setError('Failed to escalate report');
    }
  };

  return (
    <div className="dashboard-container">
      <h1>Internal Audit Dashboard</h1>
      
      <div className="filters">
        <select value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)}>
          {categories.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
        <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
          {statuses.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
        </select>
        
        <button onClick={fetchReports} className="btn-secondary">Refresh</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading reports...</div>
      ) : (
        <div className="reports-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Category</th>
                <th>Status</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {reports.map(report => (
                <tr key={report.id} onClick={() => setSelectedReport(report)}>
                  <td>{report.id.slice(0, 8)}...</td>
                  <td>{report.category}</td>
                  <td>
                    <span className={`status-badge status-${report.status.toLowerCase()}`}>
                      {report.status}
                    </span>
                  </td>
                  <td>{new Date(report.createdAt).toLocaleDateString()}</td>
                  <td>
                    <button className="btn-small" onClick={() => setSelectedReport(report)}>View</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedReport && (
        <div className="modal-overlay" onClick={() => setSelectedReport(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Report Details</h2>
            <p><strong>Category:</strong> {selectedReport.category}</p>
            <p><strong>Status:</strong> {selectedReport.status}</p>
            <p><strong>Message:</strong></p>
            <p>{selectedReport.description}</p>
            <p><strong>Submitted:</strong> {new Date(selectedReport.createdAt).toLocaleString()}</p>
            
            {selectedReport.filePath && (
              <p><strong>Attachment:</strong> {selectedReport.filePath}</p>
            )}

            <div className="modal-actions">
              {selectedReport.status === 'NEW' && (
                <button className="btn-primary" onClick={() => updateStatus(selectedReport.id, 'IN_REVIEW')}>
                  Mark In Review
                </button>
              )}
              {selectedReport.status === 'IN_REVIEW' && (
                <>
                  <button className="btn-primary" onClick={() => escalateReport(selectedReport.id)}>
                    Escalate to CEO
                  </button>
                  <button className="btn-secondary" onClick={() => updateStatus(selectedReport.id, 'RESOLVED')}>
                    Mark Resolved
                  </button>
                </>
              )}
              <button className="btn-secondary" onClick={() => setSelectedReport(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DashboardPage;

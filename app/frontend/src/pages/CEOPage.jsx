import React, { useState, useEffect } from 'react';

function CEOPage() {
  const [reports, setReports] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchEscalatedReports();
  }, []);

  const fetchEscalatedReports = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch('/api/reports/escalated', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to fetch reports');
      
      const data = await response.json();
      setReports(data.reports || []);
      setStats(data.stats || {});
    } catch (err) {
      setError('Failed to load escalated reports');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryCount = (category) => {
    if (!stats || !Array.isArray(stats)) return 0;
    const stat = stats.find(s => s.category === category);
    return stat ? stat._count.id : 0;
  };

  const categories = [
    { key: 'FINANCIAL_MISCONDUCT', label: 'Financial Misconduct' },
    { key: 'FRAUD_CORRUPTION', label: 'Fraud / Corruption' },
    { key: 'HARASSMENT_WORKPLACE_MISCONDUCT', label: 'Harassment' },
    { key: 'HEALTH_SAFETY_VIOLATION', label: 'Health & Safety' },
    { key: 'OTHER', label: 'Other' }
  ];

  return (
    <div className="ceo-container">
      <h1>CEO Dashboard</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Escalated Reports</h3>
          <p className="stat-number">{reports.length}</p>
        </div>
        
        {categories.map(cat => (
          <div className="stat-card" key={cat.key}>
            <h3>{cat.label}</h3>
            <p className="stat-number">{getCategoryCount(cat.key)}</p>
          </div>
        ))}
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading reports...</div>
      ) : (
        <div className="reports-table">
          <h2>Escalated Reports</h2>
          
          {reports.length === 0 ? (
            <p>No escalated reports at this time.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Category</th>
                  <th>Message</th>
                  <th>Submitted</th>
                  <th>Escalated</th>
                </tr>
              </thead>
              <tbody>
                {reports.map(report => (
                  <tr key={report.id}>
                    <td>{report.id.slice(0, 8)}...</td>
                    <td>{report.category}</td>
                    <td>{report.description?.substring(0, 100)}...</td>
                    <td>{new Date(report.createdAt).toLocaleDateString()}</td>
                    <td>{new Date(report.updatedAt).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}

export default CEOPage;

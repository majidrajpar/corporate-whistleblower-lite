import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  const { user, isAuthenticated, logout, isAuditor, isCEO } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">🏢 Ethics Reporting Portal</Link>
      </div>
      
      <div className="navbar-links">
        <Link to="/">Report</Link>
        
        {isAuthenticated ? (
          <>
            {isAuditor && <Link to="/dashboard">Dashboard</Link>}
            {isCEO && <Link to="/ceo">CEO Dashboard</Link>}
            <span className="user-role">
              {user?.role === 'AUDITOR' ? 'Internal Audit' : 'CEO'}
            </span>
            <button onClick={logout} className="btn-logout">Logout</button>
          </>
        ) : (
          <Link to="/login" className="btn-login">Internal Access</Link>
        )}
      </div>
    </nav>
  );
}

export default Navbar;

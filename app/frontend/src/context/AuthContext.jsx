import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

// SECURITY NOTE: This application uses localStorage for JWT token storage.
// This is acceptable for an internal corporate tool but carries XSS risk.
// For production hardening, consider:
// 1. httpOnly secure cookies with CSRF protection
// 2. Content Security Policy (CSP) headers
// 3. Short token expiry (currently 1 hour)
// 4. Token rotation on sensitive actions
// See: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for stored token on mount
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (token && storedUser) {
      try {
        // Basic token validation - check it's a valid JWT format
        const tokenParts = token.split('.');
        if (tokenParts.length === 3) {
          setUser(JSON.parse(storedUser));
        } else {
          // Invalid token format, clear storage
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }
      } catch (e) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (!response.ok) {
        throw new Error('Invalid credentials');
      }

      const data = await response.json();
      
      // Validate token format before storing
      if (!data.token || data.token.split('.').length !== 3) {
        throw new Error('Invalid token received');
      }
      
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      setUser(data.user);
      
      return data.user;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
    isAuditor: user?.role === 'AUDITOR',
    isCEO: user?.role === 'CEO',
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

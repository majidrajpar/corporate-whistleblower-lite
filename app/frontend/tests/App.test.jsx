import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../src/context/AuthContext';
import App from '../src/App';

describe('Whistleblowing Frontend', () => {
  it('renders home page with anonymous reporting form', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText('Ethics Reporting Portal')).toBeInTheDocument();
    expect(screen.getByText('100% Anonymous')).toBeInTheDocument();
    expect(screen.getByText('Submit Report Anonymously')).toBeInTheDocument();
  });

  it('shows login page when navigating to /login', () => {
    window.history.pushState({}, '', '/login');
    
    render(
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText('Internal Access')).toBeInTheDocument();
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
  });
});

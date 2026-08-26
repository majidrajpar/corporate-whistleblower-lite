const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export async function apiClient(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // Add auth token if available
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  get: (endpoint) => apiClient(endpoint, { method: 'GET' }),
  post: (endpoint, data) => apiClient(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  put: (endpoint, data) => apiClient(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
};

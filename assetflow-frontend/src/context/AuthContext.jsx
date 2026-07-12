import { createContext, useContext, useState, useEffect, useRef } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    // Restore user from localStorage on initial load
    const saved = localStorage.getItem('assetflow_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(localStorage.getItem('assetflow_token'));
  const [loading, setLoading] = useState(true);
  const justLoggedIn = useRef(false);

  useEffect(() => {
    // Skip /auth/me if we just logged in (user already set from login response)
    if (justLoggedIn.current) {
      justLoggedIn.current = false;
      setLoading(false);
      return;
    }

    if (token) {
      api.get('/auth/me')
        .then(res => {
          setUser(res.data);
          localStorage.setItem('assetflow_user', JSON.stringify(res.data));
        })
        .catch(() => {
          localStorage.removeItem('assetflow_token');
          localStorage.removeItem('assetflow_user');
          setToken(null);
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('assetflow_token', access_token);
    localStorage.setItem('assetflow_user', JSON.stringify(userData));
    justLoggedIn.current = true;
    setUser(userData);
    setToken(access_token);
    return userData;
  };

  const logout = () => {
    localStorage.removeItem('assetflow_token');
    localStorage.removeItem('assetflow_user');
    setToken(null);
    setUser(null);
  };

  // Backend returns lowercase roles: "admin", "manager", "employee"
  const role = user?.role?.toLowerCase();
  const isAdmin = role === 'admin';
  const isManager = role === 'manager';
  const canApprove = isAdmin || isManager;

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, isAdmin, isManager, canApprove }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}

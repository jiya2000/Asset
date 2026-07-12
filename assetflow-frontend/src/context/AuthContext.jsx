import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('assetflow_user');
      return saved ? JSON.parse(saved) : null;
    } catch { return null; }
  });
  const [token, setToken] = useState(localStorage.getItem('assetflow_token'));
  const [loading, setLoading] = useState(!user); // If user is restored, don't show loading

  // Only verify token on cold start (page reload with no cached user)
  useEffect(() => {
    if (token && !user) {
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
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run ONCE on mount only

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('assetflow_token', access_token);
    localStorage.setItem('assetflow_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const logout = () => {
    localStorage.removeItem('assetflow_token');
    localStorage.removeItem('assetflow_user');
    setToken(null);
    setUser(null);
  };

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

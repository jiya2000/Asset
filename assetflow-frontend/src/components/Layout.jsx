import { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard, Package, ArrowLeftRight, Wrench,
  Building2, LogOut, Settings, Bell
} from 'lucide-react';

export default function Layout() {
  const { user, logout, canApprove } = useAuth();
  const navigate = useNavigate();
  const [showNotifications, setShowNotifications] = useState(false);

  const notifications = [
    { id: 1, title: 'New Maintenance Request', message: 'Laptop screen cracked', time: '5m ago' },
    { id: 2, title: 'Asset Allocated', message: 'MacBook Pro assigned to John Doe', time: '1h ago' },
    { id: 3, title: 'Low Stock', message: 'Only 2 HDMI cables left', time: '2h ago' }
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const initials = user
    ? `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase()
    : '??';

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h1>AssetFlow</h1>
          <span>Asset Management</span>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/" end>
            <LayoutDashboard size={18} /> Dashboard
          </NavLink>
          <NavLink to="/assets">
            <Package size={18} /> Assets
          </NavLink>
          <NavLink to="/allocations">
            <ArrowLeftRight size={18} /> Allocations
          </NavLink>
          <NavLink to="/maintenance">
            <Wrench size={18} /> Maintenance
          </NavLink>
          {canApprove && (
            <NavLink to="/org-setup">
              <Settings size={18} /> Org Setup
            </NavLink>
          )}
        </nav>

        <div className="sidebar-user">
          <div className="sidebar-user-avatar">{initials}</div>
          <div className="sidebar-user-info">
            <p>{user?.first_name} {user?.last_name}</p>
            <span>{user?.role}</span>
          </div>
          <button onClick={handleLogout} className="btn btn-icon btn-ghost" title="Logout">
            <LogOut size={16} />
          </button>
        </div>
      </aside>

      <main className="main-content animate-fade" style={{ position: 'relative' }}>
        <div style={{ position: 'absolute', top: 24, right: 32, zIndex: 50 }}>
          <div style={{ position: 'relative' }}>
            <button 
              className="btn btn-icon btn-ghost" 
              style={{ position: 'relative' }}
              onClick={() => setShowNotifications(!showNotifications)}
            >
              <Bell size={20} />
              <span style={{ 
                position: 'absolute', top: 2, right: 2, width: 8, height: 8, 
                backgroundColor: 'var(--danger)', borderRadius: '50%' 
              }}></span>
            </button>
            {showNotifications && (
              <div style={{ 
                position: 'absolute', right: 0, top: '100%', marginTop: 8, width: 280, 
                background: 'var(--surface)', border: '1px solid var(--border)', 
                borderRadius: 'var(--radius)', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.3)' 
              }}>
                <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)' }}>
                  <h3 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 600 }}>Notifications</h3>
                </div>
                <div style={{ maxHeight: 300, overflowY: 'auto' }}>
                  {notifications.map(n => (
                    <div key={n.id} style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)' }}>
                      <h4 style={{ margin: 0, fontSize: '0.85rem', fontWeight: 600, color: 'var(--text)' }}>{n.title}</h4>
                      <p style={{ margin: '4px 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>{n.message}</p>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{n.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
        <Outlet />
      </main>
    </div>
  );
}

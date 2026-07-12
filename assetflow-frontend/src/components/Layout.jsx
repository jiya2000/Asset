import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard, Package, ArrowLeftRight, Wrench,
  Building2, LogOut, Settings
} from 'lucide-react';

export default function Layout() {
  const { user, logout, canApprove } = useAuth();
  const navigate = useNavigate();

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

      <main className="main-content animate-fade">
        <Outlet />
      </main>
    </div>
  );
}

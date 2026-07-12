import { useState, useEffect } from 'react';
import api from '../api/client';
import {
  Package, Users, ArrowLeftRight, Wrench, AlertTriangle,
  Clock, TrendingUp, Activity, CheckCircle, XCircle
} from 'lucide-react';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Legend
} from 'recharts';

const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#64748b', '#ef4444', '#8b5cf6'];

const SEVERITY_MAP = {
  info: { bg: 'var(--info-muted)', color: 'var(--info)', icon: Activity },
  warning: { bg: 'var(--warning-muted)', color: 'var(--warning)', icon: AlertTriangle },
  critical: { bg: 'var(--danger-muted)', color: 'var(--danger)', icon: XCircle },
};

export default function Dashboard() {
  const [kpis, setKpis] = useState(null);
  const [insights, setInsights] = useState([]);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/dashboard/kpis'),
      api.get('/dashboard/insights'),
      api.get('/dashboard/activity?limit=15'),
    ]).then(([kRes, iRes, aRes]) => {
      setKpis(kRes.data);
      setInsights(iRes.data);
      setActivity(aRes.data);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-page"><div className="spinner" /></div>;
  if (!kpis) return null;

  const kpiCards = [
    { label: 'Total Assets', value: kpis.total_assets, icon: Package, color: 'var(--primary)' },
    { label: 'Available', value: kpis.available_assets, icon: CheckCircle, color: 'var(--success)' },
    { label: 'Allocated', value: kpis.allocated_assets, icon: ArrowLeftRight, color: 'var(--info)' },
    { label: 'Maintenance', value: kpis.under_maintenance, icon: Wrench, color: 'var(--warning)' },
    { label: 'Employees', value: kpis.total_employees, icon: Users, color: 'var(--primary-hover)' },
    { label: 'Pending Approvals', value: kpis.pending_approvals, icon: Clock, color: 'var(--warning)' },
    { label: 'Overdue Returns', value: kpis.overdue_returns, icon: AlertTriangle, color: 'var(--danger)' },
    { label: 'Retired', value: kpis.retired_assets, icon: XCircle, color: 'var(--text-muted)' },
  ];

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Real-time overview of your asset ecosystem</p>
      </div>

      {/* KPI Grid */}
      <div className="kpi-grid">
        {kpiCards.map((k, i) => (
          <div key={i} className="kpi-card">
            <div className="kpi-icon" style={{ background: `${k.color}15` }}>
              <k.icon size={18} style={{ color: k.color }} />
            </div>
            <div className="kpi-label">{k.label}</div>
            <div className="kpi-value" style={{ color: k.color }}>{k.value}</div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid-2 mb-4">
        {/* Assets by Status - Pie */}
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 16 }}>Assets by Status</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={kpis.assets_by_status}
                dataKey="count"
                nameKey="status"
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={3}
                stroke="none"
              >
                {kpis.assets_by_status.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)' }}
              />
              <Legend wrapperStyle={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Assets by Category - Bar */}
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 16 }}>Assets by Category</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={kpis.assets_by_category}>
              <XAxis dataKey="category" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)' }}
              />
              <Bar dataKey="count" fill="var(--primary)" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Row: Insights + Activity */}
      <div className="grid-2">
        {/* Smart Insights */}
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 16 }}>
            <TrendingUp size={16} style={{ display: 'inline', marginRight: 8, color: 'var(--primary)' }} />
            Smart Insights
          </h3>
          <div className="flex flex-col gap-2">
            {insights.length === 0 && <p className="text-sm text-muted">No actionable insights right now</p>}
            {insights.map((ins, i) => {
              const sev = SEVERITY_MAP[ins.severity] || SEVERITY_MAP.info;
              const Icon = sev.icon;
              return (
                <div key={i} style={{
                  padding: '10px 14px', borderRadius: 'var(--radius)', background: sev.bg,
                  border: '1px solid transparent', display: 'flex', alignItems: 'flex-start', gap: 10
                }}>
                  <Icon size={16} style={{ color: sev.color, marginTop: 2, flexShrink: 0 }} />
                  <div>
                    <span style={{ fontSize: '0.82rem', fontWeight: 600, color: sev.color }}>{ins.insight_type.replace(/_/g, ' ').toUpperCase()}</span>
                    <p style={{ fontSize: '0.82rem', color: 'var(--text)', marginTop: 2 }}>{ins.message}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Activity Feed */}
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 16 }}>
            <Activity size={16} style={{ display: 'inline', marginRight: 8, color: 'var(--primary)' }} />
            Recent Activity
          </h3>
          <div className="flex flex-col gap-2">
            {activity.length === 0 && <p className="text-sm text-muted">No recent activity</p>}
            {activity.map((act, i) => (
              <div key={i} style={{
                padding: '8px 12px', borderRadius: 'var(--radius-sm)',
                background: 'var(--bg)', border: '1px solid var(--border)',
                display: 'flex', justifyContent: 'space-between', alignItems: 'center'
              }}>
                <div>
                  <span style={{ fontSize: '0.78rem', fontWeight: 600 }}>{act.action.replace(/_/g, ' ')}</span>
                  {act.description && <p className="text-xs text-muted">{act.description}</p>}
                </div>
                <span className="text-xs text-muted">{new Date(act.created_at).toLocaleString('en-IN', {
                  day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
                })}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

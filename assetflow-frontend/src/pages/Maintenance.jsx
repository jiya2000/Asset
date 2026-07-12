import { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Wrench, Plus, X, CheckCircle, Play, CheckCheck, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';

const STATUS_MAP = {
  PENDING: 'badge-warning',
  APPROVED: 'badge-info',
  IN_PROGRESS: 'badge-primary',
  RESOLVED: 'badge-success',
  CANCELLED: 'badge-danger',
};

const PRIORITY_MAP = {
  LOW: 'badge-ghost',
  MEDIUM: 'badge-info',
  HIGH: 'badge-warning',
  CRITICAL: 'badge-danger',
};

const STATUS_OPTIONS = ['', 'PENDING', 'APPROVED', 'IN_PROGRESS', 'RESOLVED'];
const PRIORITY_OPTIONS = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

export default function Maintenance() {
  const { canApprove } = useAuth();
  const [requests, setRequests] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showResolveModal, setShowResolveModal] = useState(null);
  const [resolveNotes, setResolveNotes] = useState('');
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ asset_id: '', title: '', description: '', priority: 'MEDIUM' });

  const fetchRequests = async () => {
    const params = {};
    if (statusFilter) params.status = statusFilter;
    const res = await api.get('/maintenance/', { params });
    setRequests(res.data);
  };

  useEffect(() => { fetchRequests(); }, [statusFilter]);

  const fetchAssets = async () => {
    const res = await api.get('/assets/', { params: { page_size: 100 } });
    setAssets(res.data.items);
  };

  const createRequest = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/maintenance/', {
        asset_id: parseInt(form.asset_id),
        title: form.title,
        description: form.description || undefined,
        priority: form.priority,
      });
      toast.success('Maintenance request created');
      setShowModal(false);
      setForm({ asset_id: '', title: '', description: '', priority: 'MEDIUM' });
      fetchRequests();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed');
    } finally {
      setLoading(false);
    }
  };

  const approveRequest = async (id) => {
    await api.post(`/maintenance/${id}/approve`);
    toast.success('Request approved');
    fetchRequests();
  };

  const startMaintenance = async (id) => {
    await api.post(`/maintenance/${id}/start`);
    toast.success('Maintenance started');
    fetchRequests();
  };

  const resolveRequest = async (id) => {
    if (!resolveNotes.trim()) { toast.error('Resolution notes required'); return; }
    await api.post(`/maintenance/${id}/resolve`, { resolution_notes: resolveNotes });
    toast.success('Request resolved');
    setShowResolveModal(null);
    setResolveNotes('');
    fetchRequests();
  };

  const getNextAction = (req) => {
    if (req.status === 'PENDING' && canApprove) {
      return <button className="btn btn-success btn-sm" onClick={() => approveRequest(req.id)}><CheckCircle size={14} /> Approve</button>;
    }
    if (req.status === 'APPROVED' && canApprove) {
      return <button className="btn btn-primary btn-sm" onClick={() => startMaintenance(req.id)}><Play size={14} /> Start Work</button>;
    }
    if (req.status === 'IN_PROGRESS' && canApprove) {
      return <button className="btn btn-success btn-sm" onClick={() => { setShowResolveModal(req.id); setResolveNotes(''); }}>
        <CheckCheck size={14} /> Resolve
      </button>;
    }
    return null;
  };

  return (
    <div>
      <div className="page-header page-header-actions">
        <div>
          <h1>Maintenance</h1>
          <p>{requests.length} requests</p>
        </div>
        <button className="btn btn-primary" onClick={() => { fetchAssets(); setShowModal(true); }}>
          <Plus size={16} /> New Request
        </button>
      </div>

      {/* Status Filter Tabs */}
      <div className="tabs">
        {STATUS_OPTIONS.map(s => (
          <button key={s} className={`tab ${statusFilter === s ? 'active' : ''}`}
            onClick={() => setStatusFilter(s)}>
            {s || 'All'}
          </button>
        ))}
      </div>

      {/* Request List */}
      <div className="flex flex-col gap-3">
        {requests.length === 0 && (
          <div className="empty-state"><Wrench size={40} /><h3>No maintenance requests</h3><p>All systems operational</p></div>
        )}
        {requests.map(req => (
          <div key={req.id} className="card" style={{
            borderLeft: `3px solid var(--${req.priority === 'CRITICAL' ? 'danger' : req.priority === 'HIGH' ? 'warning' : 'primary'})`
          }}>
            <div className="flex items-center justify-between">
              <div style={{ flex: 1 }}>
                <div className="flex items-center gap-2">
                  <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>{req.title}</span>
                  <span className={`badge ${STATUS_MAP[req.status]}`}>{req.status.replace('_', ' ')}</span>
                  <span className={`badge ${PRIORITY_MAP[req.priority]}`}>{req.priority}</span>
                </div>
                <div className="flex items-center gap-3 mt-2 text-sm text-muted">
                  <span>Asset #{req.asset_id}</span>
                  <span>Requested: {new Date(req.created_at).toLocaleDateString('en-IN')}</span>
                  {req.description && <span>{req.description}</span>}
                  {req.resolution_notes && <span style={{ color: 'var(--success)' }}>✓ {req.resolution_notes}</span>}
                </div>
              </div>
              {getNextAction(req)}
            </div>
          </div>
        ))}
      </div>

      {/* New Request Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && setShowModal(false)}>
          <div className="modal animate-slide">
            <div className="flex items-center justify-between mb-4">
              <h2>New Maintenance Request</h2>
              <button className="btn btn-ghost btn-icon" onClick={() => setShowModal(false)}><X size={18} /></button>
            </div>
            <form onSubmit={createRequest}>
              <div className="form-group">
                <label>Asset *</label>
                <select className="form-input" value={form.asset_id}
                  onChange={e => setForm({ ...form, asset_id: e.target.value })} required>
                  <option value="">Select asset</option>
                  {assets.map(a => <option key={a.id} value={a.id}>{a.asset_tag} — {a.name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Title *</label>
                <input className="form-input" placeholder="Keyboard malfunction" value={form.title}
                  onChange={e => setForm({ ...form, title: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea className="form-input" placeholder="Detailed description of the issue" value={form.description}
                  onChange={e => setForm({ ...form, description: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Priority</label>
                <select className="form-input" value={form.priority}
                  onChange={e => setForm({ ...form, priority: e.target.value })}>
                  {PRIORITY_OPTIONS.map(p => <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-ghost" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Creating...' : 'Submit Request'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Resolve Modal */}
      {showResolveModal && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && setShowResolveModal(null)}>
          <div className="modal animate-slide">
            <h2>Resolve Maintenance Request</h2>
            <div className="form-group mt-4">
              <label>Resolution Notes *</label>
              <textarea className="form-input" placeholder="Describe what was done to resolve the issue..."
                value={resolveNotes} onChange={e => setResolveNotes(e.target.value)} rows={4} />
            </div>
            <div className="modal-actions">
              <button className="btn btn-ghost" onClick={() => setShowResolveModal(null)}>Cancel</button>
              <button className="btn btn-success" onClick={() => resolveRequest(showResolveModal)}>
                <CheckCheck size={16} /> Mark Resolved
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

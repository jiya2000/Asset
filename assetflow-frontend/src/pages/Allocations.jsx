import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import {
  ArrowLeftRight, Plus, X, CheckCircle, RotateCcw, Send,
  Clock, AlertTriangle, User, Package
} from 'lucide-react';
import toast from 'react-hot-toast';

const ALLOC_STATUS_MAP = {
  PENDING: 'badge-warning',
  ACTIVE: 'badge-success',
  RETURNED: 'badge-ghost',
  CANCELLED: 'badge-danger',
};

const TRANSFER_STATUS_MAP = {
  PENDING: 'badge-warning',
  APPROVED: 'badge-info',
  COMPLETED: 'badge-success',
  REJECTED: 'badge-danger',
};

export default function Allocations() {
  const { canApprove } = useAuth();
  const [tab, setTab] = useState('active');
  const [allocations, setAllocations] = useState([]);
  const [pendingData, setPendingData] = useState({ pending_allocations: [], pending_transfers: [] });
  const [transfers, setTransfers] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [availableAssets, setAvailableAssets] = useState([]);
  const [allAssets, setAllAssets] = useState([]);
  const [showAllocModal, setShowAllocModal] = useState(false);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [loading, setLoading] = useState(false);

  const [allocForm, setAllocForm] = useState({
    asset_id: '', employee_id: '', expected_return: '', purpose: '', notes: ''
  });
  const [transferForm, setTransferForm] = useState({
    asset_id: '', from_employee_id: '', to_employee_id: '', reason: ''
  });

  const [searchParams, setSearchParams] = useSearchParams();

  const fetchAll = useCallback(async () => {
    try {
      const [allocRes, empRes] = await Promise.all([
        api.get('/allocations/'),
        api.get('/auth/employees'),
      ]);
      setAllocations(allocRes.data);
      setEmployees(empRes.data);

      if (canApprove) {
        const pendingRes = await api.get('/allocations/pending');
        setPendingData(pendingRes.data);
      }

      const transferRes = await api.get('/allocations/transfers/all');
      setTransfers(transferRes.data);
    } catch (err) {
      console.error('Failed to fetch allocations', err);
    }
  }, [canApprove]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  useEffect(() => {
    if (searchParams.get('new')) {
      fetchAvailableAssets();
      setShowAllocModal(true);
      searchParams.delete('new');
      setSearchParams(searchParams, { replace: true });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, setSearchParams]);

  const fetchAvailableAssets = async () => {
    const res = await api.get('/assets/', { params: { status: 'AVAILABLE', page_size: 100 } });
    setAvailableAssets(res.data.items);
  };

  const fetchAllAssets = async () => {
    const res = await api.get('/assets/', { params: { status: 'ALLOCATED', page_size: 100 } });
    setAllAssets(res.data.items);
  };

  const getEmployee = (id) => employees.find(e => e.id === id);
  const getEmployeeName = (id) => {
    const emp = getEmployee(id);
    return emp ? `${emp.first_name} ${emp.last_name}` : `Employee #${id}`;
  };

  const isOverdue = (alloc) => {
    if (alloc.status !== 'ACTIVE' || !alloc.expected_return) return false;
    return new Date(alloc.expected_return) < new Date();
  };

  // Actions
  const approveAllocation = async (id) => {
    await api.post(`/allocations/${id}/approve`);
    toast.success('Allocation approved');
    fetchAll();
  };

  const returnAsset = async (id) => {
    await api.post(`/allocations/${id}/return`, { notes: '' });
    toast.success('Asset returned');
    fetchAll();
  };

  const approveTransfer = async (id) => {
    await api.post(`/allocations/transfers/${id}/approve`);
    toast.success('Transfer approved');
    fetchAll();
  };

  const createAllocation = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        asset_id: parseInt(allocForm.asset_id),
        employee_id: parseInt(allocForm.employee_id),
      };
      if (allocForm.expected_return) payload.expected_return = new Date(allocForm.expected_return).toISOString();
      if (allocForm.purpose) payload.purpose = allocForm.purpose;
      if (allocForm.notes) payload.notes = allocForm.notes;
      await api.post('/allocations/', payload);
      toast.success('Allocation created');
      setShowAllocModal(false);
      setAllocForm({ asset_id: '', employee_id: '', expected_return: '', purpose: '', notes: '' });
      fetchAll();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed');
    } finally {
      setLoading(false);
    }
  };

  const createTransfer = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        asset_id: parseInt(transferForm.asset_id),
        from_employee_id: parseInt(transferForm.from_employee_id),
        to_employee_id: parseInt(transferForm.to_employee_id),
      };
      if (transferForm.reason) payload.reason = transferForm.reason;
      await api.post('/allocations/transfers', payload);
      toast.success('Transfer initiated');
      setShowTransferModal(false);
      setTransferForm({ asset_id: '', from_employee_id: '', to_employee_id: '', reason: '' });
      fetchAll();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed');
    } finally {
      setLoading(false);
    }
  };

  // Filtered data
  const activeAllocs = allocations.filter(a => a.status === 'ACTIVE');
  const returnedAllocs = allocations.filter(a => a.status === 'RETURNED');

  const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '—';

  return (
    <div>
      <div className="page-header page-header-actions">
        <div>
          <h1>Allocations & Transfers</h1>
          <p>{activeAllocs.length} active allocations</p>
        </div>
        {canApprove && (
          <div className="flex gap-2">
            <button className="btn btn-primary" onClick={() => { fetchAvailableAssets(); setShowAllocModal(true); }}>
              <Plus size={16} /> Allocate Asset
            </button>
            <button className="btn btn-ghost" onClick={() => { fetchAllAssets(); setShowTransferModal(true); }}>
              <ArrowLeftRight size={16} /> Transfer
            </button>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button className={`tab ${tab === 'active' ? 'active' : ''}`} onClick={() => setTab('active')}>
          Active ({activeAllocs.length})
        </button>
        {canApprove && (
          <button className={`tab ${tab === 'pending' ? 'active' : ''}`} onClick={() => setTab('pending')}>
            Pending ({pendingData.pending_allocations.length + pendingData.pending_transfers.length})
          </button>
        )}
        <button className={`tab ${tab === 'returned' ? 'active' : ''}`} onClick={() => setTab('returned')}>
          Returned ({returnedAllocs.length})
        </button>
        <button className={`tab ${tab === 'transfers' ? 'active' : ''}`} onClick={() => setTab('transfers')}>
          Transfers ({transfers.length})
        </button>
      </div>

      {/* Active Tab */}
      {tab === 'active' && (
        <div className="flex flex-col gap-3">
          {activeAllocs.length === 0 && (
            <div className="empty-state"><Package size={40} /><h3>No active allocations</h3><p>Allocate an asset to get started</p></div>
          )}
          {activeAllocs.map(a => (
            <div key={a.id} className="card" style={{ borderLeft: isOverdue(a) ? '3px solid var(--danger)' : '3px solid var(--success)' }}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>Asset #{a.asset_id}</span>
                      <span className={`badge ${ALLOC_STATUS_MAP[a.status]}`}>{a.status}</span>
                      {isOverdue(a) && <span className="badge badge-danger"><AlertTriangle size={10} /> OVERDUE</span>}
                    </div>
                    <div className="flex items-center gap-3 mt-2 text-sm text-muted">
                      <span className="flex items-center gap-1"><User size={13} /> {getEmployeeName(a.employee_id)}</span>
                      <span>Allocated: {formatDate(a.allocated_at)}</span>
                      {a.expected_return && <span>Return by: {formatDate(a.expected_return)}</span>}
                      {a.purpose && <span>Purpose: {a.purpose}</span>}
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button className="btn btn-warning btn-sm" onClick={() => returnAsset(a.id)}>
                    <RotateCcw size={14} /> Return
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pending Tab */}
      {tab === 'pending' && canApprove && (
        <div className="flex flex-col gap-3">
          {pendingData.pending_allocations.length === 0 && pendingData.pending_transfers.length === 0 && (
            <div className="empty-state"><CheckCircle size={40} /><h3>All caught up!</h3><p>No pending approvals</p></div>
          )}
          {pendingData.pending_allocations.map(a => (
            <div key={`alloc-${a.id}`} className="card" style={{ borderLeft: '3px solid var(--warning)' }}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="badge badge-primary">ALLOCATION</span>
                    <span style={{ fontWeight: 700 }}>Asset #{a.asset_id}</span>
                    <span className="badge badge-warning">PENDING</span>
                  </div>
                  <p className="text-sm text-muted mt-2">
                    Assign to: {getEmployeeName(a.employee_id)} • {formatDate(a.created_at)}
                    {a.purpose && ` • ${a.purpose}`}
                  </p>
                </div>
                <button className="btn btn-success btn-sm" onClick={() => approveAllocation(a.id)}>
                  <CheckCircle size={14} /> Approve
                </button>
              </div>
            </div>
          ))}
          {pendingData.pending_transfers.map(t => (
            <div key={`xfer-${t.id}`} className="card" style={{ borderLeft: '3px solid var(--info)' }}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="badge badge-info">TRANSFER</span>
                    <span style={{ fontWeight: 700 }}>Asset #{t.asset_id}</span>
                    <span className="badge badge-warning">PENDING</span>
                  </div>
                  <p className="text-sm text-muted mt-2">
                    {getEmployeeName(t.from_employee_id)} → {getEmployeeName(t.to_employee_id)}
                    {t.reason && ` • ${t.reason}`}
                  </p>
                </div>
                <button className="btn btn-success btn-sm" onClick={() => approveTransfer(t.id)}>
                  <CheckCircle size={14} /> Approve
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Returned Tab */}
      {tab === 'returned' && (
        <div className="table-container">
          <table>
            <thead>
              <tr><th>Asset</th><th>Employee</th><th>Allocated</th><th>Returned</th><th>Purpose</th></tr>
            </thead>
            <tbody>
              {returnedAllocs.map(a => (
                <tr key={a.id}>
                  <td className="font-mono text-sm">Asset #{a.asset_id}</td>
                  <td>{getEmployeeName(a.employee_id)}</td>
                  <td className="text-sm text-muted">{formatDate(a.allocated_at)}</td>
                  <td className="text-sm text-muted">{formatDate(a.actual_return)}</td>
                  <td className="text-sm text-muted">{a.purpose || '—'}</td>
                </tr>
              ))}
              {returnedAllocs.length === 0 && (
                <tr><td colSpan={5} className="empty-state"><h3>No returned allocations</h3></td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Transfers Tab */}
      {tab === 'transfers' && (
        <div className="flex flex-col gap-3">
          {transfers.length === 0 && (
            <div className="empty-state"><ArrowLeftRight size={40} /><h3>No transfers</h3></div>
          )}
          {transfers.map(t => (
            <div key={t.id} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span style={{ fontWeight: 700 }}>Asset #{t.asset_id}</span>
                    <span className={`badge ${TRANSFER_STATUS_MAP[t.status]}`}>{t.status}</span>
                  </div>
                  <p className="text-sm text-muted mt-2">
                    {getEmployeeName(t.from_employee_id)} → {getEmployeeName(t.to_employee_id)}
                    {t.reason && ` • ${t.reason}`} • {formatDate(t.created_at)}
                  </p>
                </div>
                {t.status === 'PENDING' && canApprove && (
                  <button className="btn btn-success btn-sm" onClick={() => approveTransfer(t.id)}>
                    <CheckCircle size={14} /> Approve
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Allocate Modal */}
      {showAllocModal && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && setShowAllocModal(false)}>
          <div className="modal animate-slide">
            <div className="flex items-center justify-between mb-4">
              <h2>Allocate Asset</h2>
              <button className="btn btn-ghost btn-icon" onClick={() => setShowAllocModal(false)}><X size={18} /></button>
            </div>
            <form onSubmit={createAllocation}>
              <div className="form-group">
                <label>Asset *</label>
                <select className="form-input" value={allocForm.asset_id}
                  onChange={e => setAllocForm({ ...allocForm, asset_id: e.target.value })} required>
                  <option value="">Select an available asset</option>
                  {availableAssets.map(a => (
                    <option key={a.id} value={a.id}>{a.asset_tag} — {a.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Employee *</label>
                <select className="form-input" value={allocForm.employee_id}
                  onChange={e => setAllocForm({ ...allocForm, employee_id: e.target.value })} required>
                  <option value="">Select employee</option>
                  {employees.map(emp => (
                    <option key={emp.id} value={emp.id}>{emp.first_name} {emp.last_name} ({emp.emp_code})</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Expected Return Date</label>
                <input type="datetime-local" className="form-input" value={allocForm.expected_return}
                  onChange={e => setAllocForm({ ...allocForm, expected_return: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Purpose</label>
                <input className="form-input" placeholder="Project work, client demo..." value={allocForm.purpose}
                  onChange={e => setAllocForm({ ...allocForm, purpose: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Notes</label>
                <textarea className="form-input" placeholder="Any additional notes" value={allocForm.notes}
                  onChange={e => setAllocForm({ ...allocForm, notes: e.target.value })} />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-ghost" onClick={() => setShowAllocModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Creating...' : 'Allocate Asset'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Transfer Modal */}
      {showTransferModal && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && setShowTransferModal(false)}>
          <div className="modal animate-slide">
            <div className="flex items-center justify-between mb-4">
              <h2>Transfer Asset</h2>
              <button className="btn btn-ghost btn-icon" onClick={() => setShowTransferModal(false)}><X size={18} /></button>
            </div>
            <form onSubmit={createTransfer}>
              <div className="form-group">
                <label>Asset (currently allocated) *</label>
                <select className="form-input" value={transferForm.asset_id}
                  onChange={e => {
                    const assetId = e.target.value;
                    const alloc = allocations.find(a => a.asset_id === parseInt(assetId) && a.status === 'ACTIVE');
                    setTransferForm({
                      ...transferForm,
                      asset_id: assetId,
                      from_employee_id: alloc ? String(alloc.employee_id) : '',
                    });
                  }} required>
                  <option value="">Select an allocated asset</option>
                  {allAssets.map(a => (
                    <option key={a.id} value={a.id}>{a.asset_tag} — {a.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>From Employee</label>
                <select className="form-input" value={transferForm.from_employee_id}
                  onChange={e => setTransferForm({ ...transferForm, from_employee_id: e.target.value })} required>
                  <option value="">Auto-filled from asset</option>
                  {employees.map(emp => (
                    <option key={emp.id} value={emp.id}>{emp.first_name} {emp.last_name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>To Employee *</label>
                <select className="form-input" value={transferForm.to_employee_id}
                  onChange={e => setTransferForm({ ...transferForm, to_employee_id: e.target.value })} required>
                  <option value="">Select destination employee</option>
                  {employees.filter(emp => String(emp.id) !== transferForm.from_employee_id).map(emp => (
                    <option key={emp.id} value={emp.id}>{emp.first_name} {emp.last_name} ({emp.emp_code})</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Reason</label>
                <textarea className="form-input" placeholder="Reason for transfer" value={transferForm.reason}
                  onChange={e => setTransferForm({ ...transferForm, reason: e.target.value })} />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-ghost" onClick={() => setShowTransferModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Creating...' : 'Initiate Transfer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

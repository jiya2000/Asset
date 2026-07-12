import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Package, Plus, Search, X, Edit3, Trash2, QrCode, Printer } from 'lucide-react';
import toast from 'react-hot-toast';

const STATUS_MAP = {
  AVAILABLE: 'badge-success',
  ALLOCATED: 'badge-info',
  UNDER_MAINTENANCE: 'badge-warning',
  RETIRED: 'badge-ghost',
};

const CONDITION_OPTIONS = ['NEW', 'GOOD', 'FAIR', 'POOR', 'DAMAGED'];
const STATUS_OPTIONS = ['AVAILABLE', 'ALLOCATED', 'UNDER_MAINTENANCE', 'RETIRED'];

export default function Assets() {
  const { canApprove } = useAuth();
  const [assets, setAssets] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [categories, setCategories] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [showQrModal, setShowQrModal] = useState(false);
  const [qrAsset, setQrAsset] = useState(null);
  const [editAsset, setEditAsset] = useState(null);
  const [loading, setLoading] = useState(false);

  const emptyForm = {
    asset_tag: '', name: '', description: '', serial_number: '',
    category_id: '', condition: 'NEW', purchase_date: '', purchase_cost: '',
    warranty_expiry: '', location: '', department_id: '',
  };
  const [form, setForm] = useState(emptyForm);

  const [searchParams, setSearchParams] = useSearchParams();

  const fetchAssets = useCallback(async () => {
    const params = { page, page_size: 15 };
    if (search) params.search = search;
    if (statusFilter) params.status = statusFilter;
    if (categoryFilter) params.category_id = categoryFilter;
    const res = await api.get('/assets/', { params });
    setAssets(res.data.items);
    setTotal(res.data.total);
    setTotalPages(res.data.total_pages);
  }, [page, search, statusFilter, categoryFilter]);

  useEffect(() => { fetchAssets(); }, [fetchAssets]);

  useEffect(() => {
    if (searchParams.get('new')) {
      setShowModal(true);
      searchParams.delete('new');
      setSearchParams(searchParams, { replace: true });
    }
  }, [searchParams, setSearchParams]);

  useEffect(() => {
    Promise.all([api.get('/assets/categories'), api.get('/auth/departments')])
      .then(([c, d]) => { setCategories(c.data); setDepartments(d.data); });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = { ...form, category_id: parseInt(form.category_id) };
      if (form.department_id) payload.department_id = parseInt(form.department_id);
      else delete payload.department_id;
      if (form.purchase_cost) payload.purchase_cost = parseFloat(form.purchase_cost);
      else delete payload.purchase_cost;
      if (!form.purchase_date) delete payload.purchase_date;
      if (!form.warranty_expiry) delete payload.warranty_expiry;
      if (!form.description) delete payload.description;
      if (!form.location) delete payload.location;

      if (editAsset) {
        const { asset_tag, serial_number, ...updatePayload } = payload;
        await api.patch(`/assets/${editAsset.id}`, updatePayload);
        toast.success('Asset updated');
      } else {
        await api.post('/assets/', payload);
        toast.success('Asset registered');
      }
      setShowModal(false);
      setEditAsset(null);
      setForm(emptyForm);
      fetchAssets();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (asset) => {
    setEditAsset(asset);
    setForm({
      asset_tag: asset.asset_tag,
      name: asset.name,
      description: asset.description || '',
      serial_number: asset.serial_number,
      category_id: String(asset.category_id),
      condition: asset.condition,
      purchase_date: asset.purchase_date || '',
      purchase_cost: asset.purchase_cost || '',
      warranty_expiry: asset.warranty_expiry || '',
      location: asset.location || '',
      department_id: asset.department_id ? String(asset.department_id) : '',
    });
    setShowModal(true);
  };

  const handleDelete = async (asset) => {
    if (!confirm(`Retire asset ${asset.asset_tag}?`)) return;
    await api.delete(`/assets/${asset.id}`);
    toast.success('Asset retired');
    fetchAssets();
  };

  const handleShowQr = (asset) => {
    setQrAsset(asset);
    setShowQrModal(true);
  };

  const getCategoryName = (id) => categories.find(c => c.id === id)?.name || '—';

  return (
    <div>
      <div className="page-header page-header-actions">
        <div>
          <h1>Asset Registry</h1>
          <p>{total} assets total</p>
        </div>
        {canApprove && (
          <button className="btn btn-primary" onClick={() => { setEditAsset(null); setForm(emptyForm); setShowModal(true); }}>
            <Plus size={16} /> Register Asset
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="filters-bar">
        <div className="search-input">
          <Search size={16} />
          <input className="form-input" placeholder="Search name, tag, serial..."
            value={search} onChange={e => { setSearch(e.target.value); setPage(1); }} />
        </div>
        <select className="form-input" value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1); }}>
          <option value="">All Statuses</option>
          {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
        </select>
        <select className="form-input" value={categoryFilter} onChange={e => { setCategoryFilter(e.target.value); setPage(1); }}>
          <option value="">All Categories</option>
          {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Asset Tag</th>
              <th>Name</th>
              <th>Category</th>
              <th>Status</th>
              <th>Condition</th>
              <th>Location</th>
              {canApprove && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {assets.map(a => (
              <tr key={a.id}>
                <td><span className="font-mono text-sm">{a.asset_tag}</span></td>
                <td style={{ fontWeight: 600 }}>{a.name}</td>
                <td>{getCategoryName(a.category_id)}</td>
                <td><span className={`badge ${STATUS_MAP[a.status] || 'badge-ghost'}`}>{a.status.replace('_', ' ')}</span></td>
                <td><span className="text-sm text-muted">{a.condition}</span></td>
                <td><span className="text-sm text-muted">{a.location || '—'}</span></td>
                {canApprove && (
                  <td>
                    <div className="flex gap-2">
                      <button className="btn btn-ghost btn-sm" onClick={() => handleShowQr(a)} title="Show QR Code"><QrCode size={14} /></button>
                      <button className="btn btn-ghost btn-sm" onClick={() => handleEdit(a)} title="Edit"><Edit3 size={14} /></button>
                      <button className="btn btn-ghost btn-sm" onClick={() => handleDelete(a)} title="Delete"><Trash2 size={14} /></button>
                    </div>
                  </td>
                )}
              </tr>
            ))}
            {assets.length === 0 && (
              <tr><td colSpan={canApprove ? 7 : 6} className="empty-state"><h3>No assets found</h3><p>Try adjusting your filters</p></td></tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pagination">
          <button disabled={page <= 1} onClick={() => setPage(page - 1)}>Prev</button>
          {Array.from({ length: totalPages }, (_, i) => (
            <button key={i + 1} className={page === i + 1 ? 'active' : ''} onClick={() => setPage(i + 1)}>{i + 1}</button>
          ))}
          <button disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && setShowModal(false)}>
          <div className="modal modal-lg animate-slide">
            <div className="flex items-center justify-between mb-4">
              <h2>{editAsset ? 'Edit Asset' : 'Register New Asset'}</h2>
              <button className="btn btn-ghost btn-icon" onClick={() => setShowModal(false)}><X size={18} /></button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label>Asset Tag *</label>
                  <input className="form-input" placeholder="AST-LAP-001" value={form.asset_tag}
                    onChange={e => setForm({ ...form, asset_tag: e.target.value })} required disabled={!!editAsset} />
                </div>
                <div className="form-group">
                  <label>Serial Number *</label>
                  <input className="form-input" placeholder="SN12345" value={form.serial_number}
                    onChange={e => setForm({ ...form, serial_number: e.target.value })} required disabled={!!editAsset} />
                </div>
              </div>
              <div className="form-group">
                <label>Name *</label>
                <input className="form-input" placeholder="MacBook Pro 16-inch" value={form.name}
                  onChange={e => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea className="form-input" placeholder="Optional description" value={form.description}
                  onChange={e => setForm({ ...form, description: e.target.value })} />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Category *</label>
                  <select className="form-input" value={form.category_id}
                    onChange={e => setForm({ ...form, category_id: e.target.value })} required>
                    <option value="">Select category</option>
                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Condition</label>
                  <select className="form-input" value={form.condition}
                    onChange={e => setForm({ ...form, condition: e.target.value })}>
                    {CONDITION_OPTIONS.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Purchase Date</label>
                  <input type="date" className="form-input" value={form.purchase_date}
                    onChange={e => setForm({ ...form, purchase_date: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Purchase Cost (₹)</label>
                  <input type="number" className="form-input" placeholder="0.00" value={form.purchase_cost}
                    onChange={e => setForm({ ...form, purchase_cost: e.target.value })} />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Warranty Expiry</label>
                  <input type="date" className="form-input" value={form.warranty_expiry}
                    onChange={e => setForm({ ...form, warranty_expiry: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Location</label>
                  <input className="form-input" placeholder="Floor 3, Room 301" value={form.location}
                    onChange={e => setForm({ ...form, location: e.target.value })} />
                </div>
              </div>
              <div className="form-group">
                <label>Department</label>
                <select className="form-input" value={form.department_id}
                  onChange={e => setForm({ ...form, department_id: e.target.value })}>
                  <option value="">No department</option>
                  {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-ghost" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Saving...' : editAsset ? 'Update Asset' : 'Register Asset'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* QR Code Modal */}
      {showQrModal && qrAsset && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && setShowQrModal(false)}>
          <div className="modal animate-slide" style={{ maxWidth: '400px', textAlign: 'center' }}>
            <div className="flex items-center justify-between mb-4">
              <h2>Asset QR Code</h2>
              <button className="btn btn-ghost btn-icon" onClick={() => setShowQrModal(false)}><X size={18} /></button>
            </div>
            <div className="p-6 bg-white rounded-lg inline-block border border-gray-200">
              <img 
                src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrAsset.asset_tag)}`} 
                alt="QR Code" 
                style={{ width: 200, height: 200, margin: '0 auto', display: 'block' }} 
              />
              <div className="mt-4 font-mono font-bold text-lg text-black">{qrAsset.asset_tag}</div>
              <div className="text-sm text-gray-500 mt-1">{qrAsset.name}</div>
            </div>
            <div className="modal-actions mt-6">
              <button type="button" className="btn btn-ghost" onClick={() => setShowQrModal(false)}>Close</button>
              <button type="button" className="btn btn-primary" onClick={() => window.print()}>
                <Printer size={16} style={{ marginRight: 8 }} /> Print Tag
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

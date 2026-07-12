import { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Building2, Tag, Plus, X } from 'lucide-react';
import toast from 'react-hot-toast';

export default function OrgSetup() {
  const { canApprove } = useAuth();
  const [departments, setDepartments] = useState([]);
  const [categories, setCategories] = useState([]);
  const [showDeptForm, setShowDeptForm] = useState(false);
  const [showCatForm, setShowCatForm] = useState(false);
  const [deptForm, setDeptForm] = useState({ name: '', code: '', description: '' });
  const [catForm, setCatForm] = useState({ name: '', code: '', description: '' });
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    const [dRes, cRes] = await Promise.all([
      api.get('/auth/departments'),
      api.get('/assets/categories'),
    ]);
    setDepartments(dRes.data);
    setCategories(cRes.data);
  };

  useEffect(() => { fetchData(); }, []);

  const createDept = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/auth/departments', deptForm);
      toast.success('Department created');
      setDeptForm({ name: '', code: '', description: '' });
      setShowDeptForm(false);
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed');
    } finally {
      setLoading(false);
    }
  };

  const createCat = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/assets/categories', catForm);
      toast.success('Category created');
      setCatForm({ name: '', code: '', description: '' });
      setShowCatForm(false);
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Organization Setup</h1>
        <p>Manage departments and asset categories</p>
      </div>

      <div className="grid-2">
        {/* Departments */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Building2 size={20} style={{ color: 'var(--primary)' }} />
              <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Departments</h2>
            </div>
            {canApprove && (
              <button className="btn btn-primary btn-sm" onClick={() => setShowDeptForm(!showDeptForm)}>
                {showDeptForm ? <X size={14} /> : <Plus size={14} />}
                {showDeptForm ? 'Cancel' : 'Add'}
              </button>
            )}
          </div>

          {showDeptForm && (
            <form onSubmit={createDept} className="card-glass mb-4" style={{ padding: 16 }}>
              <div className="form-row">
                <div className="form-group">
                  <label>Name</label>
                  <input className="form-input" placeholder="Engineering" value={deptForm.name}
                    onChange={e => setDeptForm({ ...deptForm, name: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>Code</label>
                  <input className="form-input" placeholder="ENG" value={deptForm.code}
                    onChange={e => setDeptForm({ ...deptForm, code: e.target.value })} required maxLength={10} />
                </div>
              </div>
              <div className="form-group">
                <label>Description</label>
                <input className="form-input" placeholder="Optional description" value={deptForm.description}
                  onChange={e => setDeptForm({ ...deptForm, description: e.target.value })} />
              </div>
              <button type="submit" className="btn btn-primary btn-sm" disabled={loading}>
                {loading ? 'Creating...' : 'Create Department'}
              </button>
            </form>
          )}

          <div className="flex flex-col gap-2">
            {departments.map(d => (
              <div key={d.id} className="flex items-center justify-between" style={{
                padding: '10px 14px', background: 'var(--bg)', borderRadius: 'var(--radius)', border: '1px solid var(--border)'
              }}>
                <div>
                  <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>{d.name}</span>
                  <span className="badge badge-ghost" style={{ marginLeft: 8 }}>{d.code}</span>
                </div>
                {d.description && <span className="text-xs text-muted truncate" style={{ maxWidth: 150 }}>{d.description}</span>}
              </div>
            ))}
            {departments.length === 0 && (
              <p className="text-sm text-muted" style={{ textAlign: 'center', padding: 20 }}>No departments yet</p>
            )}
          </div>
        </div>

        {/* Categories */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Tag size={20} style={{ color: 'var(--warning)' }} />
              <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Asset Categories</h2>
            </div>
            {canApprove && (
              <button className="btn btn-primary btn-sm" onClick={() => setShowCatForm(!showCatForm)}>
                {showCatForm ? <X size={14} /> : <Plus size={14} />}
                {showCatForm ? 'Cancel' : 'Add'}
              </button>
            )}
          </div>

          {showCatForm && (
            <form onSubmit={createCat} className="card-glass mb-4" style={{ padding: 16 }}>
              <div className="form-row">
                <div className="form-group">
                  <label>Name</label>
                  <input className="form-input" placeholder="Laptops" value={catForm.name}
                    onChange={e => setCatForm({ ...catForm, name: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>Code</label>
                  <input className="form-input" placeholder="LAP" value={catForm.code}
                    onChange={e => setCatForm({ ...catForm, code: e.target.value })} required maxLength={10} />
                </div>
              </div>
              <div className="form-group">
                <label>Description</label>
                <input className="form-input" placeholder="Optional description" value={catForm.description}
                  onChange={e => setCatForm({ ...catForm, description: e.target.value })} />
              </div>
              <button type="submit" className="btn btn-primary btn-sm" disabled={loading}>
                {loading ? 'Creating...' : 'Create Category'}
              </button>
            </form>
          )}

          <div className="flex flex-col gap-2">
            {categories.map(c => (
              <div key={c.id} className="flex items-center justify-between" style={{
                padding: '10px 14px', background: 'var(--bg)', borderRadius: 'var(--radius)', border: '1px solid var(--border)'
              }}>
                <div>
                  <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>{c.name}</span>
                  <span className="badge badge-ghost" style={{ marginLeft: 8 }}>{c.code}</span>
                </div>
                {c.description && <span className="text-xs text-muted truncate" style={{ maxWidth: 150 }}>{c.description}</span>}
              </div>
            ))}
            {categories.length === 0 && (
              <p className="text-sm text-muted" style={{ textAlign: 'center', padding: 20 }}>No categories yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

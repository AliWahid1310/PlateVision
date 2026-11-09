'use client';

import { useState, useEffect } from 'react';
import { History, Search, Download } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function HistoryTable() {
  const [records, setRecords] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchHistory = async (query = '') => {
    setLoading(true);
    try {
      const url = query
        ? `${API_BASE}/api/history?limit=25&search=${encodeURIComponent(query)}`
        : `${API_BASE}/api/history?limit=25`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setRecords(data.records || []);
      }
    } catch (_) {}
    setLoading(false);
  };

  useEffect(() => { fetchHistory(); }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchHistory(search);
  };

  const handleExportCSV = () => {
    window.open(`${API_BASE}/api/export/csv`, '_blank');
  };

  if (records.length === 0 && !loading) return null;

  return (
    <div className="glass-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <History size={16} color="var(--accent-amber)" /> Detection History
        </h3>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <form onSubmit={handleSearch} style={{ display: 'flex', gap: '6px' }}>
            <div style={{ position: 'relative' }}>
              <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search plates..."
                style={{
                  padding: '6px 12px 6px 30px',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--text-primary)',
                  fontSize: '0.8125rem',
                  outline: 'none',
                  width: '160px'
                }}
              />
            </div>
          </form>
          <button type="button" className="btn-secondary" onClick={handleExportCSV} style={{ fontSize: '0.75rem', padding: '6px 10px' }}>
            <Download size={12} /> CSV
          </button>
        </div>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table className="history-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Plate</th>
              <th>Confidence</th>
              <th>Vehicle</th>
              <th>Color</th>
              <th>Latency</th>
            </tr>
          </thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.id}>
                <td>#{r.id}</td>
                <td style={{ fontWeight: '600', fontFamily: 'monospace', color: r.plate_detected ? 'var(--accent-emerald)' : 'var(--text-muted)' }}>
                  {r.plate_text || 'N/A'}
                </td>
                <td>{r.plate_confidence ? `${(r.plate_confidence * 100).toFixed(0)}%` : '-'}</td>
                <td>{r.vehicle_class || '-'}</td>
                <td>{r.vehicle_color || '-'}</td>
                <td>{r.processing_time_ms ? `${r.processing_time_ms}ms` : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

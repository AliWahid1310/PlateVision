'use client';

import { useState, useEffect } from 'react';
import { BarChart3, Target, Clock, Truck } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function StatsPanel() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/stats`);
        if (res.ok) setStats(await res.json());
      } catch (_) {}
    };
    fetchStats();
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, []);

  if (!stats) return null;

  const statItems = [
    { icon: <BarChart3 size={18} />, value: stats.total_scans, label: 'Total Scans' },
    { icon: <Target size={18} />, value: `${stats.detection_rate_pct}%`, label: 'Detection Rate' },
    { icon: <Clock size={18} />, value: `${stats.avg_processing_time_ms}ms`, label: 'Avg Latency' },
    { icon: <Truck size={18} />, value: stats.plates_detected, label: 'Plates Found' }
  ];

  return (
    <div className="glass-card">
      <h3 style={{ fontSize: '1rem', fontWeight: '700', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <BarChart3 size={16} color="var(--accent-violet)" /> Fleet Analytics
      </h3>
      <div className="stats-grid">
        {statItems.map((item, i) => (
          <div key={i} className="stat-card">
            <div style={{ color: 'var(--accent-cyan)', marginBottom: '6px' }}>{item.icon}</div>
            <div className="stat-value">{item.value}</div>
            <div className="stat-label">{item.label}</div>
          </div>
        ))}
      </div>
      {stats.fleet_distribution && Object.keys(stats.fleet_distribution).length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <h4 style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Vehicle Class Distribution
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {Object.entries(stats.fleet_distribution).map(([cls, count]) => (
              <span key={cls} className="vehicle-tag" style={{ fontSize: '0.75rem' }}>
                {cls}: <strong>{count}</strong>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

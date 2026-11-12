'use client';

import { ShieldCheck, Car, ScanLine, Tag, Gauge, CheckCircle2, AlertTriangle, MapPin } from 'lucide-react';

export default function ResultsPanel({ result }) {
  if (!result) {
    return (
      <div
        className="glass-card"
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '360px',
          textAlign: 'center',
          color: 'var(--text-muted)'
        }}
      >
        <ScanLine size={48} style={{ opacity: 0.3, marginBottom: '16px' }} />
        <h3 style={{ color: 'var(--text-secondary)', marginBottom: '6px' }}>No Results Yet</h3>
        <p style={{ fontSize: '0.875rem', maxWidth: '300px' }}>
          Select a vehicle image and hit &ldquo;Run ANPR Analysis&rdquo; to detect plates, vehicles, and colors.
        </p>
      </div>
    );
  }

  const { plate_text, plate_confidence, plate_detected, vehicles, vehicle_count, plate_image, plate_region, processing_time_ms, scan_id } = result;

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.125rem', fontWeight: '700', color: 'var(--text-primary)' }}>
            Detection Intelligence
          </h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
            Scan #{scan_id || '-'} &bull; {processing_time_ms ? `${processing_time_ms}ms` : 'N/A'}
          </p>
        </div>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '0.75rem',
          padding: '4px 10px',
          borderRadius: 'var(--radius-full)',
          background: plate_detected ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
          color: plate_detected ? '#34d399' : '#fb7185',
          fontWeight: '600'
        }}>
          {plate_detected ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
          {plate_detected ? 'Plate Detected' : 'No Plate'}
        </div>
      </div>

      {/* Plate Badge */}
      <div className="plate-hero-badge">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', fontWeight: '600' }}>
            Recognized License Plate
          </span>
          <div className="plate-text-display">
            {plate_text || (plate_detected ? 'UNREADABLE' : 'NONE')}
          </div>
          <div style={{ display: 'flex', gap: '16px', marginTop: '4px' }}>
            {plate_detected && (
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Gauge size={12} /> {(plate_confidence * 100).toFixed(1)}% confidence
              </span>
            )}
            {plate_region && plate_region !== 'Standard' && (
              <span style={{ fontSize: '0.75rem', color: 'var(--accent-amber)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <MapPin size={12} /> {plate_region}
              </span>
            )}
          </div>
        </div>
        {plate_image && (
          <div style={{ textAlign: 'center' }}>
            <div style={{
              width: '120px',
              height: '50px',
              borderRadius: 'var(--radius-sm)',
              overflow: 'hidden',
              border: '1px solid rgba(52, 211, 153, 0.4)',
              background: '#000',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <img src={`data:image/jpeg;base64,${plate_image}`} alt="Plate" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
            </div>
            <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '4px', display: 'block' }}>Cropped Region</span>
          </div>
        )}
      </div>

      {/* Vehicle List */}
      {vehicles && vehicles.length > 0 && (
        <div>
          <h3 style={{ fontSize: '0.875rem', fontWeight: '700', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Car size={16} color="var(--accent-cyan)" /> Detected Vehicles ({vehicle_count})
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {vehicles.map((v, i) => (
              <div key={i} className="vehicle-tag">
                <Tag size={14} color="var(--accent-violet)" />
                <div>
                  <div style={{ fontWeight: '600', fontSize: '0.875rem' }}>{v.class_name}</div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>
                    {(v.confidence * 100).toFixed(0)}% &bull; {v.color || 'Unknown color'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

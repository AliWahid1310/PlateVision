'use client';

import { ShieldCheck, Car, ScanLine, Tag, Gauge, CheckCircle2, AlertTriangle } from 'lucide-react';

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
          Select a vehicle picture and hit &ldquo;Run ANPR&rdquo; to see plate numbers and YOLO classifications.
        </p>
      </div>
    );
  }

  const { plate_text, plate_confidence, plate_detected, vehicles, vehicle_count, plate_image } = result;

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.125rem', fontWeight: '700', color: 'var(--text-primary)' }}>
            Detection Intelligence
          </h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
            Real-time inference breakdown
          </p>
        </div>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '0.75rem',
            padding: '4px 10px',
            borderRadius: 'var(--radius-full)',
            background: plate_detected ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
            color: plate_detected ? '#34d399' : '#fb7185',
            fontWeight: '600'
          }}
        >
          {plate_detected ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
          {plate_detected ? 'Plate Detected' : 'No Plate Identified'}
        </div>
      </div>

      {/* Plate Highlight Section */}
      <div className="plate-hero-badge">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)', fontWeight: '600' }}>
            Recognized License Plate
          </span>
          <div className="plate-text-display">
            {plate_text || (plate_detected ? 'TEXT UNREADABLE' : 'NONE DETECTED')}
          </div>
          {plate_detected && (
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Gauge size={12} /> OCR Confidence: {(plate_confidence * 100).toFixed(1)}%
            </span>
          )}
        </div>

        {plate_image && (
          <div style={{ textAlign: 'center' }}>
            <div
              style={{
                width: '120px',
                height: '50px',
                borderRadius: 'var(--radius-sm)',
                overflow: 'hidden',
                border: '1px solid rgba(52, 211, 153, 0.4)',
                background: '#000',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <img
                src={`data:image/jpeg;base64,${plate_image}`}
                alt="Cropped Plate"
                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
              />
            </div>
            <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '4px', display: 'block' }}>
              Cropped Region
            </span>
          </div>
        )}
      </div>

      {/* Vehicle Detection Breakdown */}
      <div>
        <h3 style={{ fontSize: '0.875rem', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Car size={16} color="var(--accent-cyan)" />
          Vehicles Detected ({vehicle_count})
        </h3>

        {vehicles && vehicles.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {vehicles.map((v, idx) => {
              const tagClass =
                v.class_name.toLowerCase() === 'car' ? 'tag-car' :
                v.class_name.toLowerCase() === 'truck' ? 'tag-truck' :
                v.class_name.toLowerCase() === 'bus' ? 'tag-bus' : 'tag-motorcycle';

              return (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 16px',
                    background: 'var(--bg-tertiary)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span className={`vehicle-tag ${tagClass}`}>
                      {v.class_name}
                    </span>
                    <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                      Vehicle #{idx + 1}
                    </span>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <span style={{ fontSize: '0.875rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                      {(v.confidence * 100).toFixed(0)}%
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: '4px' }}>
                      conf.
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
            No vehicle classified by YOLOv8 model in this image.
          </p>
        )}
      </div>
    </div>
  );
}

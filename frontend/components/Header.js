'use client';

import { ShieldCheck, Wifi, WifiOff, Activity } from 'lucide-react';

export default function Header({ isServerOnline }) {
  return (
    <header style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '16px 0'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: 'var(--radius-md)',
          background: 'var(--gradient-main)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <ShieldCheck size={22} color="#fff" />
        </div>
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: '800', letterSpacing: '-0.02em' }}>
            ANPR Vehicle Intelligence
          </h1>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            License Plate Recognition & Fleet Analysis Dashboard
          </p>
        </div>
      </div>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '6px 14px',
        borderRadius: 'var(--radius-full)',
        background: isServerOnline ? 'rgba(16, 185, 129, 0.12)' : 'rgba(244, 63, 94, 0.12)',
        color: isServerOnline ? '#34d399' : '#fb7185',
        fontSize: '0.75rem',
        fontWeight: '600'
      }}>
        {isServerOnline ? <Wifi size={14} /> : <WifiOff size={14} />}
        {isServerOnline ? 'API Connected' : 'API Offline'}
        {isServerOnline && (
          <Activity size={12} style={{ marginLeft: '4px', opacity: 0.6 }} />
        )}
      </div>
    </header>
  );
}

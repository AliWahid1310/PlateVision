'use client';

import { Car, Sparkles, Activity } from 'lucide-react';

export default function Header({ isServerOnline }) {
  return (
    <header className="header">
      <div className="brand">
        <div className="brand-icon">
          <Car size={24} strokeWidth={2.2} />
        </div>
        <div>
          <h1 className="brand-title">ANPR Vision AI</h1>
          <p className="brand-subtitle">Automatic Number Plate & Vehicle Intelligence</p>
        </div>
      </div>

      <div className="system-status">
        <span className="status-dot" style={{ backgroundColor: isServerOnline ? '#10b981' : '#f43f5e', boxShadow: isServerOnline ? '0 0 10px #10b981' : '0 0 10px #f43f5e' }} />
        <span>{isServerOnline ? 'FastAPI & YOLO Ready' : 'Backend Connecting...'}</span>
      </div>
    </header>
  );
}

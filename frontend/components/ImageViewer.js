'use client';

import { useState } from 'react';
import { Eye, Layers, Sparkles, Download } from 'lucide-react';

export default function ImageViewer({ originalPreview, outputBase64, filename }) {
  const [activeView, setActiveView] = useState('annotated'); // 'annotated' | 'original'

  if (!originalPreview && !outputBase64) return null;

  const currentSrc = activeView === 'annotated' && outputBase64
    ? `data:image/jpeg;base64,${outputBase64}`
    : originalPreview;

  const handleDownload = () => {
    if (!currentSrc) return;
    const link = document.createElement('a');
    link.href = currentSrc;
    link.download = `${filename || 'anpr_result'}_${activeView}.jpg`;
    link.click();
  };

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', gap: '6px', background: 'var(--bg-tertiary)', padding: '4px', borderRadius: 'var(--radius-md)' }}>
          <button
            type="button"
            className={`btn-secondary ${activeView === 'annotated' ? 'active' : ''}`}
            style={{
              padding: '6px 14px',
              fontSize: '0.8125rem',
              background: activeView === 'annotated' ? 'var(--gradient-main)' : 'transparent',
              color: activeView === 'annotated' ? '#fff' : 'var(--text-secondary)',
              border: 'none'
            }}
            onClick={() => setActiveView('annotated')}
            disabled={!outputBase64}
          >
            <Sparkles size={14} /> AI Annotated Frame
          </button>
          <button
            type="button"
            className={`btn-secondary ${activeView === 'original' ? 'active' : ''}`}
            style={{
              padding: '6px 14px',
              fontSize: '0.8125rem',
              background: activeView === 'original' ? 'var(--gradient-main)' : 'transparent',
              color: activeView === 'original' ? '#fff' : 'var(--text-secondary)',
              border: 'none'
            }}
            onClick={() => setActiveView('original')}
          >
            <Eye size={14} /> Original Source
          </button>
        </div>

        {outputBase64 && (
          <button type="button" className="btn-secondary" onClick={handleDownload} style={{ fontSize: '0.8125rem', padding: '6px 12px' }}>
            <Download size={14} /> Save Frame
          </button>
        )}
      </div>

      <div
        style={{
          width: '100%',
          minHeight: '380px',
          maxHeight: '520px',
          borderRadius: 'var(--radius-md)',
          background: '#040711',
          border: '1px solid var(--border-subtle)',
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative'
        }}
      >
        <img
          src={currentSrc}
          alt="Detection output"
          style={{ width: '100%', height: '100%', maxHeight: '520px', objectFit: 'contain' }}
        />
      </div>
    </div>
  );
}

'use client';

import { useState } from 'react';
import { Layers, Image, Eye } from 'lucide-react';

export default function ProcessingSteps({ steps }) {
  const [selectedStep, setSelectedStep] = useState(null);

  if (!steps) return null;

  const stepList = [
    { key: 'grayscale', name: 'Grayscale Conversion', desc: '1-channel brightness mapping', num: '01' },
    { key: 'blurred', name: 'Gaussian Filter Blur', desc: '5x5 Kernel Noise reduction', num: '02' },
    { key: 'edges', name: 'Canny Edge Detection', desc: 'Boundary & gradient extraction', num: '03' },
    { key: 'threshold', name: 'Otsu Thresholding', desc: 'Binary separation for OCR', num: '04' }
  ];

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2 style={{ fontSize: '1.125rem', fontWeight: '700', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Layers size={18} color="var(--accent-cyan)" />
          Computer Vision Pipeline Breakdown
        </h2>
        <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
          Step-by-step intermediate transformations computed before contour analysis
        </p>
      </div>

      <div className="steps-grid">
        {stepList.map((st) => {
          const imgBase64 = steps[st.key];
          if (!imgBase64) return null;

          return (
            <div
              key={st.key}
              className="step-card"
              onClick={() => setSelectedStep(st)}
              style={{ cursor: 'pointer' }}
            >
              <div className="step-img-wrapper">
                <img
                  src={`data:image/jpeg;base64,${imgBase64}`}
                  alt={st.name}
                  className="step-img"
                />
              </div>
              <div className="step-info">
                <span className="step-num">Step {st.num}</span>
                <h4 className="step-name">{st.name}</h4>
                <p style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  {st.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal for viewing larger step */}
      {selectedStep && steps[selectedStep.key] && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 100,
            background: 'rgba(0,0,0,0.8)',
            backdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '24px'
          }}
          onClick={() => setSelectedStep(null)}
        >
          <div
            className="glass-card"
            style={{ maxWidth: '800px', width: '100%', padding: '20px', background: 'var(--bg-secondary)' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <span className="step-num">Step {selectedStep.num}</span>
                <h3 style={{ fontSize: '1.25rem', fontWeight: '700' }}>{selectedStep.name}</h3>
              </div>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setSelectedStep(null)}
                style={{ padding: '4px 12px', fontSize: '0.8125rem' }}
              >
                Close
              </button>
            </div>
            <div style={{ width: '100%', maxHeight: '500px', overflow: 'hidden', background: '#000', borderRadius: 'var(--radius-md)' }}>
              <img
                src={`data:image/jpeg;base64,${steps[selectedStep.key]}`}
                alt={selectedStep.name}
                style={{ width: '100%', height: '100%', maxHeight: '500px', objectFit: 'contain' }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

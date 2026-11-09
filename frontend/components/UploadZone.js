'use client';

import { useState, useRef, useCallback } from 'react';
import { Upload, ImagePlus, X } from 'lucide-react';

export default function UploadZone({ onImageSelected, selectedPreview }) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleFile = useCallback((file) => {
    if (!file || !file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = (e) => onImageSelected(file, e.target.result);
    reader.readAsDataURL(file);
  }, [onImageSelected]);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  const handleClick = () => fileInputRef.current?.click();

  const handleClear = (e) => {
    e.stopPropagation();
    onImageSelected(null, null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div
      className={`upload-zone ${isDragging ? 'drag-over' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={(e) => handleFile(e.target.files[0])}
        style={{ display: 'none' }}
      />
      {selectedPreview ? (
        <div style={{ position: 'relative', display: 'inline-block' }}>
          <img
            src={selectedPreview}
            alt="Selected"
            style={{
              maxHeight: '200px',
              maxWidth: '100%',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-accent)'
            }}
          />
          <button
            type="button"
            onClick={handleClear}
            style={{
              position: 'absolute',
              top: '-8px',
              right: '-8px',
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              background: 'var(--accent-rose)',
              border: 'none',
              color: '#fff',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <X size={14} />
          </button>
          <p style={{ marginTop: '10px', fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
            Click or drop to replace image
          </p>
        </div>
      ) : (
        <>
          <Upload size={40} style={{ color: 'var(--accent-cyan)', opacity: 0.5, marginBottom: '16px' }} />
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: '600' }}>
            Drop Vehicle Image Here
          </h3>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
            or click to browse &bull; JPG, PNG, WebP supported
          </p>
        </>
      )}
    </div>
  );
}

'use client';

import { useState, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, Sparkles, CheckCircle2 } from 'lucide-react';

export default function UploadZone({ onImageSelected, selectedImagePreview, onProcess, isProcessing, disabled }) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    if (!file.type.startsWith('image/')) {
      alert('Please upload a valid image file (JPEG, PNG, WEBP, etc.)');
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      onImageSelected(file, reader.result);
    };
    reader.readAsDataURL(file);
  };

  const loadSample = async (samplePath) => {
    try {
      const response = await fetch(samplePath);
      const blob = await response.blob();
      const file = new File([blob], 'sample_car.jpg', { type: 'image/jpeg' });
      handleFile(file);
    } catch (err) {
      console.error('Failed to load sample image', err);
    }
  };

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.125rem', fontWeight: '700', color: 'var(--text-primary)' }}>
            Input Vehicle Image
          </h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
            Upload high-resolution camera capture for optimal plate recognition
          </p>
        </div>
      </div>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="image/*"
        style={{ display: 'none' }}
      />

      <div
        className={`upload-zone ${isDragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        {selectedImagePreview ? (
          <div style={{ width: '100%', position: 'relative' }}>
            <div
              style={{
                width: '100%',
                maxHeight: '280px',
                borderRadius: 'var(--radius-md)',
                overflow: 'hidden',
                background: '#000',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative'
              }}
            >
              <img
                src={selectedImagePreview}
                alt="Upload preview"
                style={{ width: '100%', height: '100%', maxHeight: '280px', objectFit: 'contain' }}
              />
              {isProcessing && <div className="scanner-line" />}
            </div>
            <p style={{ marginTop: '12px', fontSize: '0.8125rem', color: 'var(--accent-cyan)' }}>
              Click or drag another image to change
            </p>
          </div>
        ) : (
          <>
            <div className="upload-icon-wrapper">
              <UploadCloud size={32} />
            </div>
            <h3 className="upload-title">Drop your image here, or click to browse</h3>
            <p className="upload-subtitle">Supports JPG, PNG, WEBP up to 20MB</p>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', justifyContent: 'center' }}>
              <button
                type="button"
                className="btn-upload"
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}
              >
                <ImageIcon size={16} /> Choose Image
              </button>
              <button
                type="button"
                className="btn-secondary"
                onClick={(e) => {
                  e.stopPropagation();
                  loadSample('/sample_car.jpg');
                }}
                style={{ padding: '10px 18px', borderRadius: 'var(--radius-full)' }}
              >
                <Sparkles size={16} color="var(--accent-cyan)" /> Try Sample Image
              </button>
            </div>
          </>
        )}
      </div>

      <button
        type="button"
        className="btn-primary"
        onClick={onProcess}
        disabled={!selectedImagePreview || isProcessing || disabled}
      >
        <Sparkles size={18} />
        {isProcessing ? 'Analyzing Frame with YOLO & EasyOCR...' : 'Run ANPR & Vehicle Detection'}
      </button>
    </div>
  );
}

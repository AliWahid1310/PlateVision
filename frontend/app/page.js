'use client';

import { useState, useEffect } from 'react';
import Header from '../components/Header';
import UploadZone from '../components/UploadZone';
import ResultsPanel from '../components/ResultsPanel';
import ImageViewer from '../components/ImageViewer';
import ProcessingSteps from '../components/ProcessingSteps';
import { AlertCircle } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

export default function Home() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedImagePreview, setSelectedImagePreview] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isServerOnline, setIsServerOnline] = useState(false);
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  // Check if FastAPI backend is online
  useEffect(() => {
    const checkServer = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/health`);
        if (res.ok) {
          setIsServerOnline(true);
        } else {
          setIsServerOnline(false);
        }
      } catch (e) {
        setIsServerOnline(false);
      }
    };

    checkServer();
    const interval = setInterval(checkServer, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleImageSelected = (file, previewUrl) => {
    setSelectedFile(file);
    setSelectedImagePreview(previewUrl);
    setResult(null);
    setErrorMessage(null);
  };

  const handleProcess = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setErrorMessage(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${API_BASE_URL}/api/process`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned error ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error('ANPR Error:', err);
      setErrorMessage(
        err.message.includes('Failed to fetch')
          ? 'Cannot connect to Python API server. Please ensure `python api.py` is running on port 8000.'
          : err.message
      );
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <main className="app-container">
      <Header isServerOnline={isServerOnline} />

      {!isServerOnline && (
        <div
          style={{
            padding: '12px 20px',
            borderRadius: 'var(--radius-md)',
            background: 'rgba(245, 158, 11, 0.12)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            color: '#fbbf24',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            fontSize: '0.875rem'
          }}
        >
          <AlertCircle size={18} />
          <span>
            <strong>Python API Backend is Offline:</strong> Run{' '}
            <code style={{ background: 'rgba(0,0,0,0.3)', padding: '2px 6px', borderRadius: '4px' }}>
              python api.py
            </code>{' '}
            in the <code style={{ background: 'rgba(0,0,0,0.3)', padding: '2px 6px', borderRadius: '4px' }}>ANPR_Project</code> directory.
          </span>
        </div>
      )}

      {errorMessage && (
        <div
          style={{
            padding: '14px 20px',
            borderRadius: 'var(--radius-md)',
            background: 'rgba(244, 63, 94, 0.12)',
            border: '1px solid rgba(244, 63, 94, 0.3)',
            color: '#fb7185',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            fontSize: '0.875rem'
          }}
        >
          <AlertCircle size={18} />
          <span>{errorMessage}</span>
        </div>
      )}

      <div className="main-grid">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <UploadZone
            onImageSelected={handleImageSelected}
            selectedImagePreview={selectedImagePreview}
            onProcess={handleProcess}
            isProcessing={isProcessing}
            disabled={!isServerOnline}
          />

          {result && <ResultsPanel result={result} />}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <ImageViewer
            originalPreview={selectedImagePreview}
            outputBase64={result?.output_image}
            filename={result?.filename}
          />

          {result?.processing_steps && (
            <ProcessingSteps steps={result.processing_steps} />
          )}
        </div>
      </div>
    </main>
  );
}

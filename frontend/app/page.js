'use client';

import { useState, useEffect } from 'react';
import Header from '../components/Header';
import UploadZone from '../components/UploadZone';
import ResultsPanel from '../components/ResultsPanel';
import ImageViewer from '../components/ImageViewer';
import ProcessingSteps from '../components/ProcessingSteps';
import StatsPanel from '../components/StatsPanel';
import HistoryTable from '../components/HistoryTable';
import { AlertCircle, Zap } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

export default function Home() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedImagePreview, setSelectedImagePreview] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isServerOnline, setIsServerOnline] = useState(false);
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  useEffect(() => {
    const checkServer = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/health`);
        setIsServerOnline(res.ok);
      } catch (_) {
        setIsServerOnline(false);
      }
    };
    checkServer();
    const interval = setInterval(checkServer, 5000);
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
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error ${response.status}`);
      }
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setErrorMessage(
        err.message.includes('Failed to fetch')
          ? 'Cannot connect to Python API. Ensure python api.py is running on port 8000.'
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
        <div style={{
          padding: '12px 20px',
          borderRadius: 'var(--radius-md)',
          background: 'rgba(245, 158, 11, 0.12)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          color: '#fbbf24',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          fontSize: '0.875rem'
        }}>
          <AlertCircle size={18} />
          <span>
            <strong>Backend Offline</strong> &mdash; Start the Python API server:
            <code style={{ marginLeft: '8px', padding: '2px 8px', background: 'rgba(0,0,0,0.3)', borderRadius: '4px' }}>
              python api.py
            </code>
          </span>
        </div>
      )}

      <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '280px' }}>
          <UploadZone onImageSelected={handleImageSelected} selectedPreview={selectedImagePreview} />
        </div>
        <button
          className="btn-primary"
          onClick={handleProcess}
          disabled={!selectedFile || isProcessing || !isServerOnline}
        >
          {isProcessing ? (
            <>
              <span className="spinner-ring" />
              Analyzing...
            </>
          ) : (
            <>
              <Zap size={18} />
              Run ANPR Analysis
            </>
          )}
        </button>
      </div>

      {errorMessage && (
        <div style={{
          padding: '12px 20px',
          borderRadius: 'var(--radius-md)',
          background: 'rgba(244, 63, 94, 0.12)',
          border: '1px solid rgba(244, 63, 94, 0.3)',
          color: '#fb7185',
          fontSize: '0.875rem',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <AlertCircle size={16} />
          {errorMessage}
        </div>
      )}

      {(result || selectedImagePreview) && (
        <div className="main-grid">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <ImageViewer
              originalPreview={selectedImagePreview}
              outputBase64={result?.annotated_image}
              filename={selectedFile?.name}
            />
            {result?.processing_steps && <ProcessingSteps steps={result.processing_steps} />}
          </div>
          <ResultsPanel result={result} />
        </div>
      )}

      <StatsPanel />
      <HistoryTable />
    </main>
  );
}

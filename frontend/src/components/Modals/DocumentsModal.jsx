import React, { useState, useEffect } from 'react';
import { X, FileText, Download, Eye, Calendar, HardDrive, Upload, Loader2, CheckCircle, AlertCircle, Trash2 } from 'lucide-react';
import { getDocuments, getDocumentUrl, ingestDocument, deleteDocument } from '../../api';
import './DocumentsModal.css';

const DocumentsModal = ({ isOpen, onClose }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [provider, setProvider] = useState('');
  const [error, setError] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, success, error
  const [uploadMessage, setUploadMessage] = useState('');
  const [deletingDoc, setDeletingDoc] = useState(null); // Track which document is being deleted

  useEffect(() => {
    if (isOpen) {
      fetchDocuments();
    }
  }, [isOpen]);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getDocuments();
      setDocuments(data.documents);
      setProvider(data.provider);
    } catch (err) {
      setError('Failed to load documents');
      console.error('Error fetching documents:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDocument = (filename) => {
    const url = getDocumentUrl(filename);
    window.open(url, '_blank');
  };

  const handleDownloadDocument = (filename) => {
    const url = getDocumentUrl(filename);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadStatus('uploading');
    setUploadMessage('Uploading and processing document...');

    try {
      const response = await ingestDocument(file);
      setUploadStatus('success');
      setUploadMessage(`Successfully uploaded! Created ${response.chunks} chunks.`);
      
      // Refresh document list after successful upload
      setTimeout(() => {
        fetchDocuments();
        setUploadStatus('idle');
        setUploadMessage('');
      }, 2000);
    } catch (err) {
      setUploadStatus('error');
      setUploadMessage('Failed to upload document. Please try again.');
      console.error('Upload error:', err);
      
      setTimeout(() => {
        setUploadStatus('idle');
        setUploadMessage('');
      }, 3000);
    }
  };

  const handleDeleteDocument = async (doc) => {
    // Confirmation dialog
    const confirmDelete = window.confirm(
      `Are you sure you want to delete "${doc.filename}"?\n\nThis will remove the document and all its embeddings from the vector store.`
    );
    
    if (!confirmDelete) return;

    setDeletingDoc(doc.filename);
    
    try {
      await deleteDocument(doc.filename, doc.uploadedOn);
      
      // Refresh document list after successful deletion
      await fetchDocuments();
      
      // Show success message briefly
      setUploadStatus('success');
      setUploadMessage(`Document "${doc.filename}" deleted successfully.`);
      
      setTimeout(() => {
        setUploadStatus('idle');
        setUploadMessage('');
      }, 2000);
    } catch (err) {
      setUploadStatus('error');
      setUploadMessage('Failed to delete document. Please try again.');
      console.error('Delete error:', err);
      
      setTimeout(() => {
        setUploadStatus('idle');
        setUploadMessage('');
      }, 3000);
    } finally {
      setDeletingDoc(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content documents-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-header-content">
            <h2>Manage Documents</h2>
            {provider && (
              <span className="provider-badge">
                Using: {provider.toUpperCase()}
              </span>
            )}
          </div>
          <div className="modal-header-actions">
            <label className={`upload-btn-modal ${uploadStatus}`}>
              {uploadStatus === 'uploading' ? (
                <Loader2 size={18} className="spin" />
              ) : uploadStatus === 'success' ? (
                <CheckCircle size={18} />
              ) : uploadStatus === 'error' ? (
                <AlertCircle size={18} />
              ) : (
                <Upload size={18} />
              )}
              <span>
                {uploadStatus === 'uploading' ? 'Uploading...' :
                 uploadStatus === 'success' ? 'Uploaded!' :
                 uploadStatus === 'error' ? 'Failed' :
                 'Upload PDF'}
              </span>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                disabled={uploadStatus === 'uploading'}
                style={{ display: 'none' }}
              />
            </label>
            <button className="modal-close-btn" onClick={onClose}>
              <X size={24} />
            </button>
          </div>
        </div>

        {uploadMessage && (
          <div className={`upload-message ${uploadStatus}`}>
            {uploadMessage}
          </div>
        )}

        <div className="modal-body">
          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading documents...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <p>{error}</p>
              <button onClick={fetchDocuments} className="retry-btn">
                Try Again
              </button>
            </div>
          ) : documents.length === 0 ? (
            <div className="empty-state">
              <FileText size={64} strokeWidth={1.5} />
              <h3>No documents uploaded yet</h3>
              <p>Upload a PDF to get started with your Q&A session</p>
            </div>
          ) : (
            <div className="documents-grid">
              {documents.map((doc) => (
                <div key={doc.filename} className="document-card">
                  <div className="document-icon">
                    <FileText size={32} />
                    <span className="document-extension">{doc.extension}</span>
                  </div>
                  
                  <div className="document-info">
                    <h3 className="document-name" title={doc.filename}>
                      {doc.name}
                    </h3>
                    
                    <div className="document-meta">
                      <div className="meta-item">
                        <HardDrive size={14} />
                        <span>{doc.sizeFormatted}</span>
                      </div>
                      <div className="meta-item">
                        <Calendar size={14} />
                        <span>{doc.uploadedOnFormatted}</span>
                      </div>
                    </div>
                  </div>

                  <div className="document-actions">
                    <button
                      className="action-btn view-btn"
                      onClick={() => handleViewDocument(doc.filename)}
                      title="View Document"
                      disabled={deletingDoc === doc.filename}
                    >
                      <Eye size={18} />
                      View
                    </button>
                    <button
                      className="action-btn download-btn"
                      onClick={() => handleDownloadDocument(doc.filename)}
                      title="Download Document"
                      disabled={deletingDoc === doc.filename}
                    >
                      <Download size={18} />
                    </button>
                    <button
                      className="action-btn delete-btn"
                      onClick={() => handleDeleteDocument(doc)}
                      title="Delete Document"
                      disabled={deletingDoc === doc.filename}
                    >
                      {deletingDoc === doc.filename ? (
                        <Loader2 size={18} className="spin" />
                      ) : (
                        <Trash2 size={18} />
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <p className="document-count">
            {documents.length} {documents.length === 1 ? 'document' : 'documents'} available
          </p>
        </div>
      </div>
    </div>
  );
};

export default DocumentsModal;

import React, { useState } from 'react';
import { Upload, CheckCircle, AlertCircle, Loader2, FileText, X } from 'lucide-react';
import { ingestDocument } from '../../api';
import './UploadSection.css';

const UploadSection = ({ setIsUploading }) => {
    const [status, setStatus] = useState('idle'); // idle, uploading, success, error
    const [filePreview, setFilePreview] = useState(null);

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // Set preview info
        setFilePreview({
            name: file.name,
            size: (file.size / 1024 / 1024).toFixed(2) + ' MB',
            type: file.type
        });

        setStatus('uploading');
        setIsUploading(true);

        try {
            await ingestDocument(file);
            setStatus('success');
        } catch (error) {
            setStatus('error');
        } finally {
            setIsUploading(false);
        }
    };

    const clearPreview = (e) => {
        e.preventDefault();
        setFilePreview(null);
        setStatus('idle');
    };

    return (
        <div className="upload-container">
            {!filePreview ? (
                <label className={`upload-btn ${status}`}>
                    {status === 'uploading' ? (
                        <Loader2 className="icon spin" />
                    ) : status === 'success' ? (
                        <CheckCircle className="icon" />
                    ) : status === 'error' ? (
                        <AlertCircle className="icon" />
                    ) : (
                        <Upload className="icon" />
                    )}
                    <span>{status === 'success' ? 'Uploaded' : 'Upload PDF'}</span>
                    <input
                        type="file"
                        accept=".pdf"
                        onChange={handleFileChange}
                        disabled={status === 'uploading'}
                        className="file-input-hidden"
                    />
                </label>
            ) : (
                <div className="file-preview-card">
                    <div className="file-icon-wrapper">
                        <FileText size={24} className="file-icon" />
                    </div>
                    <div className="file-info">
                        <span className="file-name">{filePreview.name}</span>
                        <span className="file-size">{filePreview.size}</span>
                    </div>
                    {status === 'uploading' && <Loader2 className="status-icon spin" size={20} />}
                    {status === 'success' && <CheckCircle className="status-icon success" size={20} />}
                    {status === 'error' && <AlertCircle className="status-icon error" size={20} />}

                    {/* Allow re-upload or clear if not currently uploading */}
                    {status !== 'uploading' && (
                        <button className="clear-btn" onClick={clearPreview} title="Clear file">
                            <X size={16} />
                        </button>
                    )}
                </div>
            )}
        </div>
    );
};

export default UploadSection;

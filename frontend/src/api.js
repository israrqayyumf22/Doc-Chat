import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
});

export const ingestDocument = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await api.post('/ingest', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error('Error uploading file:', error);
        throw error;
    }
};

export const chatWithBot = async (query) => {
    try {
        const response = await api.post('/chat', { query });
        return response.data;
    } catch (error) {
        console.error('Error chatting:', error);
        throw error;
    }
};

export const getDocuments = async () => {
    try {
        const response = await api.get('/documents');
        return response.data;
    } catch (error) {
        console.error('Error fetching documents:', error);
        throw error;
    }
};

export const getDocumentUrl = (filename) => {
    return `${API_BASE_URL}/documents/${encodeURIComponent(filename)}`;
};

export const deleteDocument = async (filename, uploadedAt) => {
    try {
        const response = await api.delete(`/documents/${encodeURIComponent(filename)}`, {
            params: { uploaded_at: uploadedAt }
        });
        return response.data;
    } catch (error) {
        console.error('Error deleting document:', error);
        throw error;
    }
};

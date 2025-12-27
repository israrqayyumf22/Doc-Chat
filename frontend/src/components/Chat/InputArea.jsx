import React, { useState } from 'react';
import { Send, Loader2, FileText } from 'lucide-react';
import { chatWithBot } from '../../api';
import './InputArea.css';

const InputArea = ({ messages, setMessages, onOpenDocuments }) => {
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = { id: Date.now(), role: 'user', content: input };
        const newMessagesWithUser = [...messages, userMessage];

        setMessages(newMessagesWithUser);
        setInput('');
        setIsLoading(true);

        // Initial placeholder for AI response logic could go here if streaming
        // For now, wait for full response
        try {
            const response = await chatWithBot(userMessage.content);
            const botMessage = {
                id: Date.now() + 1,
                role: 'ai',
                content: response.answer
            };
            setMessages([...newMessagesWithUser, botMessage]);
        } catch (error) {
            const errorMessage = {
                id: Date.now() + 1,
                role: 'ai',
                content: 'Sorry, I encountered an error. Please ensure a document is uploaded and try again.'
            };
            setMessages([...newMessagesWithUser, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="input-wrapper">
            <div className="documents-button-container">
                <button 
                    className="documents-access-btn" 
                    onClick={onOpenDocuments}
                    title="Manage Documents"
                >
                    <FileText size={20} />
                    <span>Documents</span>
                </button>
            </div>
            <form className="input-container" onSubmit={handleSend}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask a question about your document..."
                    disabled={isLoading}
                />
                <button type="submit" className="primary-btn" disabled={isLoading || !input.trim()}>
                    {isLoading ? <Loader2 className="spin" size={20} /> : <Send size={20} />}
                </button>
            </form>
        </div>
    );
};

export default InputArea;

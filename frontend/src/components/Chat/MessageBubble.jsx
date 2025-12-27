import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User } from 'lucide-react';
import './MessageBubble.css';

const MessageBubble = ({ message }) => {
    const isAi = message.role === 'ai';

    return (
        <div className={`message-container ${isAi ? 'ai' : 'user'}`}>
            <div className="avatar">
                {isAi ? <Bot size={20} /> : <User size={20} />}
            </div>
            <div className="bubble">
                {isAi ? (
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                ) : (
                    <p>{message.content}</p>
                )}
            </div>
        </div>
    );
};

export default MessageBubble;

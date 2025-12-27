import React, { useState } from 'react';
import { Plus, MessageSquare, Moon, Sun, Monitor, Menu, X, Trash2, Info } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import AboutUsModal from '../Modals/AboutUsModal';
import './Sidebar.css';

const Sidebar = ({ isOpen, onClose, savedChats, onSelectChat, onNewChat, onDeleteChat }) => {
    const { theme, toggleTheme } = useTheme();
    const [showAboutUs, setShowAboutUs] = useState(false);

    return (
        <>
            {/* Mobile Overlay */}
            {isOpen && <div className="sidebar-overlay" onClick={onClose} />}

            <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <button className="new-chat-btn" onClick={() => { onNewChat(); if (window.innerWidth < 768) onClose(); }}>
                        <Plus size={20} />
                        <span>New Chat</span>
                    </button>

                    {/* Mobile Close Button */}
                    <button className="close-sidebar-btn" onClick={onClose}>
                        <X size={20} />
                    </button>
                </div>

                <div className="sidebar-content">
                    <div className="chat-history-label">Recents</div>
                    <div className="chat-list">
                        {savedChats.length === 0 ? (
                            <div className="empty-history">No previous chats</div>
                        ) : (
                            savedChats.map((chat) => (
                                <div key={chat.id} className="chat-item-group">
                                    <button
                                        className="chat-item"
                                        onClick={() => { onSelectChat(chat); if (window.innerWidth < 768) onClose(); }}
                                    >
                                        <MessageSquare size={16} />
                                        <span className="chat-title-text">{chat.title || 'Untitled Chat'}</span>
                                    </button>
                                    <button
                                        className="delete-chat-btn"
                                        onClick={(e) => { e.stopPropagation(); onDeleteChat(chat.id); }}
                                        title="Delete Chat"
                                    >
                                        <Trash2 size={14} />
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                <div className="sidebar-footer">
                    <button className="theme-toggle" onClick={toggleTheme}>
                        {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                        <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
                    </button>
                    <button className="about-us-btn" onClick={() => setShowAboutUs(true)}>
                        <Info size={20} />
                        <span>About Us</span>
                    </button>
                </div>
            </aside>
            <AboutUsModal isOpen={showAboutUs} onClose={() => setShowAboutUs(false)} />
        </>
    );
};

export default Sidebar;

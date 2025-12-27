import React, { useState, useEffect } from 'react';
import { Menu, FileText } from 'lucide-react';
import ChatWindow from './components/Chat/ChatWindow';
import InputArea from './components/Chat/InputArea';
import Sidebar from './components/Sidebar/Sidebar';
import DocumentsModal from './components/Modals/DocumentsModal';
import { ThemeProvider } from './context/ThemeContext';
import './App.css';

const AppContent = () => {
  // Initial state from localStorage or default
  const [savedChats, setSavedChats] = useState(() => {
    const saved = localStorage.getItem('chatHistory');
    return saved ? JSON.parse(saved) : [];
  });

  // Current active chat
  const [currentChatId, setCurrentChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isDocumentsModalOpen, setIsDocumentsModalOpen] = useState(false);

  // Load active chat messages when ID changes
  useEffect(() => {
    if (currentChatId) {
      const chat = savedChats.find(c => c.id === currentChatId);
      if (chat) {
        setMessages(chat.messages);
      }
    } else {
      // New chat state
      setMessages([
        { id: 1, role: 'ai', content: 'Hello! Upload a PDF to get started, then ask me anything about it.' }
      ]);
    }
  }, [currentChatId, savedChats]);

  // Save chats to local storage whenever they update
  useEffect(() => {
    localStorage.setItem('chatHistory', JSON.stringify(savedChats));
  }, [savedChats]);

  const handleNewChat = () => {
    setCurrentChatId(null);
    setMessages([
      { id: 1, role: 'ai', content: 'Hello! Upload a PDF to get started, then ask me anything about it.' }
    ]);
    setIsSidebarOpen(false); // Close sidebar on mobile
  };

  const handleSelectChat = (chat) => {
    setCurrentChatId(chat.id);
    setIsSidebarOpen(false); // Close sidebar on mobile
  };

  const handleDeleteChat = (chatId) => {
    const updatedChats = savedChats.filter(c => c.id !== chatId);
    setSavedChats(updatedChats);
    if (currentChatId === chatId) {
      handleNewChat();
    }
  };

  const updateCurrentChatMessages = (newMessages) => {
    setMessages(newMessages);

    // If it's a new conversation (no ID yet) and user sends a message, save it
    if (!currentChatId && newMessages.length > 1) { // >1 because of initial greeting
      const newChatId = Date.now().toString();
      // Use user's first message as title
      const userMsg = newMessages.find(m => m.role === 'user');
      const title = userMsg ? userMsg.content.substring(0, 30) + (userMsg.content.length > 30 ? '...' : '') : 'New Chat';

      const newChat = {
        id: newChatId,
        title: title,
        timestamp: new Date().toISOString(),
        messages: newMessages
      };

      setSavedChats([newChat, ...savedChats]);
      setCurrentChatId(newChatId);
    } else if (currentChatId) {
      // Update existing chat
      const updatedChats = savedChats.map(chat =>
        chat.id === currentChatId
          ? { ...chat, messages: newMessages }
          : chat
      );
      setSavedChats(updatedChats);
    }
  };

  return (
    <div className="app-container">
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        savedChats={savedChats}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
      />

      <main className="main-content">
        <header className="app-header">
          <button className="menu-btn" onClick={() => setIsSidebarOpen(true)}>
            <Menu size={24} />
          </button>
          <div className="header-title">
            <h1>ChatPDF</h1>
          </div>
          <div className="header-actions">
          </div>
        </header>

        <div className="chat-area-wrapper">
          <ChatWindow messages={messages} />
          <InputArea 
            messages={messages} 
            setMessages={updateCurrentChatMessages} 
            onOpenDocuments={() => setIsDocumentsModalOpen(true)}
          />
        </div>
      </main>

      <DocumentsModal 
        isOpen={isDocumentsModalOpen}
        onClose={() => setIsDocumentsModalOpen(false)}
      />
    </div>
  );
};

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;

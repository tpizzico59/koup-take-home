import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import { MessageSquare, Plus, Menu, Settings, HelpCircle, User } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    setMessages([{
      role: 'assistant',
      content: 'Hello! I\'m your Care Coordinator Assistant. I can help you schedule appointments, check provider availability, verify insurance coverage, and answer questions about our healthcare services. How can I assist you today?'
    }]);
  }, []);

  const handleSendMessage = async (content) => {
    const userMessage = { role: 'user', content };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        messages: updatedMessages
      });

      setMessages([...updatedMessages, {
        role: 'assistant',
        content: response.data.message
      }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages([...updatedMessages, {
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([{
      role: 'assistant',
      content: 'Hello! I\'m your Care Coordinator Assistant. How can I help you today?'
    }]);
  };

  return (
    <div className="flex h-screen bg-[#0D0D0D] text-white">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 flex-shrink-0 bg-[#0D0D0D] border-r border-white/10 flex flex-col overflow-hidden`}>
        <div className="flex items-center justify-between p-3 border-b border-white/10">
          <button
            onClick={handleNewChat}
            className="flex-1 flex items-center gap-3 px-3 py-2.5 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-sm"
          >
            <Plus className="w-4 h-4" />
            New chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          <div className="space-y-1">
            <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 transition-colors text-sm text-left text-white/70">
              <MessageSquare className="w-4 h-4 flex-shrink-0" />
              <span className="truncate">Current conversation</span>
            </button>
          </div>
        </div>

        <div className="p-2 border-t border-white/10 space-y-1">
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 transition-colors text-sm text-white/70">
            <HelpCircle className="w-4 h-4" />
            Help & Support
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 transition-colors text-sm text-white/70">
            <Settings className="w-4 h-4" />
            Settings
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 transition-colors text-sm text-white/70">
            <User className="w-4 h-4" />
            Profile
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col relative">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-white/5 transition-colors"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Care Coordinator</span>
          </div>
          <div className="w-9" /> {/* Spacer for centering */}
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 1 ? (
            <div className="h-full flex items-center justify-center px-4">
              <div className="max-w-3xl w-full space-y-8">
                <div className="text-center space-y-4">
                  <h1 className="text-4xl font-semibold">How can I help you today?</h1>
                  <p className="text-white/60">I can assist with scheduling appointments, checking provider availability, and more.</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {[
                    { title: 'Schedule an appointment', desc: 'Book with available providers' },
                    { title: 'Check insurance coverage', desc: 'Verify your insurance plan' },
                    { title: 'Find a specialist', desc: 'Search by specialty or location' },
                    { title: 'View appointment times', desc: 'See available time slots' }
                  ].map((item, i) => (
                    <button
                      key={i}
                      onClick={() => handleSendMessage(item.title)}
                      className="p-4 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-colors text-left group"
                    >
                      <p className="font-medium text-sm mb-1">{item.title}</p>
                      <p className="text-xs text-white/50">{item.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
              {messages.slice(1).map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}
              {isLoading && (
                <div className="flex gap-4 items-start">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#10A37F] flex items-center justify-center">
                    <MessageSquare className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-white/10 bg-[#0D0D0D]">
          <div className="max-w-3xl mx-auto px-4 py-4">
            <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
          </div>
        </div>
      </div>
    </div>
  );
}

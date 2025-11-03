import React, { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';

export default function ChatInput({ onSend, isLoading }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input);
      setInput('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="relative flex items-end gap-2 bg-[#2F2F2F] rounded-2xl border border-white/10 focus-within:border-white/20 transition-colors p-3">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Message Care Coordinator..."
          disabled={isLoading}
          rows={1}
          className="flex-1 bg-transparent text-white placeholder:text-white/40 resize-none outline-none text-[15px] max-h-[200px] scrollbar-hide disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="flex-shrink-0 w-8 h-8 rounded-lg bg-white hover:bg-white/90 disabled:bg-white/10 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
        >
          <Send className={`w-4 h-4 ${input.trim() && !isLoading ? 'text-black' : 'text-white/40'}`} />
        </button>
      </div>
      <p className="text-xs text-white/40 text-center mt-2">
        Care Coordinator can make mistakes. Please verify important information.
      </p>
    </form>
  );
}
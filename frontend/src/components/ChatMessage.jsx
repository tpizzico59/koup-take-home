import React from 'react';
import { User, MessageSquare } from 'lucide-react';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  
  return (
    <div className="group relative">
      <div className="flex gap-4 items-start">
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-white/10' : 'bg-[#10A37F]'
        }`}>
          {isUser ? (
            <User className="w-4 h-4 text-white" />
          ) : (
            <MessageSquare className="w-4 h-4 text-white" />
          )}
        </div>
        
        <div className="flex-1 space-y-2 pt-1">
          <div className="prose prose-invert max-w-none">
            <p className="text-[15px] leading-7 text-white/90 whitespace-pre-wrap m-0">
              {message.content}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
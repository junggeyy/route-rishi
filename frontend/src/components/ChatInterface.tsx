import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  AlertCircle, 
  RefreshCw, 
  X, 
  Bot,
  User,
  Cpu,
  Loader2
} from 'lucide-react';
import type { Message, AgentThought } from '../types';

interface ChatInterfaceProps {
  messages: Message[];
  isLoading: boolean;
  isAgentThinking: boolean;
  agentThoughts: AgentThought[];
  error: string | null;
  onSendMessage: (message: string) => void;
  onRetry: () => void;
  onClearError: () => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  isLoading,
  isAgentThinking,
  agentThoughts,
  error,
  onSendMessage,
  onRetry,
  onClearError,
}) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, agentThoughts]);

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
    }
  }, [inputValue]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const formatMessageContent = (content: string) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-secondary/50 px-1 rounded text-sm">$1</code>')
      .replace(/\n/g, '<br>');
  };

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Error Banner */}
      {error && (
        <div className="bg-danger/10 border-l-4 border-danger p-4 mx-4 mt-4 rounded-r">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-danger" />
              <p className="text-danger text-sm">{error}</p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={onRetry}
                className="text-danger hover:text-danger/80 transition-colors"
                title="Retry last message"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
              <button
                onClick={onClearError}
                className="text-danger hover:text-danger/80 transition-colors"
                title="Clear error"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start space-x-3 ${
              message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}
          >
            {/* Avatar */}
            <div className={`
              flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center
              ${message.type === 'user' 
                ? 'bg-accent' 
                : 'bg-gradient-to-br from-travel-blue to-accent'
              }
            `}>
              {message.type === 'user' ? (
                <User className="w-4 h-4 text-white" />
              ) : (
                <Bot className="w-4 h-4 text-white" />
              )}
            </div>

            {/* Message Content */}
            <div className={`
              flex-1 max-w-4xl
              ${message.type === 'user' ? 'flex justify-end' : ''}
            `}>
              <div className={`
                p-4 rounded-2xl
                ${message.type === 'user' 
                  ? 'bg-accent text-white max-w-xl' 
                  : 'glass-card text-text-primary'
                }
              `}>
                <div 
                  className="prose prose-invert max-w-none"
                  dangerouslySetInnerHTML={{ 
                    __html: formatMessageContent(message.content) 
                  }}
                />
                <div className={`
                  text-xs mt-2 opacity-70
                  ${message.type === 'user' ? 'text-white/70' : 'text-text-secondary'}
                `}>
                  {message.timestamp.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Agent Thinking Display */}
        {isAgentThinking && (
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-travel-blue to-accent flex items-center justify-center">
              <Cpu className="w-4 h-4 text-white" />
            </div>
            <div className="flex-1 max-w-4xl">
              <div className="agent-thinking">
                <div className="flex items-center space-x-2 mb-3">
                  <Loader2 className="w-4 h-4 text-accent animate-spin" />
                  <span className="text-accent font-medium">RouteRishi is thinking...</span>
                </div>
                
                {agentThoughts.map((thought) => (
                  <div key={thought.id} className="mb-2 p-2 bg-secondary/30 rounded">
                    <div className="text-xs text-travel-blue font-mono">
                      Invoking: {thought.action}
                    </div>
                    {thought.output && (
                      <div className="text-sm text-text-secondary mt-1">
                        {thought.output}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Loading Indicator */}
        {isLoading && !isAgentThinking && (
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-travel-blue to-accent flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="glass-card p-4 rounded-2xl">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-accent rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
                <span className="text-text-secondary text-sm">RouteRishi is typing...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-border/50 p-4">
        <form onSubmit={handleSubmit} className="flex items-end space-x-3">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask me anything about your travel plans..."
              className="input-field w-full resize-none min-h-[44px] max-h-32"
              rows={1}
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className={`
              p-3 rounded-lg transition-all duration-200
              ${inputValue.trim() && !isLoading
                ? 'bg-accent hover:bg-accent/90 text-white hover:scale-105'
                : 'bg-secondary/50 text-text-secondary cursor-not-allowed'
              }
            `}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </form>
        
        {/* Input Hint */}
        <div className="flex items-center justify-between mt-2 text-xs text-text-secondary">
          <span>Press Enter to send, Shift+Enter for new line</span>
          <span className="hidden sm:inline">Powered by AI • Real-time data</span>
        </div>
      </div>
    </div>
  );
}; 
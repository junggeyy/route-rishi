import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  AlertCircle, 
  RefreshCw, 
  X, 
  Bot,
  User,
  Cpu,
  Loader2,
  Brain
} from 'lucide-react';
import type { Message, AgentThought } from '../types';
import { ToolCallDisplay } from './ToolCallDisplay';

interface ChatInterfaceProps {
  messages: Message[];
  isLoading: boolean;
  isAgentThinking: boolean;
  agentThoughts: AgentThought[];
  error: string | null;
  onSendMessage: (message: string, withReasoning?: boolean) => void;
  onRetry: () => void;
  onClearError: () => void;
  isGuest?: boolean;
  hasReachedLimit?: boolean;
  remainingMessages?: number | null;
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
  isGuest = false,
  hasReachedLimit = false,
  remainingMessages = null,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [reasoningEnabled, setReasoningEnabled] = useState(true);
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
    if (inputValue.trim() && !isLoading && !hasReachedLimit) {
      onSendMessage(inputValue.trim(), reasoningEnabled);
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
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
          {messages.map((message) => (
            <div key={message.id} className="w-full">
              {message.type === 'user' ? (
                /* User Message */
                <div className="flex justify-end">
                  <div className="bg-accent/80 text-white p-4 rounded-2xl max-w-2xl">
                    <div 
                      className="prose prose-invert max-w-none"
                      dangerouslySetInnerHTML={{ 
                        __html: formatMessageContent(message.content) 
                      }}
                    />
                    <div className="text-xs mt-2 opacity-70 text-white/70">
                      {message.timestamp.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>
                </div>
              ) : (
                /* AI Message with Reasoning */
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-travel-blue to-accent flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1">
                    {/* Reasoning Display - show before the final message */}
                    {message.toolCalls && message.toolCalls.length > 0 && (
                      <ToolCallDisplay 
                        toolCalls={message.toolCalls} 
                        executionTimeMs={message.executionTimeMs}
                      />
                    )}
                    
                    {/* Main AI Response */}
                    <div className="glass-card p-4 rounded-2xl text-text-primary">
                      <div 
                        className="prose prose-invert max-w-none"
                        dangerouslySetInnerHTML={{ 
                          __html: formatMessageContent(message.content) 
                        }}
                      />
                      <div className="text-xs mt-2 opacity-70 text-text-secondary">
                        {message.timestamp.toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Agent Thinking Display */}
          {isAgentThinking && (
            <div className="w-full">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-travel-blue to-accent flex items-center justify-center">
                  <Cpu className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1">
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
            </div>
          )}

          {/* Loading Indicator */}
          {isLoading && !isAgentThinking && (
            <div className="w-full">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-travel-blue to-accent flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1">
                  <div className="glass-card p-4 rounded-2xl">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-accent rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                      <span className="text-text-secondary text-sm">
                        {reasoningEnabled ? 'RouteRishi is researching...' : 'RouteRishi is typing...'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-border/50 p-4">
        <div className="max-w-3xl mx-auto">
          {/* Guest Warning */}
          {isGuest && remainingMessages !== null && (
            <div className="mb-3 text-center">
              <div className={`inline-flex items-center space-x-2 px-3 py-2 rounded-lg text-sm ${
                remainingMessages > 0 
                  ? 'bg-warning/10 text-warning border border-warning/20' 
                  : 'bg-danger/10 text-danger border border-danger/20'
              }`}>
                <span>
                  {remainingMessages > 0 
                    ? `${remainingMessages} messages remaining in guest mode` 
                    : 'Guest message limit reached'
                  }
                </span>
              </div>
            </div>
          )}

          {/* Reasoning Toggle */}
          {!hasReachedLimit && (
            <div className="flex items-center justify-center mb-3">
              <button
                onClick={() => setReasoningEnabled(!reasoningEnabled)}
                className={`
                  flex items-center space-x-2 px-3 py-1.5 rounded-full text-xs transition-all duration-200
                  ${reasoningEnabled 
                    ? 'bg-accent/20 text-accent border border-accent/30' 
                    : 'bg-secondary/30 text-text-secondary border border-secondary/50'
                  }
                `}
              >
                <Brain className="w-3 h-3" />
                <span>{reasoningEnabled ? 'Reasoning ON' : 'Reasoning OFF'}</span>
              </button>
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex items-center space-x-3">
            <div className="flex-1">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={hasReachedLimit 
                  ? "Please sign up to continue chatting..." 
                  : "Ask me anything about your travel plans..."
                }
                className="input-field w-full resize-none min-h-[44px] max-h-32"
                rows={1}
                disabled={isLoading || hasReachedLimit}
              />
            </div>
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading || hasReachedLimit}
              className={`
                p-3 rounded-lg transition-all duration-200 flex-shrink-0
                ${inputValue.trim() && !isLoading && !hasReachedLimit
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
          <div className="flex items-center justify-center mt-2 text-xs text-text-secondary">
            <span>RouteRishi may make mistakes. Please check the information you receive.</span>
          </div>
        </div>
      </div>
    </div>
  );
}; 
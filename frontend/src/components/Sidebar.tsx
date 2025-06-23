import React from 'react';
import { 
  Plus, 
  MessageSquare, 
  Trash2, 
  User, 
  Settings, 
  X,
  Clock,
  Sparkles
} from 'lucide-react';
import icon from '../assets/icon.svg';
import type { Conversation } from '../types';

interface SidebarProps {
  conversations: Conversation[];
  currentConversationId: string | null;
  onSelectConversation: (conversationId: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (conversationId: string) => void;
  onCloseSidebar: () => void;
  collapsed?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  onCloseSidebar,
  collapsed = false,
}) => {
  const formatDate = (date: Date) => {
    const now = new Date();
    const diffInHours = Math.abs(now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 168) { // 7 days
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  const handleDeleteConversation = (e: React.MouseEvent, conversationId: string) => {
    e.stopPropagation();
    onDeleteConversation(conversationId);
  };

  return (
    <div className="h-full bg-secondary/90 backdrop-blur-xl border-r border-border/50 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-border/50">
        <div className="flex items-center justify-between">
          <div className={`flex items-center ${collapsed ? 'justify-center' : 'space-x-3'}`}>
            <div className="w-10 h-10 bg-gradient-to-br from-travel-blue to-accent rounded-xl flex items-center justify-center">
              <img src={icon} alt="RouteRishi" className="w-6 h-6 text-white" />
            </div>
            {!collapsed && (
              <div>
                <h1 className="text-xl font-bold gradient-text">RouteRishi</h1>
                <p className="text-xs text-text-secondary">Built to Get You Going</p>
              </div>
            )}
          </div>
          
          {/* Close button for mobile */}
          {!collapsed && (
            <button
              onClick={onCloseSidebar}
              className="lg:hidden p-2 hover:bg-secondary/60 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-text-secondary" />
            </button>
          )}
        </div>
        
        {/* New Chat Button */}
        <button
          onClick={onNewConversation}
          className={`w-full mt-4 flex items-center justify-center transition-all duration-200 ${
            collapsed 
              ? 'p-3 bg-accent/80 hover:bg-accent text-white rounded-lg hover:scale-105' 
              : 'button-primary space-x-2'
          }`}
          title={collapsed ? "New Chat" : ""}
        >
          <Plus className={collapsed ? "w-6 h-6" : "w-5 h-5"} />
          {!collapsed && <span>New Chat</span>}
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin p-2">
        <div className="space-y-1">
          {conversations.length === 0 ? (
            <div className="text-center py-8 px-4">
              <MessageSquare className="w-12 h-12 text-text-secondary/50 mx-auto mb-3" />
              {!collapsed && (
                <p className="text-text-secondary text-sm">
                  No conversations yet.<br />
                  Start a new chat to begin planning your journey!
                </p>
              )}
            </div>
          ) : (
            conversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => onSelectConversation(conversation.id)}
                className={`
                  group cursor-pointer p-3 rounded-lg transition-all duration-200 hover:bg-secondary/80
                  ${currentConversationId === conversation.id 
                    ? 'bg-accent/20 border-l-4 border-accent' 
                    : 'hover:bg-secondary/60'
                  }
                `}
                title={collapsed ? conversation.title : ""}
              >
                {collapsed ? (
                  <div className="flex justify-center">
                    <MessageSquare className="w-5 h-5 text-text-secondary" />
                  </div>
                ) : (
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <MessageSquare className="w-4 h-4 text-text-secondary flex-shrink-0" />
                        <h3 className="text-sm font-medium text-text-primary truncate">
                          {conversation.title}
                        </h3>
                      </div>
                      
                      {conversation.messages.length > 0 && (
                        <p className="text-xs text-text-secondary truncate">
                          {conversation.messages[conversation.messages.length - 1].content}
                        </p>
                      )}
                      
                      <div className="flex items-center space-x-2 mt-2">
                        <Clock className="w-3 h-3 text-text-secondary/60" />
                        <span className="text-xs text-text-secondary/60">
                          {formatDate(conversation.updatedAt)}
                        </span>
                        <span className="text-xs text-text-secondary/60">
                          • {conversation.messages.length} messages
                        </span>
                      </div>
                    </div>
                    
                    <button
                      onClick={(e) => handleDeleteConversation(e, conversation.id)}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-danger/20 rounded transition-all duration-200"
                    >
                      <Trash2 className="w-4 h-4 text-danger" />
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-border/50">
        {/* User Profile Placeholder */}
        {!collapsed && (
          <div className="flex items-center p-3 rounded-lg bg-secondary/50 hover:bg-secondary/70 transition-colors cursor-pointer space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-accent to-travel-blue rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-text-primary">Guest User</p>
              <p className="text-xs text-text-secondary">Ready to explore</p>
            </div>
            <Settings className="w-4 h-4 text-text-secondary" />
          </div>
        )}
        
        {/* Version/Status */}
        {!collapsed && (
          <div className="mt-3 text-center">
            <p className="text-xs text-text-secondary/60">
              RouteRishi v1.0 • Powered by AI
            </p>
          </div>
        )}
      </div>
    </div>
  );
}; 
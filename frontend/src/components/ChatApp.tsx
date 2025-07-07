import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useGuestLimits } from '../hooks/useGuestLimits';
import { Sidebar } from './Sidebar';
import { ChatInterface } from './ChatInterface';
import { WelcomeScreen } from './WelcomeScreen';
import { GuestLimitModal } from './GuestLimitModal';
import { useChat } from '../hooks/useChat';
import { Menu, PanelLeftClose, PanelLeftOpen, LogOut, User, AlertTriangle } from 'lucide-react';
import icon from '../assets/icon.svg';

export const ChatApp = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true); // Default open on desktop
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const chat = useChat();
  const { user, logout, isGuest } = useAuth();
  const guestLimits = useGuestLimits();

  const handleSendMessage = async (message: string, withReasoning?: boolean) => {
    // Check guest limits before sending
    if (isGuest && !guestLimits.incrementMessageCount()) {
      return; // Block the message if limit exceeded
    }

    // Close sidebar on mobile when sending message
    if (window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
    await chat.sendMessage(message, withReasoning);
  };

  const toggleSidebar = () => {
    if (window.innerWidth < 1024) {
      // Mobile: toggle open/close
      setSidebarOpen(!sidebarOpen);
    } else {
      // Desktop: toggle collapsed/expanded
      setSidebarCollapsed(!sidebarCollapsed);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const showWelcome = !chat.currentConversation || chat.messages.length === 0;

  return (
    <div className="h-screen bg-primary flex overflow-hidden">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed lg:static inset-y-0 left-0 z-50 
        ${sidebarCollapsed ? 'w-16 lg:w-16' : 'w-80 lg:w-80'}
        transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 transition-all duration-300 ease-in-out
      `}>
        <Sidebar
          conversations={chat.conversations}
          currentConversationId={chat.currentConversation?.id || null}
          onSelectConversation={chat.selectConversation}
          onNewConversation={isGuest ? undefined : chat.createNewConversation}
          onDeleteConversation={isGuest ? undefined : chat.deleteConversation}
          onCloseSidebar={() => setSidebarOpen(false)}
          collapsed={sidebarCollapsed}
          isGuest={isGuest}
        />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between p-4 bg-secondary/50 border-b border-border/50">
          <div className="flex items-center space-x-2">
            <button
              onClick={toggleSidebar}
              className="p-2 rounded-lg hover:bg-secondary/60 transition-colors lg:hidden"
            >
              <Menu className="w-6 h-6 text-text-primary" />
            </button>
            
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-travel-blue to-accent rounded-lg flex items-center justify-center">
                <img src={icon} alt="RouteRishi" className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-lg font-bold gradient-text">RouteRishi</h1>
            </div>
          </div>
          
          {/* User menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2 p-2 rounded-lg hover:bg-secondary/60 transition-colors"
            >
              {user?.photoURL ? (
                <img 
                  src={user.photoURL} 
                  alt={user.fullName}
                  className="w-8 h-8 rounded-full"
                />
              ) : (
                <div className="w-8 h-8 bg-accent/20 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-accent" />
                </div>
              )}
                             <div className="hidden sm:block text-left">
                 <p className="text-text-primary text-sm font-medium">{user?.fullName}</p>
                 {isGuest && (
                   <div className="text-xs">
                     <p className="text-text-secondary">Guest Mode</p>
                     {guestLimits.remainingMessages !== null && (
                       <p className="text-warning">
                         {guestLimits.remainingMessages} msgs left
                       </p>
                     )}
                   </div>
                 )}
               </div>
            </button>

            {/* User dropdown menu */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 glass-card rounded-lg shadow-lg py-2 z-50">
                <div className="px-4 py-2 border-b border-border/50">
                  <p className="text-text-primary font-medium">{user?.fullName}</p>
                  <p className="text-text-secondary text-sm">{user?.email}</p>
                  {isGuest && (
                    <span className="inline-block mt-1 px-2 py-1 bg-warning/20 text-warning text-xs rounded">
                      Guest Mode
                    </span>
                  )}
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 w-full px-4 py-2 text-text-primary hover:bg-secondary/60 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Sign Out</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col overflow-hidden relative">
          {/* Desktop sidebar toggle */}
          <button
            onClick={toggleSidebar}
            className="hidden lg:flex absolute top-4 left-4 z-10 p-2 bg-secondary/80 hover:bg-secondary border border-border/50 rounded-lg transition-all duration-200 hover:scale-105"
            title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {sidebarCollapsed ? (
              <PanelLeftOpen className="w-5 h-5 text-text-primary" />
            ) : (
              <PanelLeftClose className="w-5 h-5 text-text-primary" />
            )}
          </button>

          {showWelcome ? (
            <WelcomeScreen 
              onSendMessage={handleSendMessage} 
              isGuest={isGuest}
              remainingMessages={guestLimits.remainingMessages}
            />
          ) : (
            <ChatInterface
              messages={chat.messages}
              isLoading={chat.isLoading}
              isAgentThinking={chat.isAgentThinking}
              agentThoughts={chat.agentThoughts}
              error={chat.error}
              onSendMessage={handleSendMessage}
              onRetry={chat.retryLastMessage}
              onClearError={chat.clearError}
              isGuest={isGuest}
              hasReachedLimit={guestLimits.hasReachedLimit}
              remainingMessages={guestLimits.remainingMessages}
            />
          )}
        </div>
      </div>

      {/* Click outside to close user menu */}
      {showUserMenu && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setShowUserMenu(false)} 
        />
      )}

      {/* Guest limit modal */}
      <GuestLimitModal
        isOpen={guestLimits.showLimitWarning}
        onClose={guestLimits.dismissWarning}
        messageLimit={guestLimits.messageLimit}
      />
    </div>
  );
};

export default ChatApp; 
import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatInterface } from './components/ChatInterface';
import { WelcomeScreen } from './components/WelcomeScreen';
import { useChat } from './hooks/useChat';
import { Menu, PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import icon from './assets/icon.svg';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true); // Default open on desktop
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const chat = useChat();

  const handleSendMessage = async (message: string) => {
    // Close sidebar on mobile when sending message
    if (window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
    await chat.sendMessage(message);
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
          onNewConversation={chat.createNewConversation}
          onDeleteConversation={chat.deleteConversation}
          onCloseSidebar={() => setSidebarOpen(false)}
          collapsed={sidebarCollapsed}
        />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between p-4 bg-secondary/50 border-b border-border/50 lg:hidden">
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-lg hover:bg-secondary/60 transition-colors"
          >
            <Menu className="w-6 h-6 text-text-primary" />
          </button>
          
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-travel-blue to-accent rounded-lg flex items-center justify-center">
              <img src={icon} alt="RouteRishi" className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-lg font-bold gradient-text">RouteRishi</h1>
          </div>
          
          <div className="w-10" /> {/* Spacer for centering */}
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
            <WelcomeScreen onSendMessage={handleSendMessage} />
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
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

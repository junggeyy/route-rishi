import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatInterface } from './components/ChatInterface';
import { WelcomeScreen } from './components/WelcomeScreen';
import { useChat } from './hooks/useChat';
import { Menu } from 'lucide-react';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const chat = useChat();

  const handleSendMessage = async (message: string) => {
    setSidebarOpen(false); // Close sidebar on mobile when sending message
    await chat.sendMessage(message);
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
        fixed lg:static inset-y-0 left-0 z-50 w-80 lg:w-80
        transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 transition-transform duration-300 ease-in-out
      `}>
        <Sidebar
          conversations={chat.conversations}
          currentConversationId={chat.currentConversation?.id || null}
          onSelectConversation={chat.selectConversation}
          onNewConversation={chat.createNewConversation}
          onDeleteConversation={chat.deleteConversation}
          onCloseSidebar={() => setSidebarOpen(false)}
        />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile header */}
        <div className="lg:hidden flex items-center justify-between p-4 bg-secondary/50 border-b border-border/50">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-lg hover:bg-secondary/60 transition-colors"
          >
            <Menu className="w-6 h-6 text-text-primary" />
          </button>
          
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-travel-blue to-accent rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">R</span>
            </div>
            <h1 className="text-lg font-bold gradient-text">RouteRishi</h1>
          </div>
          
          <div className="w-10" /> {/* Spacer for centering */}
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
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

import React, { useState, useRef } from 'react';
import { 
  Sparkles,
  Globe,
  Star,
  Send,
  Loader2
} from 'lucide-react';
import icon from '../assets/icon.svg';

interface WelcomeScreenProps {
  onSendMessage: (message: string) => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSendMessage }) => {
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;
    
    setIsLoading(true);
    await onSendMessage(inputValue.trim());
    setInputValue('');
    setIsLoading(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const sampleQuestions = [
    "Plan a 7-day trip to Japan starting next month",
    "Find flights from New York to London for 2 people", 
    "What's the weather like in Bali this time of year?",
    "Show me hotels in Paris under $200 per night"
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 overflow-y-auto">
      <div className="max-w-3xl w-full mx-auto space-y-8">
        {/* Hero Section */}
        <div className="text-center space-y-6">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-travel-blue to-accent rounded-xl mb-4">
            <img src={icon} alt="RouteRishi" className="w-8 h-8 text-white" />
          </div>
          
          <div className="space-y-3">
            <h1 className="text-4xl font-bold gradient-text">
              Welcome to RouteRishi
            </h1>
            <p className="text-lg text-text-secondary">
              Smarter Trips. Zero Hassle.
            </p>
          </div>
        </div>

        {/* Chat Input */}
        <div className="space-y-6">
          <form onSubmit={handleSubmit} className="relative">
            <div className="relative">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Message RouteRishi..."
                className="w-full min-h-[120px] p-4 pr-12 bg-secondary/50 border border-border/50 rounded-xl text-text-primary placeholder-text-secondary/60 resize-none focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent/50 transition-all duration-200"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!inputValue.trim() || isLoading}
                className={`
                  absolute bottom-3 right-3 p-2 rounded-lg transition-all duration-200
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
            </div>
          </form>

          {/* Sample Questions */}
          <div className="space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {sampleQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => setInputValue(question)}
                  className="text-left p-4 bg-secondary/30 hover:bg-secondary/50 border border-border/30 hover:border-accent/30 rounded-lg transition-all duration-200 group"
                >
                  <p className="text-text-secondary group-hover:text-text-primary transition-colors text-sm">
                    {question}
                  </p>
                </button>
              ))}
            </div>
          </div>

          {/* Features */}
          <div className="flex flex-wrap justify-center gap-2 text-xs text-text-secondary">
            <div className="flex items-center space-x-1 bg-secondary/30 px-2 py-1 rounded-full">
              <Star className="w-3 h-3 text-travel-blue" />
              <span>Real-time Data</span>
            </div>
            <div className="flex items-center space-x-1 bg-secondary/30 px-2 py-1 rounded-full">
              <Star className="w-3 h-3 text-travel-blue" />
              <span>Flight Search</span>
            </div>
            <div className="flex items-center space-x-1 bg-secondary/30 px-2 py-1 rounded-full">
              <Star className="w-3 h-3 text-travel-blue" />
              <span>Hotel Booking</span>
            </div>
            <div className="flex items-center space-x-1 bg-secondary/30 px-2 py-1 rounded-full">
              <Star className="w-3 h-3 text-travel-blue" />
              <span>Weather & Currency</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 
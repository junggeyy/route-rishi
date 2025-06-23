import React, { useState } from 'react';
import { 
  Plane, 
  Building, 
  Map, 
  Cloud, 
  DollarSign, 
  Sparkles,
  ArrowRight,
  Globe,
  Star
} from 'lucide-react';
import { quickActions } from '../data/messageTemplates';

interface WelcomeScreenProps {
  onSendMessage: (message: string) => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSendMessage }) => {
  const [hoveredAction, setHoveredAction] = useState<string | null>(null);

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 overflow-y-auto">
      <div className="max-w-4xl w-full space-y-8">
        {/* Hero Section */}
        <div className="text-center space-y-6">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-travel-blue to-accent rounded-2xl mb-4">
            <Globe className="w-10 h-10 text-white" />
          </div>
          
          <div className="space-y-2">
            <h1 className="text-4xl lg:text-5xl font-bold gradient-text">
              Welcome to RouteRishi
            </h1>
            <p className="text-xl text-text-secondary max-w-2xl mx-auto">
              Your AI-powered travel companion ready to plan amazing journeys with real-time data ✈️
            </p>
          </div>

          {/* Features */}
          <div className="flex flex-wrap justify-center gap-3 text-sm text-text-secondary">
            <div className="flex items-center space-x-1 bg-secondary/50 px-3 py-1 rounded-full">
              <Star className="w-4 h-4 text-travel-blue" />
              <span>Real-time Flight Data</span>
            </div>
            <div className="flex items-center space-x-1 bg-secondary/50 px-3 py-1 rounded-full">
              <Star className="w-4 h-4 text-travel-blue" />
              <span>Hotel Recommendations</span>
            </div>
            <div className="flex items-center space-x-1 bg-secondary/50 px-3 py-1 rounded-full">
              <Star className="w-4 h-4 text-travel-blue" />
              <span>Weather Forecasts</span>
            </div>
            <div className="flex items-center space-x-1 bg-secondary/50 px-3 py-1 rounded-full">
              <Star className="w-4 h-4 text-travel-blue" />
              <span>Currency Exchange</span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold text-center text-text-primary">
            What would you like to do today?
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {quickActions.map((action) => (
              <button
                key={action.id}
                onClick={() => onSendMessage(action.action)}
                onMouseEnter={() => setHoveredAction(action.id)}
                onMouseLeave={() => setHoveredAction(null)}
                className={`
                  glass-card p-6 text-left transition-all duration-300 hover:scale-105 hover:border-accent/50
                  ${hoveredAction === action.id ? 'bg-accent/10' : ''}
                `}
              >
                <div className="flex items-start space-x-4">
                  <div className="text-3xl flex-shrink-0">
                    {action.icon}
                  </div>
                  <div className="flex-1 space-y-2">
                    <h3 className="font-semibold text-text-primary flex items-center justify-between">
                      {action.title}
                      <ArrowRight className={`
                        w-4 h-4 text-accent transition-transform duration-300
                        ${hoveredAction === action.id ? 'translate-x-1' : ''}
                      `} />
                    </h3>
                    <p className="text-text-secondary text-sm leading-relaxed">
                      {action.description}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Example Queries */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-center text-text-primary">
            Or try asking me something like:
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              "Plan a 7-day trip to Japan starting next month",
              "Find flights from New York to London for 2 people",
              "What's the weather like in Bali this time of year?",
              "Show me hotels in Paris under $200 per night",
              "What's the current exchange rate for Euros?",
              "Plan a romantic weekend getaway to Italy"
            ].map((query, index) => (
              <button
                key={index}
                onClick={() => onSendMessage(query)}
                className="text-left p-4 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-all duration-200 hover:border-l-4 hover:border-accent border border-transparent"
              >
                <p className="text-text-secondary hover:text-text-primary transition-colors">
                  "{query}"
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* Footer Message */}
        <div className="text-center pt-8">
          <div className="inline-flex items-center space-x-2 text-text-secondary text-sm">
            <Sparkles className="w-4 h-4 text-travel-blue" />
            <span>Just start typing to begin your travel planning journey!</span>
            <Sparkles className="w-4 h-4 text-travel-blue" />
          </div>
        </div>
      </div>
    </div>
  );
}; 
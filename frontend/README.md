# RouteRishi Frontend

A modern, dark-themed React frontend for RouteRishi, an AI-powered travel agent chatbot that plans complete itineraries with real-time flight, hotel, weather, and currency data.

## 🚀 Features

### ✅ Completed Features

- **Modern Dark Theme**: Sophisticated dark UI with travel-inspired accent colors
- **Responsive Design**: Mobile-first approach with collapsible sidebar
- **Chat Interface**: Full conversation management with message history
- **Welcome Screen**: Interactive landing page with quick action templates
- **Agent Thinking Display**: Real-time visualization of AI agent's thought process
- **Message Templates**: Pre-built templates for common travel queries
- **Conversation Management**: Create, select, and delete conversations
- **Local Storage**: Automatic persistence of chat history
- **Error Handling**: Comprehensive error states with retry functionality
- **Loading States**: Beautiful loading animations and skeleton screens

### 🎨 UI Components

- **Sidebar**: Collapsible navigation with conversation history
- **Chat Interface**: Message bubbles with user/AI distinction
- **Welcome Screen**: Hero section with quick action cards
- **Message Input**: Auto-resizing textarea with send button
- **Agent Thoughts**: Expandable thinking process display
- **Error Banner**: Dismissible error messages with retry options

### 🛠 Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with custom dark theme
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State Management**: React Hooks (useState, useEffect, useCallback)

## 🎨 Design System

### Color Palette
```css
Primary: #1a1b23 (Deep dark background)
Secondary: #2a2d3a (Card/sidebar background)  
Accent: #3b82f6 (Travel blue - CTAs and highlights)
Success: #10b981 (Confirmation green)
Warning: #f59e0b (Attention amber)
Travel Blue: #00ffe0 (Brand accent color)
Text Primary: #f8fafc (White text)
Text Secondary: #94a3b8 (Muted text)
Border: #374151 (Subtle borders)
```

### Key UI Patterns
- **Glass Card**: `bg-secondary/80 backdrop-blur-xl border border-border/50`
- **Button Primary**: `bg-accent hover:bg-accent/90 text-white`
- **Message Bubbles**: User (right, blue) vs AI (left, glass card)
- **Gradient Text**: Travel blue to accent gradient for branding

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── Sidebar.tsx      # Navigation and chat history
│   │   ├── WelcomeScreen.tsx # Landing page with quick actions  
│   │   └── ChatInterface.tsx # Main chat area with messages
│   ├── hooks/               # Custom React hooks
│   │   └── useChat.ts       # Chat state management
│   ├── services/            # API communication
│   │   └── api.ts           # Backend integration
│   ├── data/                # Static data and templates
│   │   └── messageTemplates.ts # Pre-built message templates
│   ├── types/               # TypeScript interfaces
│   │   └── index.ts         # All type definitions
│   ├── App.tsx              # Main app component
│   ├── index.css            # Tailwind CSS and custom styles
│   └── main.tsx             # React entry point
├── public/                  # Static assets
├── tailwind.config.js       # Tailwind configuration
├── postcss.config.js        # PostCSS configuration
└── package.json             # Dependencies and scripts
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

4. Open browser to `http://localhost:5173`

### Backend Integration

The frontend expects the backend to be running on `http://localhost:8000` with the following endpoints:

- `POST /api/v1/chat/message` - Send messages to AI agent
- `GET /api/v1/flights/search` - Search flights
- `GET /api/v1/hotels/search` - Search hotels  
- `GET /api/v1/weather/` - Get weather forecasts
- `GET /api/v1/currency/` - Get exchange rates

## 📱 Features Overview

### Welcome Screen
- **Hero Section**: Branded landing with feature highlights
- **Quick Actions**: 5 clickable cards for common tasks:
  - Find Flights ✈️
  - Book Hotels 🏨  
  - Plan Trip 🗺️
  - Check Weather 🌤️
  - Currency Rates 💱
- **Example Queries**: Clickable example questions
- **Responsive Grid**: Adapts to mobile/tablet/desktop

### Chat Interface
- **Message History**: Persistent conversation storage
- **Real-time Responses**: Streaming AI responses with thinking display
- **Auto-scroll**: Smooth scrolling to new messages
- **Message Formatting**: Basic markdown support (bold, italic, code)
- **Timestamps**: Relative time display for all messages
- **Error Recovery**: Retry failed messages, clear errors

### Sidebar Navigation  
- **Conversation List**: All chats with titles and previews
- **New Chat Button**: Prominent call-to-action
- **User Profile**: Placeholder for future authentication
- **Mobile Responsive**: Transforms to overlay on small screens
- **Search/Filter**: Ready for future conversation search

## 🔌 API Integration

### Chat API (Mock Implementation)
Currently uses mock responses that simulate the real AI agent:

```typescript
// Mock response examples
const responses = {
  flights: "I'd be happy to help you find flights! To get started...",
  hotels: "I can help you find great accommodations! Let me know...", 
  weather: "I can check the weather forecast for your destination...",
  currency: "I can help you with currency exchange rates...",
  planning: "Exciting! I love helping plan complete trips..."
}
```

### Real Backend Integration
Ready to connect to actual RouteRishi backend with:
- Agent conversation endpoint
- Flight search integration  
- Hotel booking integration
- Weather data integration
- Currency rate integration

## 🎯 Current Status

### ✅ Working Features
- Full React app setup with TypeScript
- Modern dark theme with Tailwind CSS
- Complete chat interface with message history
- Responsive sidebar navigation
- Welcome screen with quick actions
- Mock AI responses for testing
- Local storage persistence
- Error handling and loading states

### 🚧 In Progress
- Tailwind CSS configuration (some custom classes not loading)
- Backend chat endpoint integration
- Real-time agent thought process display

### 📋 Next Steps
1. Fix Tailwind CSS custom color classes
2. Connect to real backend chat endpoint
3. Add WebSocket for real-time agent thoughts
4. Implement Firebase Authentication
5. Add confirmation cards for booking flows
6. Export/share itinerary functionality
7. Dark/light theme toggle
8. Voice input integration

## 🐛 Known Issues

1. **Tailwind CSS**: Custom color classes (`bg-primary`, etc.) not being recognized
   - Need to verify Tailwind configuration
   - May need to restart dev server after config changes

2. **Backend Connection**: Currently using mock responses
   - Real backend chat endpoint created but not tested
   - Need to verify CORS configuration

## 🤝 Contributing

### Code Style
- TypeScript strict mode enabled
- ESLint + Prettier configuration
- Functional components with hooks
- Tailwind CSS for all styling
- Component composition over inheritance

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/chat-improvements

# Make changes and commit
git commit -m "feat: add message reaction system"

# Push and create PR
git push origin feature/chat-improvements
```

## 📄 License

This project is part of the RouteRishi travel planning platform.

---

**RouteRishi Frontend v1.0** - Built with ❤️ for modern travel planning

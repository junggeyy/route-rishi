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

## Authentication
- **Email/Password Login & Signup** - Secure user authentication
- **Google OAuth Integration** - Quick signup/login with Google (requires backend setup)
- **Guest Mode** - Try the app with limited functionality (5 messages)
- **Protected Routes** - Automatic redirection for authenticated/unauthenticated users

### Guest Mode Limitations
- Limited to 5 messages per session
- Cannot create new conversations
- Cannot delete conversations
- Chat history not persisted
- No access to premium features

### User Interface
- **Glass Morphism Design** - Modern, translucent UI elements
- **Dark Theme** - Optimized for comfortable viewing
- **Responsive Layout** - Works seamlessly on desktop and mobile
- **Real-time Chat** - Smooth messaging experience with typing indicators
- **Sidebar Navigation** - Easy access to conversation history and settings

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Backend API running (see backend documentation)

### Installation

1. **Clone and navigate to frontend**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment Setup**
   ```bash
   cp .env.example .env
   ```
   
   Update `.env` with your configuration:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open in browser**
   ```
   http://localhost:5173
   ```

## Authentication Flow

### For New Users
1. Visit `/signup` to create an account
2. Fill in full name, email, and password
3. Alternatively, click "Sign up with Google"
4. Or select "Continue as Guest" for limited access

### For Existing Users
1. Visit `/login` to sign in
2. Enter email and password
3. Or use "Continue with Google"
4. Or select "Continue as Guest"

### Guest Mode
- Perfect for trying out the app
- No registration required
- 5 message limit per session
- Upgrade prompt after limit reached

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── components/          # React components
│   ├── ChatApp.tsx     # Main chat interface
│   ├── ChatInterface.tsx # Chat message area
│   ├── Sidebar.tsx     # Conversation sidebar
│   ├── LoginPage.tsx   # Authentication pages
│   ├── SignupPage.tsx
│   ├── ProtectedRoute.tsx
│   └── GuestLimitModal.tsx
├── contexts/           # React contexts
│   └── AuthContext.tsx # Authentication state management
├── hooks/              # Custom React hooks
│   ├── useAuth.ts      # Authentication hook
│   ├── useChat.ts      # Chat functionality
│   └── useGuestLimits.ts # Guest limitations
├── services/           # API and external services
│   ├── authService.ts  # Authentication API calls
│   └── api.ts          # Main API service
├── types/              # TypeScript type definitions
│   ├── index.ts        # General types
│   └── auth.ts         # Authentication types
└── assets/             # Static assets
```

## Key Components

### Authentication Components
- **LoginPage** - Email/password and social login
- **SignupPage** - User registration with validation
- **ProtectedRoute** - Route protection wrapper
- **AuthContext** - Global authentication state

### Chat Components
- **ChatApp** - Main application container
- **ChatInterface** - Message display and input
- **Sidebar** - Conversation management
- **WelcomeScreen** - First-time user experience

### Guest Limitations
- **useGuestLimits** - Hook for managing guest restrictions
- **GuestLimitModal** - Upgrade prompt when limit reached

## Styling

The app uses:
- **Tailwind CSS** - Utility-first CSS framework
- **Custom Design System** - Consistent colors and components
- **Glass Morphism** - Modern translucent effects
- **Responsive Design** - Mobile-first approach

## API Integration

The frontend communicates with the backend API for:
- User authentication (login, signup, logout)
- Chat message processing
- Conversation management
- Real-time features

## Development Notes

### Adding New Features
1. Create components in appropriate directories
2. Add TypeScript types in `types/`
3. Update routing in `App.tsx` if needed
4. Add any new API calls to services

### State Management
- Authentication state managed by AuthContext
- Chat state managed by useChat hook
- Guest limitations managed by useGuestLimits hook

### Protected Routes
All chat functionality requires authentication. Guest users have limited access with clear upgrade paths to full accounts.

## Deployment

Build the application:
```bash
npm run build
```

The `dist/` folder contains the production build ready for deployment to any static hosting service.

## Environment Variables

Required variables in `.env`:
- `VITE_API_URL` - Backend API base URL

Optional (for future Google OAuth):
- `VITE_FIREBASE_*` - Firebase configuration

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check `VITE_API_URL` in `.env`
   - Ensure backend is running
   - Check CORS configuration

2. **Authentication Not Working**
   - Verify backend auth endpoints
   - Check localStorage for tokens
   - Clear browser storage if needed

3. **Guest Mode Issues**
   - Check localStorage for guest data
   - Clear guest data: `localStorage.clear()`

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

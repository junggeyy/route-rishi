# RouteRishi -- Smarter Trips. Zero Hassle.

RouteRishi is an intelligent travel planning application that combines conversational AI with real-time travel data to create comprehensive trip itineraries. The system leverages LangChain agents, Google Gemini LLM, and multiple travel APIs to provide users with personalized travel recommendations, flight and hotel searches, weather forecasts, and PDF itinerary generation.

## Core Features

- **LangChain-powered conversational AI agent** with Google Gemini integration, multi-tool executor, and real-time reasoning visualization for travel planning
- **External API integration** for real-time flight searches, hotel availability, weather forecasts, and currency conversion
- **Firebase Authentication** system supporting email/password, Google OAuth, and rate-limited guest access with JWT token management
- **Firestore NoSQL database** for scalable data storage, persistent conversation history, and cross-device synchronization
- **Dynamic PDF itinerary generation** with Firebase Storage integration for cloud-hosted downloadable travel documents
- **SSE** for real-time conversation updates and AI *thought-process* visualization

## Tech Stack

**Backend**
- **FastAPI** for async API development
- **Firebase Admin SDK** for authentication and data management
- **Firestore** for NoSQL document storage
- **Firebase Storage** for file hosting
- **Pydantic** for data validation and type safety

**AI & LLM Integration**
- **LangChain** for AI agent orchestration and tool management
- **Google Generative AI** for conversation handling
- **Multi-tool Executor** for intelligent tool selection and execution
- **Custom tool definitions** for travel-specific functionality

**External APIs**<br>
The following external APIs are required for full functionality:
- `AMADEUS_API_KEY` and `AMADEUS_API_SECRET`: For flight and hotel data
- `TomorrowIO_API_KEY`: For weather forecasting
- `ExchangeRate_API_KEY`: For currency exchange rates
- `GEMINI_API_KEY`: For Google Gemini LLM access
- `FIREBASE_SERVICE_ACCOUNT_KEY`: Firebase service account JSON
- `FIREBASE_WEB_API_KEY`: Firebase web API key
- `FIREBASE_STORAGE_BUCKET`: Firebase storage bucket name
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`: For OAuth integration
- `JWT_SECRET_KEY`: For secure JWT token generation

**Frontend**
- React with TypeScript
- Vite
- Tailwind CSS 

## Running the Application

**Backend Setup:**
```bash
# Install dependencies
pip install -r requirements.txt

# Set up env and configure API keys & Firebase credentials
cp .env.example .env

# Run the development server
uvicorn app:app --reload
```

**Frontend Setup:**
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The backend API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs` and the frontend at `http://localhost:5173`.

## Screenshots

<table>
  <tr>
    <td>![ChatUI](https://i.imgur.com/cu3f3YG.png)</td>
    <td>![FlightSearch](https://i.imgur.com/KbcJb4W.png)</td>
    <td>![PDFCreation](https://i.imgur.com/cujdu42.png)</td>
  </tr>
  <tr>
    <td>![ActivityWeather](https://i.imgur.com/89CfijN.png)</td>
    <td>![SavedItinerary](https://i.imgur.com/Y0xjbBC.png)</td>
    <td>![GuestMode](https://i.imgur.com/P91ux7G.png)</td>
  </tr>
</table
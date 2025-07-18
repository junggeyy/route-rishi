import axios from 'axios';
import type {
  FlightOffer,
  FlightSearchParams,
  Hotel,
  HotelSearchParams,
  WeatherForecast,
  ExchangeRate,
  ApiResponse,
  Message,
  ToolCall,
  SavedItinerary,
  ConversationMetadata,
  Conversation,
} from '../types';

// API Configuration - Use environment variable with localhost fallback
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Flight API
export const flightApi = {
  searchFlights: async (params: FlightSearchParams): Promise<FlightOffer[]> => {
    try {
      const response = await api.get('/flights/search', { params });
      return response.data.flight_offers || [];
    } catch (error) {
      console.error('Flight search error:', error);
      throw new Error('Failed to search flights');
    }
  },
};

// Hotel API
export const hotelApi = {
  searchHotels: async (params: HotelSearchParams): Promise<Hotel[]> => {
    try {
      const response = await api.get('/hotels/search', { params });
      return response.data || [];
    } catch (error) {
      console.error('Hotel search error:', error);
      throw new Error('Failed to search hotels');
    }
  },
};

// Weather API
export const weatherApi = {
  getWeatherForecast: async (city: string, timesteps: '1d' | '1h' = '1d'): Promise<WeatherForecast> => {
    try {
      const response = await api.get('/weather/', {
        params: { city, timesteps }
      });
      return response.data;
    } catch (error) {
      console.error('Weather forecast error:', error);
      throw new Error('Failed to get weather forecast');
    }
  },
};

// Currency API
export const currencyApi = {
  getExchangeRate: async (currencyCode: string): Promise<ExchangeRate> => {
    try {
      const response = await api.get('/currency/', {
        params: { target_currency_code: currencyCode }
      });
      return response.data;
    } catch (error) {
      console.error('Currency exchange error:', error);
      throw new Error('Failed to get exchange rate');
    }
  },
};

// Chat API (we'll need to create this endpoint in the backend)
export const chatApi = {
  sendMessage: async (message: string, conversationId: string, token?: string): Promise<string> => {
    try {
      const headers: any = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await api.post('/chat/message', {
        message,
        conversation_id: conversationId,
      }, { headers });
      return response.data.response;
    } catch (error) {
      console.error('Chat message error:', error);
      throw new Error('Failed to send message');
    }
  },

  sendMessageWithReasoning: async (
    message: string, 
    conversationId: string,
    token?: string
  ): Promise<{
    response: string;
    toolCalls: ToolCall[];
    executionTimeMs: number;
  }> => {
    try {
      const headers: any = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await api.post('/chat/message-with-reasoning', {
        message,
        conversation_id: conversationId,
      }, { headers });
      
      return {
        response: response.data.response,
        toolCalls: response.data.tool_calls || [],
        executionTimeMs: response.data.total_execution_time_ms || 0,
      };
    } catch (error) {
      console.error('Chat reasoning error:', error);
      throw new Error('Failed to send message with reasoning');
    }
  },

  sendMessageMock: async (message: string, conversationId: string): Promise<string> => {
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
    
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('flight') || lowerMessage.includes('fly')) {
      return `🛫 I'd be happy to help you find flights! To get started, I'll need a few details:
      
- Where are you flying from? (e.g., JFK, LAX, LHR)
- Where would you like to go?
- What dates are you thinking?
- How many travelers?

Once I have these details, I can search for the best flight options for you! ✈️`;
    }
    
    if (lowerMessage.includes('hotel') || lowerMessage.includes('accommodation')) {
      return `🏨 I can help you find great accommodations! Let me know:
      
- Which city are you visiting?
- Check-in and check-out dates?
- How many guests?
- Any preferences (star rating, amenities, budget)?

I'll find the perfect place for your stay! 🌟`;
    }
    
    if (lowerMessage.includes('weather')) {
      return `🌤️ I can check the weather forecast for your destination! Just tell me which city you're interested in, and I'll get you the latest weather information to help you pack accordingly. 

Keep in mind I can provide forecasts for the next 5 days. For longer trips, I can give you seasonal weather patterns too! 🌈`;
    }
    
    if (lowerMessage.includes('currency') || lowerMessage.includes('exchange')) {
      return `💱 I can help you with currency exchange rates! Tell me which currency you'd like to convert to USD, and I'll get you the current exchange rate.

This is helpful for budgeting your trip and understanding local prices. Which currency are you interested in? 💰`;
    }
    
    if (lowerMessage.includes('plan') || lowerMessage.includes('itinerary') || lowerMessage.includes('trip')) {
      return `🗺️ Exciting! I love helping plan complete trips! For a full itinerary, I'll need:

**Basic Info:**
- Destination city/country
- Travel dates (departure and return)
- Number of travelers
- Budget range
- Travel style (luxury, mid-range, budget)

**Preferences:**
- Must-see attractions or activities
- Food preferences
- Accommodation preferences

Once I have these details, I can create a day-by-day itinerary with flights, hotels, activities, restaurant recommendations, and local tips! 🎯`;
    }

    return `Hello! I'm RouteRishi, your AI travel companion! 🌍 I'm here to help you plan amazing trips with real-time data.

I can help you with:
- ✈️ Finding flights
- 🏨 Booking hotels
- 🌤️ Weather forecasts
- 💱 Currency exchange rates
- 🗺️ Complete trip planning

What would you like to explore today? Just tell me about your travel plans and I'll get started! 😊`;
  },
};

// Conversation API
export const conversationApi = {
  getUserConversations: async (token: string, page: number = 1, pageSize: number = 20): Promise<ConversationMetadata[]> => {
    try {
      const response = await api.get('/conversations/', {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        params: {
          page,
          page_size: pageSize
        }
      });
      return response.data || [];
    } catch (error) {
      console.error('Get user conversations error:', error);
      throw new Error('Failed to get conversations');
    }
  },

  getConversation: async (token: string, conversationId: string): Promise<Conversation> => {
    try {
      const response = await api.get(`/conversations/${conversationId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('Get conversation error:', error);
      throw new Error('Failed to get conversation');
    }
  },

  getConversationMessages: async (
    token: string, 
    conversationId: string, 
    page: number = 1, 
    pageSize: number = 50,
    order: 'asc' | 'desc' = 'asc'
  ): Promise<Message[]> => {
    try {
      const response = await api.get(`/conversations/${conversationId}/messages`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        params: {
          page,
          page_size: pageSize,
          order
        }
      });
      const rawMessages = response.data || [];
      // Convert timestamp strings to Date objects for proper rendering
      const convertedMessages: Message[] = rawMessages.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp),
      }));
      return convertedMessages;
    } catch (error) {
      console.error('Get conversation messages error:', error);
      throw new Error('Failed to get conversation messages');
    }
  },

  deleteConversation: async (token: string, conversationId: string): Promise<void> => {
    try {
      await api.delete(`/conversations/${conversationId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
    } catch (error) {
      console.error('Delete conversation error:', error);
      throw new Error('Failed to delete conversation');
    }
  },
};

// Itinerary API
export const itineraryApi = {
  getSavedItineraries: async (token: string): Promise<SavedItinerary[]> => {
    try {
      const response = await api.get('/itinerary/saved', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      return response.data || [];
    } catch (error) {
      console.error('Get saved itineraries error:', error);
      throw new Error('Failed to get saved itineraries');
    }
  },

  deleteSavedItinerary: async (token: string, itineraryId: string): Promise<void> => {
    try {
      await api.delete(`/itinerary/saved/${itineraryId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
    } catch (error) {
      console.error('Delete saved itinerary error:', error);
      throw new Error('Failed to delete saved itinerary');
    }
  },

  deleteAllSavedItineraries: async (token: string): Promise<void> => {
    try {
      await api.delete('/itinerary/saved', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
    } catch (error) {
      console.error('Delete all saved itineraries error:', error);
      throw new Error('Failed to delete all saved itineraries');
    }
  },
};

// Health check
export const healthApi = {
  checkHealth: async (): Promise<any> => {
    try {
      const response = await api.get('/');
      return response.data;
    } catch (error) {
      console.error('Health check error:', error);
      throw new Error('Backend is not available');
    }
  },
};

export default api; 

// Export the base URL for SSE connections
export { API_BASE_URL }; 
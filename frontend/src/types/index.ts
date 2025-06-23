// Chat and Conversation Types
export interface Message {
  id: string;
  content: string;
  type: 'user' | 'ai';
  timestamp: Date;
  conversationId: string;
  toolCalls?: ToolCall[];
  executionTimeMs?: number;
}

export interface ToolCall {
  tool_name: string;
  input_params: Record<string, any>;
  output: string;
  status: 'running' | 'completed' | 'error';
  execution_time_ms?: number;
}

export interface AgentThought {
  id: string;
  action: string;
  input: any;
  output: string;
  timestamp: Date;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

// Flight Types (matching backend schemas)
export interface FlightSegment {
  departure_airport_code: string;
  departure_time: string;
  arrival_airport_code: string;
  arrival_time: string;
  carrier_code: string;
  flight_number: string;
  duration: string;
  number_of_stops: number;
}

export interface FlightItinerary {
  duration: string;
  segments: FlightSegment[];
}

export interface FlightOffer {
  id: string;
  price_total: number;
  currency: string;
  itineraries: FlightItinerary[];
  number_of_bookable_seats: number;
  last_ticketing_date: string;
  validating_airline_codes: string[];
}

export interface FlightSearchParams {
  origin_code: string;
  destination_code: string;
  departure_date: string;
  num_adults: number;
  return_date?: string;
  num_children?: number;
  travel_class?: 'ECONOMY' | 'PREMIUM_ECONOMY' | 'BUSINESS' | 'FIRST';
  non_stop?: boolean;
  max_price?: number;
  max_flights?: number;
}

// Hotel Types (matching backend schemas)
export interface HotelRoom {
  type: string;
  description: string;
}

export interface HotelOffer {
  id: string;
  checkInDate: string;
  checkOutDate: string;
  roomQuantity: number;
  rateCode: string;
  rateFamilyEstimated?: {
    code: string;
    type: string;
  };
  room: HotelRoom;
  guests: {
    adults: number;
  };
  price: {
    currency: string;
    base: string;
    total: string;
    variations?: {
      average?: {
        base: string;
      };
    };
  };
  policies?: {
    cancellations?: Array<{
      type: string;
      amount?: string;
      deadline?: string;
    }>;
    paymentType?: string;
    guarantee?: {
      acceptedPayments?: {
        creditCards?: string[];
        methods?: string[];
      };
    };
  };
  self?: string;
}

export interface Hotel {
  type: string;
  hotelId: string;
  chainCode?: string;
  dupeId: string;
  name: string;
  rating?: string;
  cityCode: string;
  latitude: number;
  longitude: number;
  hotelDistance?: {
    distance: number;
    distanceUnit: string;
  };
  address?: {
    lines?: string[];
    postalCode?: string;
    cityName?: string;
    countryCode?: string;
  };
  contact?: {
    phone?: string;
    fax?: string;
    email?: string;
  };
  description?: {
    lang: string;
    text: string;
  };
  amenities?: string[];
  media?: Array<{
    uri: string;
    category: string;
  }>;
  available: boolean;
  offers: HotelOffer[];
  self?: string;
}

export interface HotelSearchParams {
  city_code: string;
  check_in_date: string;
  check_out_date: string;
  num_adults: number;
  num_rooms?: number;
  radius?: number;
  chain_codes?: string[];
  ratings?: string[];
  currency?: string;
  price_range?: string;
  best_rate_only?: boolean;
  max_hotels_to_search?: number;
}

// Weather Types
export interface WeatherData {
  temperature: number;
  temperature_max: number;
  temperature_min: number;
  humidity: number;
  wind_speed: number;
  wind_direction: number;
  precipitation: number;
  cloud_cover: number;
  uv_index: number;
  visibility: number;
  weather_code: number;
  time: string;
}

export interface WeatherForecast {
  city: string;
  country_code: string;
  timezone: string;
  current_time: string;
  data: WeatherData[];
}

// Currency Types
export interface ExchangeRate {
  currency_code: string;
  rate_to_usd: number;
  last_updated: string;
}

// Message Template Types
export interface MessageTemplate {
  id: string;
  title: string;
  description: string;
  template: string;
  fields: TemplateField[];
  category: 'flights' | 'hotels' | 'weather' | 'currency' | 'itinerary';
  icon: string;
}

export interface TemplateField {
  name: string;
  label: string;
  type: 'text' | 'date' | 'number' | 'select';
  placeholder?: string;
  options?: string[];
  required: boolean;
}

// Confirmation/Interaction Types
export interface ConfirmationData {
  id: string;
  type: 'flight' | 'hotel' | 'itinerary';
  title: string;
  data: any;
  options: ConfirmationOption[];
}

export interface ConfirmationOption {
  id: string;
  label: string;
  action: 'accept' | 'reject' | 'modify';
  primary?: boolean;
}

// User/Settings Types
export interface UserPreferences {
  theme: 'dark' | 'light';
  language: string;
  currency: string;
  notifications: boolean;
  autoConfirm: boolean;
}

export interface User {
  id: string;
  name: string;
  email: string;
  preferences: UserPreferences;
}

// API Response Types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
  status: number;
}

// Loading and UI State Types
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
}

// Chat State Types
export interface ChatState {
  conversations: Conversation[];
  currentConversationId: string | null;
  isAgentThinking: boolean;
  agentThoughts: AgentThought[];
  isLoading: boolean;
  error: string | null;
}

// App State Types
export interface AppState {
  user: User | null;
  chat: ChatState;
  ui: {
    sidebarOpen: boolean;
    currentPage: string;
  };
} 
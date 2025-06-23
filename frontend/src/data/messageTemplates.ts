import type { MessageTemplate } from '../types';

export const messageTemplates: MessageTemplate[] = [
  {
    id: 'flights-search',
    title: 'Find Flights',
    description: 'Search for flights between destinations',
    template: 'Find flights from {departure} to {destination} on {date} for {travelers} travelers',
    fields: [
      {
        name: 'departure',
        label: 'From (City or Airport Code)',
        type: 'text',
        placeholder: 'e.g., New York or JFK',
        required: true,
      },
      {
        name: 'destination',
        label: 'To (City or Airport Code)',
        type: 'text',
        placeholder: 'e.g., London or LHR',
        required: true,
      },
      {
        name: 'date',
        label: 'Departure Date',
        type: 'date',
        placeholder: 'YYYY-MM-DD',
        required: true,
      },
      {
        name: 'travelers',
        label: 'Number of Travelers',
        type: 'number',
        placeholder: '1',
        required: true,
      },
    ],
    category: 'flights',
    icon: '✈️',
  },
  {
    id: 'hotels-search',
    title: 'Find Hotels',
    description: 'Search for accommodations in a city',
    template: 'Find hotels in {city} from {checkin} to {checkout} for {guests} guests',
    fields: [
      {
        name: 'city',
        label: 'City',
        type: 'text',
        placeholder: 'e.g., Paris, Tokyo, New York',
        required: true,
      },
      {
        name: 'checkin',
        label: 'Check-in Date',
        type: 'date',
        placeholder: 'YYYY-MM-DD',
        required: true,
      },
      {
        name: 'checkout',
        label: 'Check-out Date',
        type: 'date',
        placeholder: 'YYYY-MM-DD',
        required: true,
      },
      {
        name: 'guests',
        label: 'Number of Guests',
        type: 'number',
        placeholder: '2',
        required: true,
      },
    ],
    category: 'hotels',
    icon: '🏨',
  },
  {
    id: 'weather-forecast',
    title: 'Check Weather',
    description: 'Get weather forecast for your destination',
    template: 'What\'s the weather forecast for {city}?',
    fields: [
      {
        name: 'city',
        label: 'City',
        type: 'text',
        placeholder: 'e.g., Barcelona, Sydney, Miami',
        required: true,
      },
    ],
    category: 'weather',
    icon: '🌤️',
  },
  {
    id: 'currency-exchange',
    title: 'Currency Rates',
    description: 'Check exchange rates for trip budgeting',
    template: 'What\'s the current exchange rate for {currency} to USD?',
    fields: [
      {
        name: 'currency',
        label: 'Currency Code',
        type: 'select',
        placeholder: 'Select currency',
        options: ['EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'INR', 'KRW', 'SGD'],
        required: true,
      },
    ],
    category: 'currency',
    icon: '💱',
  },
  {
    id: 'full-itinerary',
    title: 'Plan Complete Trip',
    description: 'Create a full travel itinerary with all details',
    template: 'Plan a {duration} day trip to {destination} departing {date} for {travelers} travelers with a {budget} budget',
    fields: [
      {
        name: 'destination',
        label: 'Destination',
        type: 'text',
        placeholder: 'e.g., Tokyo, Rome, Bali',
        required: true,
      },
      {
        name: 'date',
        label: 'Departure Date',
        type: 'date',
        placeholder: 'YYYY-MM-DD',
        required: true,
      },
      {
        name: 'duration',
        label: 'Trip Duration (days)',
        type: 'number',
        placeholder: '7',
        required: true,
      },
      {
        name: 'travelers',
        label: 'Number of Travelers',
        type: 'number',
        placeholder: '2',
        required: true,
      },
      {
        name: 'budget',
        label: 'Budget Range',
        type: 'select',
        placeholder: 'Select budget',
        options: ['budget-friendly', 'mid-range', 'luxury'],
        required: true,
      },
    ],
    category: 'itinerary',
    icon: '🗺️',
  },
];

// Helper function to populate template with field values
export const populateTemplate = (template: MessageTemplate, values: Record<string, string>): string => {
  let result = template.template;
  
  template.fields.forEach(field => {
    const value = values[field.name] || `{${field.name}}`;
    result = result.replace(`{${field.name}}`, value);
  });
  
  return result;
};

// Quick action templates for the welcome screen
export const quickActions = [
  {
    id: 'quick-flights',
    title: 'Find Flights',
    description: 'Search for flights to your destination',
    icon: '✈️',
    action: 'I need help finding flights',
  },
  {
    id: 'quick-hotels',
    title: 'Book Hotels',
    description: 'Find accommodations for your stay',
    icon: '🏨',
    action: 'I need help finding hotels',
  },
  {
    id: 'quick-plan',
    title: 'Plan Trip',
    description: 'Create a complete travel itinerary',
    icon: '🗺️',
    action: 'I want to plan a complete trip',
  },
  {
    id: 'quick-weather',
    title: 'Check Weather',
    description: 'Get weather forecasts for your destination',
    icon: '🌤️',
    action: 'I want to check the weather',
  },
  {
    id: 'quick-currency',
    title: 'Currency Rates',
    description: 'Check exchange rates for budgeting',
    icon: '💱',
    action: 'I need currency exchange information',
  },
];

export default messageTemplates; 
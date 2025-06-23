import { useState, useCallback, useEffect } from 'react';
import { chatApi } from '../services/api';
import type { Message, Conversation, AgentThought } from '../types';

export interface UseChatReturn {
  // State
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  isLoading: boolean;
  isAgentThinking: boolean;
  error: string | null;
  agentThoughts: AgentThought[];
  
  // Actions
  sendMessage: (content: string) => Promise<void>;
  createNewConversation: () => string;
  selectConversation: (conversationId: string) => void;
  deleteConversation: (conversationId: string) => void;
  clearError: () => void;
  retryLastMessage: () => Promise<void>;
}

export const useChat = (): UseChatReturn => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isAgentThinking, setIsAgentThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentThoughts, setAgentThoughts] = useState<AgentThought[]>([]);
  const [lastUserMessage, setLastUserMessage] = useState<string | null>(null);

  // Get current conversation
  const currentConversation = conversations.find(conv => conv.id === currentConversationId) || null;
  const messages = currentConversation?.messages || [];

  // Load conversations from localStorage on mount
  useEffect(() => {
    const savedConversations = localStorage.getItem('routerishi-conversations');
    if (savedConversations) {
      try {
        const parsed = JSON.parse(savedConversations);
        // Convert date strings back to Date objects
        const conversationsWithDates = parsed.map((conv: any) => ({
          ...conv,
          createdAt: new Date(conv.createdAt),
          updatedAt: new Date(conv.updatedAt),
          messages: conv.messages.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp),
          })),
        }));
        setConversations(conversationsWithDates);
        
        // Set the most recent conversation as current
        if (conversationsWithDates.length > 0) {
          setCurrentConversationId(conversationsWithDates[0].id);
        }
      } catch (error) {
        console.error('Failed to load conversations from localStorage:', error);
      }
    }
  }, []);

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('routerishi-conversations', JSON.stringify(conversations));
    }
  }, [conversations]);

  // Create a new conversation
  const createNewConversation = useCallback((): string => {
    const newConversation: Conversation = {
      id: `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      title: 'New Conversation',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    setConversations(prev => [newConversation, ...prev]);
    setCurrentConversationId(newConversation.id);
    setError(null);
    
    return newConversation.id;
  }, []);

  // Select a conversation
  const selectConversation = useCallback((conversationId: string) => {
    setCurrentConversationId(conversationId);
    setError(null);
  }, []);

  // Delete a conversation
  const deleteConversation = useCallback((conversationId: string) => {
    setConversations(prev => prev.filter(conv => conv.id !== conversationId));
    
    // If we're deleting the current conversation, select another one or create new
    if (conversationId === currentConversationId) {
      const remaining = conversations.filter(conv => conv.id !== conversationId);
      if (remaining.length > 0) {
        setCurrentConversationId(remaining[0].id);
      } else {
        setCurrentConversationId(null);
      }
    }
  }, [conversations, currentConversationId]);

  // Add a message to the current conversation
  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
    };

    setConversations(prev => prev.map(conv => {
      if (conv.id === message.conversationId) {
        const updatedConversation = {
          ...conv,
          messages: [...conv.messages, newMessage],
          updatedAt: new Date(),
        };
        
        // Update title if it's the first user message
        if (conv.messages.length === 0 && message.type === 'user') {
          updatedConversation.title = message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '');
        }
        
        return updatedConversation;
      }
      return conv;
    }));

    return newMessage;
  }, []);

  // Simulate agent thinking process
  const simulateAgentThinking = useCallback(async (userMessage: string) => {
    setIsAgentThinking(true);
    setAgentThoughts([]);

    // Simulate different thinking steps based on message content
    const lowerMessage = userMessage.toLowerCase();
    const thoughts: AgentThought[] = [];

    // Simulate getting current date
    thoughts.push({
      id: `thought_${Date.now()}_1`,
      action: 'get_current_date',
      input: {},
      output: `Today is ${new Date().toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })}`,
      timestamp: new Date(),
    });

    // Add thought for each step
    for (let i = 0; i < thoughts.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 1200));
      setAgentThoughts(prev => [...prev, thoughts[i]]);
    }

    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 500));
    setIsAgentThinking(false);
  }, []);

  // Send a message
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;
    
    setIsLoading(true);
    setError(null);
    setLastUserMessage(content);

    try {
      // Create conversation if none exists
      let conversationId = currentConversationId;
      if (!conversationId) {
        conversationId = createNewConversation();
      }

      // Add user message
      const userMessage = addMessage({
        content: content.trim(),
        type: 'user',
        conversationId,
      });

      // Simulate agent thinking
      await simulateAgentThinking(content);

      // Get AI response (using mock for now)
      const aiResponse = await chatApi.sendMessageMock(content, conversationId);

      // Add AI response
      addMessage({
        content: aiResponse,
        type: 'ai',
        conversationId,
      });

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      console.error('Send message error:', err);
    } finally {
      setIsLoading(false);
      setAgentThoughts([]);
    }
  }, [currentConversationId, createNewConversation, addMessage, simulateAgentThinking]);

  // Retry the last message
  const retryLastMessage = useCallback(async () => {
    if (lastUserMessage) {
      await sendMessage(lastUserMessage);
    }
  }, [lastUserMessage, sendMessage]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // State
    conversations,
    currentConversation,
    messages,
    isLoading,
    isAgentThinking,
    error,
    agentThoughts,
    
    // Actions
    sendMessage,
    createNewConversation,
    selectConversation,
    deleteConversation,
    clearError,
    retryLastMessage,
  };
}; 
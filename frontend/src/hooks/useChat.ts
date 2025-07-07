import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { conversationApi, chatApi, API_BASE_URL } from '../services/api';
import { authService } from '../services/authService';
import type { ConversationMetadata, Message, AgentThought } from '../types';

export interface UseChatReturn {
  // State
  conversations: ConversationMetadata[];
  currentConversation: ConversationMetadata | null;
  messages: Message[];
  isLoading: boolean;
  isAgentThinking: boolean;
  error: string | null;
  agentThoughts: AgentThought[];
  
  // Actions
  sendMessage: (content: string, withReasoning?: boolean) => Promise<void>;
  createNewConversation: () => string;
  selectConversation: (conversationId: string) => void;
  deleteConversation: (conversationId: string) => void;
  clearError: () => void;
  retryLastMessage: () => Promise<void>;
}

interface LocalConversation extends ConversationMetadata {
  messages: Message[];
}

export const useChat = (): UseChatReturn => {
  const { user, isGuest } = useAuth();
  const [conversations, setConversations] = useState<ConversationMetadata[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isAgentThinking, setIsAgentThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentThoughts, setAgentThoughts] = useState<AgentThought[]>([]);
  const [lastUserMessage, setLastUserMessage] = useState<string | null>(null);
  const [eventSource, setEventSource] = useState<EventSource | null>(null);

  // Get current conversation
  const currentConversation = conversations.find(conv => conv.id === currentConversationId) || null;

  // Stable user ID reference to prevent unnecessary re-renders
  const userId = user?.id;
  
  // Generate user-specific localStorage key
  const getStorageKey = useCallback(() => {
    if (isGuest) {
      return 'routerishi-guest-conversations';
    }
    return userId ? `routerishi-conversations-${userId}` : 'routerishi-conversations';
  }, [userId, isGuest]);

  // Set up Server-Sent Events for real-time updates
  useEffect(() => {
    if (!currentConversationId) return;

    // Close existing EventSource
    if (eventSource) {
      eventSource.close();
    }

    // Create new EventSource for this conversation
    const newEventSource = new EventSource(
      `${API_BASE_URL}/api/v1/chat/stream/${currentConversationId}`
    );

    newEventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'new_message') {
          const newMessage: Message = {
            id: data.message.id,
            role: data.message.role,
            content: data.message.content,
            timestamp: new Date(data.message.timestamp),
            conversation_id: data.message.conversation_id,
            tool_calls: data.message.tool_calls,
            execution_time_ms: data.message.execution_time_ms,
          };

          setMessages(prevMessages => {
            // Avoid duplicates
            if (prevMessages.some(msg => msg.id === newMessage.id)) {
              return prevMessages;
            }
            return [...prevMessages, newMessage];
          });

          // Update conversation in sidebar
          setConversations(prevConversations => 
            prevConversations.map(conv => 
              conv.id === currentConversationId 
                ? { ...conv, updated_at: new Date().toISOString(), message_count: conv.message_count + 1 }
                : conv
            )
          );

          // Stop loading state when AI responds
          if (newMessage.role === 'assistant') {
            setIsLoading(false);
            setIsAgentThinking(false);
            setAgentThoughts([]);
          }
        }
      } catch (error) {
        console.error('Error parsing SSE message:', error);
      }
    };

    newEventSource.onerror = (error) => {
      console.error('SSE error:', error);
      newEventSource.close();
    };

    setEventSource(newEventSource);

    // Cleanup on unmount or conversation change
    return () => {
      newEventSource.close();
    };
  }, [currentConversationId]);

  // Load conversations when user or auth state changes
  useEffect(() => {
    const loadConversations = async () => {
      try {
        if (isGuest) {
          // For guests, load from localStorage
          const storageKey = getStorageKey();
          const savedConversations = localStorage.getItem(storageKey);
          if (savedConversations) {
            const parsed: LocalConversation[] = JSON.parse(savedConversations);
            // Convert to metadata format
            const conversationMetadata: ConversationMetadata[] = parsed.map(conv => ({
              id: conv.id,
              title: conv.title,
              created_at: conv.created_at,
              updated_at: conv.updated_at,
              user_id: conv.user_id,
              message_count: conv.messages.length,
              is_guest: true,
            }));
            setConversations(conversationMetadata);
            
            // Set the most recent conversation as current
            if (conversationMetadata.length > 0) {
              setCurrentConversationId(conversationMetadata[0].id);
              // Load messages for the current conversation
              const currentConv = parsed.find(c => c.id === conversationMetadata[0].id);
              if (currentConv) {
                setMessages(currentConv.messages);
              }
            } else {
              // No conversations yet
              setCurrentConversationId(null);
              setMessages([]);
            }
          } else {
            // No saved conversations
            setConversations([]);
            setCurrentConversationId(null);
            setMessages([]);
          }
        } else if (userId) {
          // For authenticated users, fetch from backend
          const token = authService.getStoredToken();
          if (token) {
            const userConversations = await conversationApi.getUserConversations(token);
            setConversations(userConversations);
            
            // Set the most recent conversation as current and load its messages
            if (userConversations.length > 0) {
              const latestConv = userConversations[0];
              setCurrentConversationId(latestConv.id);
              const conversationMessages = await conversationApi.getConversationMessages(token, latestConv.id);
              setMessages(conversationMessages);
            } else {
              // No conversations yet, clear current state
              setCurrentConversationId(null);
              setMessages([]);
            }
          }
        } else {
          // User not loaded yet, clear state
          setConversations([]);
          setCurrentConversationId(null);
          setMessages([]);
        }
      } catch (error) {
        console.error('Failed to load conversations:', error);
        setError('Failed to load conversations');
        // Set fallback state on error
        setConversations([]);
        setCurrentConversationId(null);
        setMessages([]);
      }
    };

    loadConversations();
  }, [userId, isGuest]); // Removed getStorageKey from dependencies to prevent loop

  // Clear conversations when user logs out
  useEffect(() => {
    if (!userId && !isGuest) {
      setConversations([]);
      setCurrentConversationId(null);
      setMessages([]);
    }
  }, [userId, isGuest]);

  // Save guest conversations to localStorage
  const saveGuestConversations = useCallback((updatedConversations: ConversationMetadata[], updatedMessages: Message[]) => {
    if (isGuest) {
      const storageKey = getStorageKey();
      // Convert back to local conversation format with messages
      const localConversations: LocalConversation[] = updatedConversations.map(conv => {
        const convMessages = conv.id === currentConversationId ? updatedMessages : [];
        return {
          ...conv,
          messages: convMessages,
        };
      });
      localStorage.setItem(storageKey, JSON.stringify(localConversations));
    }
  }, [isGuest, getStorageKey, currentConversationId]);

  // Create a new conversation
  const createNewConversation = useCallback((): string => {
    const conversationId = `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    if (isGuest) {
      // For guests, create the conversation locally
      const newConversation: ConversationMetadata = {
        id: conversationId,
        title: 'New Conversation',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        user_id: userId,
        message_count: 0,
        is_guest: true,
      };

      const updatedConversations = [newConversation, ...conversations];
      setConversations(updatedConversations);
      setCurrentConversationId(conversationId);
      setMessages([]);
      setError(null);
      
      // Save for guests
      saveGuestConversations(updatedConversations, []);
    } else {
      // For authenticated users, we'll let the backend create it when first message is sent
      // But we'll create a placeholder conversation in the UI to show it immediately
      const newConversation: ConversationMetadata = {
        id: conversationId,
        title: 'New Conversation',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        user_id: userId,
        message_count: 0,
        is_guest: false,
      };

      const updatedConversations = [newConversation, ...conversations];
      setConversations(updatedConversations);
      setCurrentConversationId(conversationId);
      setMessages([]);
      setError(null);
    }
    
    return conversationId;
  }, [conversations, userId, isGuest, saveGuestConversations]);

  // Select a conversation
  const selectConversation = useCallback(async (conversationId: string) => {
    setCurrentConversationId(conversationId);
    setError(null);
    
    try {
      if (isGuest) {
        // Load from localStorage
        const storageKey = getStorageKey();
        const savedConversations = localStorage.getItem(storageKey);
        if (savedConversations) {
          const parsed: LocalConversation[] = JSON.parse(savedConversations);
          const conversation = parsed.find(c => c.id === conversationId);
          if (conversation) {
            setMessages(conversation.messages);
          }
        }
      } else if (userId) {
        // Load from backend
        const token = authService.getStoredToken();
        if (token) {
          const conversationMessages = await conversationApi.getConversationMessages(token, conversationId);
          setMessages(conversationMessages);
        }
      }
    } catch (error) {
      console.error('Failed to load conversation messages:', error);
      setError('Failed to load conversation');
    }
  }, [userId, isGuest]);

  // Delete a conversation
  const deleteConversation = useCallback(async (conversationId: string) => {
    try {
      if (!isGuest && userId) {
        // Delete from backend
        const token = authService.getStoredToken();
        if (token) {
          await conversationApi.deleteConversation(token, conversationId);
        }
      }
      
      // Update local state
      const updatedConversations = conversations.filter(conv => conv.id !== conversationId);
      setConversations(updatedConversations);
      
      // If we're deleting the current conversation, select another one or clear
      if (conversationId === currentConversationId) {
        if (updatedConversations.length > 0) {
          await selectConversation(updatedConversations[0].id);
        } else {
          setCurrentConversationId(null);
          setMessages([]);
        }
      }
      
      // Save for guests
      saveGuestConversations(updatedConversations, messages);
      
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      setError('Failed to delete conversation');
    }
  }, [conversations, currentConversationId, userId, isGuest, selectConversation, saveGuestConversations, messages]);

  // Add a message to the current conversation
  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
    };

    const updatedMessages = [...messages, newMessage];
    setMessages(updatedMessages);

    // Update conversation metadata
    const updatedConversations = conversations.map(conv => {
      if (conv.id === message.conversation_id) {
        const updatedConv = {
          ...conv,
          message_count: conv.message_count + 1,
          updated_at: new Date().toISOString(),
        };
        
        // Update title if it's the first user message
        if (conv.message_count === 0 && message.role === 'user') {
          updatedConv.title = message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '');
        }
        
        return updatedConv;
      }
      return conv;
    });
    
    setConversations(updatedConversations);
    
    // Save for guests
    saveGuestConversations(updatedConversations, updatedMessages);

    return newMessage;
  }, [messages, conversations, saveGuestConversations]);

  // Send a message with optional reasoning
  const sendMessage = useCallback(async (content: string, withReasoning: boolean = false) => {
    if (!content.trim()) return;
    
    setIsLoading(true);
    setError(null);
    setLastUserMessage(content);
    setIsAgentThinking(true);

    try {
      // Create conversation if none exists
      let conversationId = currentConversationId;
      if (!conversationId) {
        conversationId = createNewConversation();
      }

      if (isGuest) {
        // For guests, manage local state
        const userMessage = addMessage({
          content: content.trim(),
          role: 'user',
          conversation_id: conversationId,
        });

        if (withReasoning) {
          const { response, toolCalls, executionTimeMs } = await chatApi.sendMessageWithReasoning(content, conversationId);
          addMessage({
            content: response,
            role: 'assistant',
            conversation_id: conversationId,
            tool_calls: toolCalls,
            execution_time_ms: executionTimeMs,
          });
        } else {
          const aiResponse = await chatApi.sendMessage(content, conversationId);
          addMessage({
            content: aiResponse,
            role: 'assistant',
            conversation_id: conversationId,
          });
        }
        setIsLoading(false);
        setIsAgentThinking(false);
      } else if (userId) {
        // For authenticated users, just send to backend
        // Real-time updates will come via SSE
        const token = authService.getStoredToken();
        
        if (withReasoning) {
          await chatApi.sendMessageWithReasoning(content, conversationId, token || undefined);
        } else {
          await chatApi.sendMessage(content, conversationId, token || undefined);
        }

        // Set current conversation ID if it was new
        setCurrentConversationId(conversationId);
        
        // Loading state will be cleared when SSE receives the AI response
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      console.error('Send message error:', err);
      setIsLoading(false);
      setIsAgentThinking(false);
    } finally {
      setAgentThoughts([]);
    }
  }, [currentConversationId, createNewConversation, addMessage, isGuest, userId]);

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
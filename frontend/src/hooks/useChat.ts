import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { conversationApi, chatApi, API_BASE_URL } from '../services/api';
import { authService } from '../services/authService';
import type { ConversationMetadata, Message, AgentThought } from '../types';

// Add draft conversation type
interface DraftConversation {
  id: string;
  isDraft: true;
  created_at: string;
  title: string;  // Add title for consistency
  message_count: number;  // Add message_count for consistency
  updated_at: string;  // Add updated_at for consistency
  is_guest: boolean;  // Add is_guest for type compatibility
}

// Helper type guard
function isDraft(conversation: DraftConversation | ConversationMetadata): conversation is DraftConversation {
  return 'isDraft' in conversation;
}

export interface UseChatReturn {
  // State
  conversations: (ConversationMetadata | DraftConversation)[];
  currentConversation: (ConversationMetadata | DraftConversation | null);
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
  const [conversations, setConversations] = useState<(ConversationMetadata | DraftConversation)[]>([]);
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

  // Set up Server-Sent Events for real-time updates (authenticated users only)
  useEffect(() => {
    if (!currentConversationId || isGuest) return;

    // Close existing EventSource
    if (eventSource) {
      eventSource.close();
    }

    // Create new EventSource for this conversation (authenticated users only)
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

          // Only add non-user messages from SSE
          if (newMessage.role !== 'user') {
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
  }, [currentConversationId, isGuest]);

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



  // Create a new conversation
  const createNewConversation = useCallback((): string => {
    const conversationId = `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Create a draft conversation
    const draftConversation: DraftConversation = {
      id: conversationId,
      isDraft: true,
      created_at: new Date().toISOString(),
      title: 'New Chat',
      message_count: 0,
      updated_at: new Date().toISOString(),
      is_guest: isGuest,
    };

    setConversations(prev => [draftConversation, ...prev]);
    setCurrentConversationId(conversationId);
    setMessages([]);
    setError(null);
    
    return conversationId;
  }, [isGuest]);

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
      const conv = conversations.find(c => c.id === conversationId);
      
      // If it's a draft, just remove it from state
      if (conv && isDraft(conv)) {
        setConversations(prev => prev.filter(c => c.id !== conversationId));
        if (conversationId === currentConversationId) {
          setCurrentConversationId(null);
          setMessages([]);
        }
        return;
      }

      // Rest of existing delete logic...
      if (!isGuest && userId) {
        const token = authService.getStoredToken();
        if (token) {
          await conversationApi.deleteConversation(token, conversationId);
        }
      }
      
      const updatedConversations = conversations.filter(conv => conv.id !== conversationId);
      setConversations(updatedConversations);
      
      if (conversationId === currentConversationId) {
        if (updatedConversations.length > 0) {
          await selectConversation(updatedConversations[0].id);
        } else {
          setCurrentConversationId(null);
          setMessages([]);
        }
      }
      
      // For guests, localStorage is updated automatically in the addMessage function
      
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      setError('Failed to delete conversation');
    }
  }, [conversations, currentConversationId, userId, isGuest, selectConversation]);

  // Add a message to the current conversation
  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    // Only add AI messages through this function
    if (message.role === 'user') {
      return null;
    }

    const newMessage: Message = {
      ...message,
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
    };

    // Use functional update to get the latest messages state
    setMessages(prev => {
      const updatedMessages = [...prev, newMessage];
      
      // Update conversation metadata
      setConversations(prevConversations => {
        const updatedConversations = prevConversations.map(conv => {
          if (conv.id === message.conversation_id) {
            return {
              ...conv,
              message_count: conv.message_count + 1,
              updated_at: new Date().toISOString(),
            };
          }
          return conv;
        });
        
        // Save for guests with the updated messages
        if (isGuest) {
          const storageKey = getStorageKey();
          const localConversations: LocalConversation[] = updatedConversations
            .filter(conv => !isDraft(conv))
            .map(conv => ({
              ...conv as ConversationMetadata,
              messages: conv.id === message.conversation_id ? updatedMessages : 
                       conv.id === currentConversationId ? prev : []
            }));
          localStorage.setItem(storageKey, JSON.stringify(localConversations));
        }
        
        return updatedConversations;
      });
      
      return updatedMessages;
    });

    return newMessage;
  }, [isGuest, getStorageKey, currentConversationId]);

  // Send a message with optional reasoning
  const sendMessage = useCallback(async (content: string, withReasoning: boolean = false) => {
    if (!content.trim()) return;
    
    setIsLoading(true);
    setError(null);
    setLastUserMessage(content);
    setIsAgentThinking(true);

    let conversationId = currentConversationId;

    try {
      // Create conversation if none exists
      if (!conversationId) {
        conversationId = createNewConversation();
      }

      // Optimistically add user message to UI
      const userMessage: Message = {
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        content: content.trim(),
        role: 'user',
        conversation_id: conversationId,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, userMessage]);

      // Convert draft to real conversation if this is the first message
      const currentConv = conversations.find(conv => conv.id === conversationId);
      if (currentConv && isDraft(currentConv)) {
        const newConversation: ConversationMetadata = {
          id: conversationId,
          title: content.slice(0, 50) + (content.length > 50 ? '...' : ''),
          created_at: currentConv.created_at,
          updated_at: new Date().toISOString(),
          user_id: userId,
          message_count: 1,
          is_guest: isGuest,
        };

        setConversations(prev => [
          newConversation,
          ...prev.filter(conv => conv.id !== conversationId)
        ]);
      } else if (currentConv && !isDraft(currentConv)) {
        // Update existing conversation
        setConversations(prevConversations => 
          prevConversations.map(conv => 
            conv.id === conversationId && !isDraft(conv)
              ? {
                  ...conv,
                  message_count: conv.message_count + 1,
                  updated_at: new Date().toISOString(),
                }
              : conv
          )
        );
      }

      if (isGuest) {
        // For guests: handle API response directly, no SSE
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
        // For authenticated users: use SSE for real-time updates
        const token = authService.getStoredToken();
        
        if (withReasoning) {
          await chatApi.sendMessageWithReasoning(content, conversationId, token || undefined);
        } else {
          await chatApi.sendMessage(content, conversationId, token || undefined);
        }

        setCurrentConversationId(conversationId);
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      console.error('Send message error:', err);
      setIsLoading(false);
      setIsAgentThinking(false);
      
      // If this was a draft conversation, remove it on error
      const currentConv = conversations.find(conv => conv.id === conversationId);
      if (currentConv && isDraft(currentConv)) {
        setConversations(prev => prev.filter(conv => conv.id !== conversationId));
      } else {
        // Otherwise rollback the message count
        setConversations(prev => 
          prev.map(conv => 
            conv.id === conversationId && !isDraft(conv)
              ? {
                  ...conv,
                  message_count: Math.max(0, conv.message_count - 1),
                }
              : conv
          )
        );
      }
      
      // Remove the optimistically added user message on error
      setMessages(prev => prev.filter(msg => msg.content !== content.trim()));
    } finally {
      setAgentThoughts([]);
    }
  }, [currentConversationId, createNewConversation, addMessage, isGuest, userId, conversations]);

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
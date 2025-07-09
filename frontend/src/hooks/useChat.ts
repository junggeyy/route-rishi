import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { conversationApi, chatApi, API_BASE_URL } from '../services/api';
import { authService } from '../services/authService';
import type { ConversationMetadata, Message, AgentThought } from '../types';

interface DraftConversation {
  id: string;
  isDraft: true;
  created_at: string;
  title: string;
  message_count: number;
  updated_at: string;
  is_guest: boolean;
}

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

  const currentConversation = conversations.find(conv => conv.id === currentConversationId) || null;

  const userId = user?.id;
  
  const getStorageKey = useCallback(() => {
    if (isGuest) {
      return 'routerishi-guest-conversations';
    }
    return userId ? `routerishi-conversations-${userId}` : 'routerishi-conversations';
  }, [userId, isGuest]);

  useEffect(() => {
    if (!currentConversationId || isGuest) return;

    if (eventSource) {
      eventSource.close();
    }

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

          if (newMessage.role !== 'user') {
            setMessages(prevMessages => {
              if (prevMessages.some(msg => msg.id === newMessage.id)) {
                return prevMessages;
              }
              return [...prevMessages, newMessage];
            });

            setConversations(prevConversations => 
              prevConversations.map(conv => 
                conv.id === currentConversationId 
                  ? { ...conv, updated_at: new Date().toISOString(), message_count: conv.message_count + 1 }
                  : conv
              )
            );

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

    return () => {
      newEventSource.close();
    };
  }, [currentConversationId, isGuest]);

  useEffect(() => {
    const loadConversations = async () => {
      try {
        if (isGuest) {
          const storageKey = getStorageKey();
          const savedConversations = localStorage.getItem(storageKey);
          if (savedConversations) {
            const parsed: LocalConversation[] = JSON.parse(savedConversations);
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
            
            if (conversationMetadata.length > 0) {
              setCurrentConversationId(conversationMetadata[0].id);
              const currentConv = parsed.find(c => c.id === conversationMetadata[0].id);
              if (currentConv) {
                setMessages(currentConv.messages);
              }
            } else {
              setCurrentConversationId(null);
              setMessages([]);
            }
          } else {
            setConversations([]);
            setCurrentConversationId(null);
            setMessages([]);
          }
        } else if (userId) {
          const token = authService.getStoredToken();
          if (token) {
            const userConversations = await conversationApi.getUserConversations(token);
            setConversations(userConversations);
            
            if (userConversations.length > 0) {
              const latestConv = userConversations[0];
              setCurrentConversationId(latestConv.id);
              const conversationMessages = await conversationApi.getConversationMessages(token, latestConv.id);
              setMessages(conversationMessages);
            } else {
              setCurrentConversationId(null);
              setMessages([]);
            }
          }
        }
      } catch (error) {
        console.error('Error loading conversations:', error);
        setConversations([]);
        setCurrentConversationId(null);
        setMessages([]);
      }
    };

    loadConversations();
  }, [userId, isGuest]);

  useEffect(() => {
    if (!userId && !isGuest) {
      setConversations([]);
      setCurrentConversationId(null);
      setMessages([]);
    }
  }, [userId, isGuest]);



  const createNewConversation = useCallback(() => {
    const newConversationId = `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const draftConversation: DraftConversation = {
      id: newConversationId,
      isDraft: true,
      created_at: new Date().toISOString(),
      title: 'New Chat',
      message_count: 0,
      updated_at: new Date().toISOString(),
      is_guest: isGuest,
    };

    setConversations(prev => [draftConversation, ...prev]);
    setCurrentConversationId(newConversationId);
    setMessages([]);
    setError(null);
    
    return newConversationId;
  }, [isGuest]);

  const selectConversation = useCallback(async (conversationId: string) => {
    setCurrentConversationId(conversationId);
    setError(null);
    
    try {
      if (isGuest) {
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

  const deleteConversation = useCallback(async (conversationId: string) => {
    try {
      const conv = conversations.find(c => c.id === conversationId);
      
      if (conv && isDraft(conv)) {
        setConversations(prev => prev.filter(c => c.id !== conversationId));
        if (conversationId === currentConversationId) {
          setCurrentConversationId(null);
          setMessages([]);
        }
        return;
      }

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
      
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      setError('Failed to delete conversation');
    }
  }, [conversations, currentConversationId, userId, isGuest, selectConversation]);

  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    if (message.role === 'user') {
      return null;
    }

    const newMessage: Message = {
      ...message,
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
    };

    setMessages(prev => {
      const updatedMessages = [...prev, newMessage];
      
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

  const sendMessage = useCallback(async (content: string, withReasoning: boolean = false) => {
    if (!content.trim()) return;
    
    setIsLoading(true);
    setError(null);
    setLastUserMessage(content);
    setIsAgentThinking(true);

    let conversationId = currentConversationId;

    try {
      if (!conversationId) {
        conversationId = createNewConversation();
      }

      const userMessage: Message = {
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        content: content.trim(),
        role: 'user',
        conversation_id: conversationId,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, userMessage]);

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
      
      const currentConv = conversations.find(conv => conv.id === conversationId);
      if (currentConv && isDraft(currentConv)) {
        setConversations(prev => prev.filter(conv => conv.id !== conversationId));
      } else {
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
      
      setMessages(prev => prev.filter(msg => msg.content !== content.trim()));
    } finally {
      setAgentThoughts([]);
    }
  }, [currentConversationId, createNewConversation, addMessage, isGuest, userId, conversations]);

  const retryLastMessage = useCallback(async () => {
    if (lastUserMessage) {
      await sendMessage(lastUserMessage);
    }
  }, [lastUserMessage, sendMessage]);

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
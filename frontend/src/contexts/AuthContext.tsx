import React, { createContext, useContext, useEffect, useState } from 'react';
import type { AuthContextType, User, AuthState } from '../types/auth';
import { authService } from '../services/authService';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    isGuest: false,
  });
  const [error, setError] = useState<string | null>(null);

  // Initialize auth state on mount
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }));

      // Check for guest user first
      const guestUser = authService.getGuestUser();
      if (guestUser) {
        setAuthState({
          user: guestUser,
          isAuthenticated: true,
          isLoading: false,
          isGuest: true,
        });
        return;
      }

      // Check for authenticated user
      const storedUser = authService.getStoredUser();
      const token = authService.getStoredToken();

      if (storedUser && token) {
        // Verify the token is still valid
        const currentUser = await authService.getCurrentUser();
        if (currentUser) {
          setAuthState({
            user: currentUser,
            isAuthenticated: true,
            isLoading: false,
            isGuest: false,
          });
        } else {
          // Token is invalid, clear storage
          authService.clearLocalStorage();
          setAuthState({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            isGuest: false,
          });
        }
      } else {
        setAuthState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          isGuest: false,
        });
      }
    } catch (error: any) {
      console.error('Auth initialization error:', error);
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        isGuest: false,
      });
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setError(null);
      setAuthState(prev => ({ ...prev, isLoading: true }));

      const authResponse = await authService.login({ email, password });
      authService.saveAuthData(authResponse);

      setAuthState({
        user: authResponse.user,
        isAuthenticated: true,
        isLoading: false,
        isGuest: false,
      });
    } catch (error: any) {
      setError(error.message);
      setAuthState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const signup = async (fullName: string, email: string, password: string) => {
    try {
      setError(null);
      setAuthState(prev => ({ ...prev, isLoading: true }));

      const authResponse = await authService.signup({ fullName, email, password });
      authService.saveAuthData(authResponse);

      setAuthState({
        user: authResponse.user,
        isAuthenticated: true,
        isLoading: false,
        isGuest: false,
      });
    } catch (error: any) {
      setError(error.message);
      setAuthState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const loginWithGoogle = async () => {
    try {
      setError(null);
      setAuthState(prev => ({ ...prev, isLoading: true }));
      await authService.loginWithGoogle();
      // Note: This will redirect, so the loading state will persist until redirect completes
    } catch (error: any) {
      setError(error.message);
      setAuthState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const signupWithGoogle = async () => {
    try {
      setError(null);
      setAuthState(prev => ({ ...prev, isLoading: true }));
      await authService.signupWithGoogle();
      // Note: This will redirect, so the loading state will persist until redirect completes
    } catch (error: any) {
      setError(error.message);
      setAuthState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const loginAsGuest = () => {
    try {
      setError(null);
      
      // Clear any existing auth data
      authService.clearLocalStorage();
      
      const guestUser = authService.createGuestUser();
      setAuthState({
        user: guestUser,
        isAuthenticated: true,
        isLoading: false,
        isGuest: true,
      });
    } catch (error: any) {
      setError(error.message);
    }
  };

  const logout = async () => {
    try {
      setError(null);
      setAuthState(prev => ({ ...prev, isLoading: true }));

      await authService.logout();

      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        isGuest: false,
      });
    } catch (error: any) {
      // Even if logout fails, clear the local state
      setError(error.message);
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        isGuest: false,
      });
    }
  };

  const clearError = () => {
    setError(null);
  };

  const value: AuthContextType = {
    ...authState,
    login,
    signup,
    loginWithGoogle,
    signupWithGoogle,
    loginAsGuest,
    logout,
    clearError,
    error,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 
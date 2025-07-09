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

      const urlParams = new URLSearchParams(window.location.search);
      const isOAuthReturn = urlParams.get('oauth') === 'success';

      if (isOAuthReturn) {
        console.log('OAuth completion detected, processing URL parameters...');
        
        const tokenB64 = urlParams.get('token');
        const refreshTokenB64 = urlParams.get('refresh_token');
        const userDataB64 = urlParams.get('user_data');
        
        console.log('URL parameters:', { tokenB64, refreshTokenB64, userDataB64 });
        
        if (tokenB64 && refreshTokenB64 && userDataB64) {
          try {
            const token = atob(tokenB64);
            const refreshToken = atob(refreshTokenB64);
            const userDataJson = atob(userDataB64);
            const userData = JSON.parse(userDataJson);
            
            console.log('Decoded auth data:', { token, refreshToken, userData });
            
            localStorage.setItem('authToken', token);
            localStorage.setItem('refreshToken', refreshToken);
            localStorage.setItem('user', userDataJson);
            
            console.log('Auth data saved to localStorage successfully');
            
            window.history.replaceState({}, document.title, window.location.pathname);
            
            setAuthState({
              user: userData,
              isAuthenticated: true,
              isLoading: false,
              isGuest: false,
            });
            
            console.log('User set as authenticated via OAuth');
            return;
            
          } catch (error) {
            console.error('Error processing OAuth data from URL:', error);
          }
        } else {
          console.error('Missing OAuth data in URL parameters');
        }
        
        window.history.replaceState({}, document.title, window.location.pathname);
      }

      const oauthCompleted = localStorage.getItem('oauth_completed');
      if (oauthCompleted) {
        localStorage.removeItem('oauth_completed');
        console.log('Legacy OAuth completion detected');
        
        const token = authService.getStoredToken();
        const storedUser = authService.getStoredUser();
        
        if (token && storedUser) {
          setAuthState({
            user: storedUser,
            isAuthenticated: true,
            isLoading: false,
            isGuest: false,
          });
          return;
        }
      }

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

      const storedUser = authService.getStoredUser();
      const token = authService.getStoredToken();

      if (storedUser && token) {
        setAuthState({
          user: storedUser,
          isAuthenticated: true,
          isLoading: false,
          isGuest: false,
        });
        
        try {
          const currentUser = await authService.getCurrentUser();
          if (currentUser) {
            setAuthState({
              user: currentUser,
              isAuthenticated: true,
              isLoading: false,
              isGuest: false,
            });
          } else {
            authService.clearLocalStorage();
            setAuthState({
              user: null,
              isAuthenticated: false,
              isLoading: false,
              isGuest: false,
            });
          }
        } catch (error) {
          console.warn('Token verification failed, keeping user logged in locally:', error);
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
      localStorage.removeItem('oauth_completed');
      
      setAuthState(prev => ({ ...prev, isLoading: true }));
      
      await authService.loginWithGoogle();
      
    } catch (error: any) {
      console.error('Google login error:', error);
      setError(error.message);
      setAuthState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const signupWithGoogle = async () => {
    try {
      setError(null);
      localStorage.removeItem('oauth_completed');
      
      setAuthState(prev => ({ ...prev, isLoading: true }));
      
      await authService.signupWithGoogle();
      
    } catch (error: any) {
      console.error('Google signup error:', error);
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

      // Clear any OAuth parameters from URL that might be lingering
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.has('oauth') || urlParams.has('token') || urlParams.has('refresh_token') || urlParams.has('user_data')) {
        window.history.replaceState({}, document.title, window.location.pathname);
      }

      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        isGuest: false,
      });
    } catch (error: any) {
      // Even if logout fails, clear the local state and URL params
      setError(error.message);
      
      // Clear URL parameters
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.has('oauth') || urlParams.has('token') || urlParams.has('refresh_token') || urlParams.has('user_data')) {
        window.history.replaceState({}, document.title, window.location.pathname);
      }
      
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
import axios from 'axios';
import type { User } from '../types/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  fullName: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  token: string;
  refreshToken: string;
}

class AuthService {
  private baseURL: string;

  constructor() {
    this.baseURL = `${API_BASE_URL}/api/v1/auth`;
  }

  async login(loginData: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await axios.post(`${this.baseURL}/login`, loginData);
      return response.data;
    } catch (error: any) {
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error(error.response?.data?.message || 'Login failed');
    }
  }

  async signup(signupData: SignupRequest): Promise<AuthResponse> {
    try {
      const response = await axios.post(`${this.baseURL}/signup`, signupData);
      return response.data;
    } catch (error: any) {
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error(error.response?.data?.message || 'Signup failed');
    }
  }

  async loginWithGoogle(): Promise<AuthResponse> {
    try {
      // For now, we'll redirect to Google OAuth endpoint
      // In a real implementation, this would handle the Google OAuth flow
      window.location.href = `${this.baseURL}/google/login`;
      return Promise.reject(new Error('Redirecting to Google...'));
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Google login failed');
    }
  }

  async signupWithGoogle(): Promise<AuthResponse> {
    try {
      // For now, we'll redirect to Google OAuth endpoint
      window.location.href = `${this.baseURL}/google/signup`;
      return Promise.reject(new Error('Redirecting to Google...'));
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Google signup failed');
    }
  }

  async logout(): Promise<void> {
    try {
      const token = localStorage.getItem('authToken');
      if (token) {
        await axios.post(`${this.baseURL}/logout`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
    } catch (error) {
      // Even if logout fails on the server, we'll clear local storage
      console.warn('Logout request failed:', error);
    } finally {
      this.clearLocalStorage();
    }
  }

  async refreshToken(): Promise<AuthResponse> {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await axios.post(`${this.baseURL}/refresh`, {
        refreshToken
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Token refresh failed');
    }
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        return null;
      }

      const response = await axios.get(`${this.baseURL}/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    } catch (error) {
      // If getting current user fails, clear invalid token
      this.clearLocalStorage();
      return null;
    }
  }

  saveAuthData(authResponse: AuthResponse): void {
    localStorage.setItem('authToken', authResponse.token);
    localStorage.setItem('refreshToken', authResponse.refreshToken);
    localStorage.setItem('user', JSON.stringify(authResponse.user));
  }

  getStoredUser(): User | null {
    try {
      const userJson = localStorage.getItem('user');
      return userJson ? JSON.parse(userJson) : null;
    } catch (error) {
      return null;
    }
  }

  getStoredToken(): string | null {
    return localStorage.getItem('authToken');
  }

  clearLocalStorage(): void {
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    localStorage.removeItem('guestUser');
  }

  createGuestUser(): User {
    const guestUser: User = {
      id: 'guest-' + Date.now(),
      email: 'guest@routerishi.com',
      fullName: 'Guest User',
      provider: 'guest',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    localStorage.setItem('guestUser', JSON.stringify(guestUser));
    return guestUser;
  }

  getGuestUser(): User | null {
    try {
      const guestUserJson = localStorage.getItem('guestUser');
      return guestUserJson ? JSON.parse(guestUserJson) : null;
    } catch (error) {
      return null;
    }
  }

  isGuest(): boolean {
    return !!localStorage.getItem('guestUser');
  }
}

export const authService = new AuthService(); 
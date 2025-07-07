import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Loader2 } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requireAuth = true 
}) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  // Debug OAuth returns
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const isOAuthReturn = urlParams.get('oauth') === 'success';
    
    if (isOAuthReturn) {
      console.log('ProtectedRoute: OAuth return detected');
      console.log('ProtectedRoute state:', { isAuthenticated, isLoading, user });
      console.log('RequireAuth:', requireAuth);
    }
  }, [location, isAuthenticated, isLoading, user, requireAuth]);

  // For OAuth returns, give extra time for authentication to complete
  const urlParams = new URLSearchParams(location.search);
  const isOAuthReturn = urlParams.get('oauth') === 'success';
  
  // Only show loading screen if we're actually loading
  // Don't show "Completing authentication" for logged out users with OAuth params in URL
  if (isLoading) {
    return (
      <div className="min-h-screen bg-primary flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-accent animate-spin mx-auto mb-4" />
          <p className="text-text-secondary">
            {isOAuthReturn && !isAuthenticated ? 'Completing authentication...' : 'Loading...'}
          </p>
        </div>
      </div>
    );
  }

  if (requireAuth && !isAuthenticated) {
    console.log('ProtectedRoute: Redirecting to login', { 
      requireAuth, 
      isAuthenticated, 
      isLoading, 
      user,
      isOAuthReturn 
    });
    // Redirect to login page with return url
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!requireAuth && isAuthenticated) {
    // Redirect authenticated users away from auth pages
    const from = location.state?.from?.pathname || '/';
    return <Navigate to={from} replace />;
  }

  return <>{children}</>;
}; 
import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './components/LoginPage';
import { SignupPage } from './components/SignupPage';
import ChatApp from './components/ChatApp';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes - only accessible when not authenticated */}
          <Route 
            path="/login" 
            element={
              <ProtectedRoute requireAuth={false}>
                <LoginPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/signup" 
            element={
              <ProtectedRoute requireAuth={false}>
                <SignupPage />
              </ProtectedRoute>
            } 
          />
          
          {/* Protected routes - require authentication */}
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <ChatApp />
              </ProtectedRoute>
            } 
          />
          
          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}



export default App;

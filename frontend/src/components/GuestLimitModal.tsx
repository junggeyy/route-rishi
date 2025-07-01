import React from 'react';
import { AlertTriangle, X, LogIn, UserPlus } from 'lucide-react';
import { Link } from 'react-router-dom';

interface GuestLimitModalProps {
  isOpen: boolean;
  onClose: () => void;
  messageLimit: number;
}

export const GuestLimitModal: React.FC<GuestLimitModalProps> = ({
  isOpen,
  onClose,
  messageLimit,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="glass-card rounded-xl max-w-md w-full p-6 relative">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-lg hover:bg-secondary/60 transition-colors"
        >
          <X className="w-5 h-5 text-text-secondary" />
        </button>

        {/* Icon */}
        <div className="flex justify-center mb-4">
          <div className="w-16 h-16 bg-warning/20 rounded-full flex items-center justify-center">
            <AlertTriangle className="w-8 h-8 text-warning" />
          </div>
        </div>

        {/* Content */}
        <div className="text-center mb-6">
          <h2 className="text-xl font-bold text-text-primary mb-2">
            Message Limit Reached
          </h2>
          <p className="text-text-secondary mb-4">
            You've reached the limit of {messageLimit} messages for guest users. 
            To continue chatting with RouteRishi, please create an account or sign in.
          </p>
        </div>

        {/* Action buttons */}
        <div className="space-y-3">
          <Link
            to="/signup"
            className="button-primary w-full flex items-center justify-center space-x-2"
          >
            <UserPlus className="w-5 h-5" />
            <span>Create Account</span>
          </Link>
          
          <Link
            to="/login"
            className="button-secondary w-full flex items-center justify-center space-x-2"
          >
            <LogIn className="w-5 h-5" />
            <span>Sign In</span>
          </Link>
        </div>

        {/* Benefits text */}
        <div className="mt-6 p-4 bg-accent/10 rounded-lg">
          <h3 className="text-sm font-medium text-accent mb-2">
            Benefits of creating an account:
          </h3>
          <ul className="text-sm text-text-secondary space-y-1">
            <li>• Unlimited messages</li>
            <li>• Save conversation history</li>
            <li>• Create multiple conversations</li>
            <li>• Access to premium features</li>
          </ul>
        </div>
      </div>
    </div>
  );
}; 
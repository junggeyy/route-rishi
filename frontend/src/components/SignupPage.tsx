import React, { useState } from 'react';
import { Mail, Lock, Eye, EyeOff, AlertCircle, Loader2, User } from 'lucide-react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import icon from '../assets/icon.svg';

export const SignupPage: React.FC = () => {
  const { signup, signupWithGoogle, error: authError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const from = location.state?.from?.pathname || '/';

  const validateForm = () => {
    if (!formData.fullName.trim()) {
      return 'Please enter your full name';
    }

    if (!formData.email) {
      return 'Please enter your email address';
    }

    if (!isValidEmail(formData.email)) {
      return 'Please enter a valid email address';
    }

    if (!formData.password) {
      return 'Please enter a password';
    }

    if (formData.password.length < 6) {
      return 'Password must be at least 6 characters long';
    }

    if (formData.password.length > 128) {
      return 'Password must be less than 128 characters';
    }

    if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      return 'Password must contain at least one uppercase letter, one lowercase letter, and one number';
    }

    if (formData.password !== formData.confirmPassword) {
      return 'Passwords do not match';
    }

    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);
    try {
      await signup(formData.fullName.trim(), formData.email, formData.password);
      navigate(from, { replace: true });
    } catch (error: any) {
      setError(error.message || 'Signup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignup = async () => {
    setError(null);
    setIsLoading(true);
    try {
      await signupWithGoogle();
      navigate(from, { replace: true });
    } catch (error: any) {
      setError(error.message || 'Google signup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (error) setError(null); // Clear error when user starts typing
  };

  const getPasswordStrength = (password: string) => {
    if (password.length === 0) return { strength: 0, label: '', color: '' };
    if (password.length < 6) return { strength: 25, label: 'Too short', color: 'bg-danger' };
    if (password.length < 8) return { strength: 50, label: 'Weak', color: 'bg-warning' };
    if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
      return { strength: 50, label: 'Weak', color: 'bg-warning' };
    }
    if (password.length < 12) return { strength: 75, label: 'Good', color: 'bg-travel-blue' };
    return { strength: 100, label: 'Strong', color: 'bg-success' };
  };

  const passwordStrength = getPasswordStrength(formData.password);

  return (
    <div className="min-h-screen bg-primary flex items-center justify-center p-4">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary via-secondary/20 to-primary" />
      
      <div className="relative w-full max-w-md">
        {/* Logo and title */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-travel-blue to-accent rounded-2xl flex items-center justify-center shadow-lg">
              <img src={icon} alt="RouteRishi" className="w-16 h-16" />
            </div>
          </div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Join RouteRishi</h1>
          <p className="text-text-secondary">Create your account and start exploring</p>
        </div>

        {/* Signup form */}
        <form onSubmit={handleSubmit} className="glass-card p-8 space-y-6">
          {/* Error message */}
          {(error || authError) && (
            <div className="bg-danger/10 border border-danger/20 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-danger" />
                <p className="text-danger text-sm">{error || authError}</p>
              </div>
            </div>
          )}

          {/* Full Name field */}
          <div className="space-y-2">
            <label htmlFor="fullName" className="text-text-primary font-medium">
              Full Name
            </label>
            <div className="relative">
              <User className="w-5 h-5 text-text-secondary absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                id="fullName"
                type="text"
                value={formData.fullName}
                onChange={(e) => handleInputChange('fullName', e.target.value)}
                className="input-field pl-11 w-full"
                placeholder="Enter your full name"
                disabled={isLoading}
              />
            </div>
          </div>

          {/* Email field */}
          <div className="space-y-2">
            <label htmlFor="email" className="text-text-primary font-medium">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-5 h-5 text-text-secondary absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                className="input-field pl-11 w-full"
                placeholder="Enter your email"
                disabled={isLoading}
              />
            </div>
          </div>

          {/* Password field */}
          <div className="space-y-2">
            <label htmlFor="password" className="text-text-primary font-medium">
              Password
            </label>
            <div className="relative">
              <Lock className="w-5 h-5 text-text-secondary absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                className="input-field pl-11 pr-11 w-full"
                placeholder="Create a password"
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary transition-colors"
                disabled={isLoading}
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            
            {/* Password strength indicator */}
            {formData.password && (
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-text-secondary">Password strength</span>
                  <span className={`font-medium ${
                    passwordStrength.strength >= 75 ? 'text-success' : 
                    passwordStrength.strength >= 50 ? 'text-warning' : 'text-danger'
                  }`}>
                    {passwordStrength.label}
                  </span>
                </div>
                <div className="w-full bg-secondary/30 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${passwordStrength.color}`}
                    style={{ width: `${passwordStrength.strength}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Confirm Password field */}
          <div className="space-y-2">
            <label htmlFor="confirmPassword" className="text-text-primary font-medium">
              Confirm Password
            </label>
            <div className="relative">
              <Lock className="w-5 h-5 text-text-secondary absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                id="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                className="input-field pl-11 pr-11 w-full"
                placeholder="Confirm your password"
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary transition-colors"
                disabled={isLoading}
              >
                {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          {/* Terms and Privacy */}
          <div className="text-xs text-text-secondary">
            By signing up, you agree to our{' '}
            <Link to="/terms" className="text-accent hover:text-accent/80 transition-colors">
              Terms of Service
            </Link>{' '}
            and{' '}
            <Link to="/privacy" className="text-accent hover:text-accent/80 transition-colors">
              Privacy Policy
            </Link>
          </div>

          {/* Signup button */}
          <button
            type="submit"
            disabled={isLoading}
            className="button-primary w-full flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <span>Create Account</span>
              </>
            )}
          </button>
        </form>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-border/50" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="bg-primary px-4 text-text-secondary">or continue with</span>
          </div>
        </div>

        {/* Google signup */}
        <button
          onClick={handleGoogleSignup}
          disabled={isLoading}
          className="button-secondary w-full flex items-center justify-center space-x-3"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          <span>Sign up with Google</span>
        </button>

        {/* Login link */}
        <div className="text-center mt-8">
          <p className="text-text-secondary">
            Already have an account?{' '}
            <Link
              to="/login"
              className="text-accent hover:text-accent/80 font-medium transition-colors"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}; 
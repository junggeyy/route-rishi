import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const GUEST_MESSAGE_LIMIT = 5;
const GUEST_STORAGE_KEY = 'guestMessageCount';

export const useGuestLimits = () => {
  const { isGuest } = useAuth();
  const [messageCount, setMessageCount] = useState(0);
  const [hasReachedLimit, setHasReachedLimit] = useState(false);
  const [showLimitWarning, setShowLimitWarning] = useState(false);

  useEffect(() => {
    if (isGuest) {
      // Load existing message count from localStorage
      const stored = localStorage.getItem(GUEST_STORAGE_KEY);
      const count = stored ? parseInt(stored, 10) : 0;
      setMessageCount(count);
      setHasReachedLimit(count >= GUEST_MESSAGE_LIMIT);
    } else {
      // Reset for authenticated users
      setMessageCount(0);
      setHasReachedLimit(false);
      localStorage.removeItem(GUEST_STORAGE_KEY);
    }
  }, [isGuest]);

  const incrementMessageCount = () => {
    if (!isGuest) return true; // Allow unlimited for authenticated users

    const newCount = messageCount + 1;
    setMessageCount(newCount);
    localStorage.setItem(GUEST_STORAGE_KEY, newCount.toString());

    if (newCount >= GUEST_MESSAGE_LIMIT) {
      setHasReachedLimit(true);
      setShowLimitWarning(true);
      return false; // Block the message
    }

    return true; // Allow the message
  };

  const getRemainingMessages = () => {
    if (!isGuest) return null;
    return Math.max(0, GUEST_MESSAGE_LIMIT - messageCount);
  };

  const resetGuestData = () => {
    setMessageCount(0);
    setHasReachedLimit(false);
    setShowLimitWarning(false);
    localStorage.removeItem(GUEST_STORAGE_KEY);
  };

  const dismissWarning = () => {
    setShowLimitWarning(false);
  };

  return {
    isGuest,
    messageCount,
    hasReachedLimit,
    showLimitWarning,
    remainingMessages: getRemainingMessages(),
    incrementMessageCount,
    resetGuestData,
    dismissWarning,
    messageLimit: GUEST_MESSAGE_LIMIT,
  };
}; 
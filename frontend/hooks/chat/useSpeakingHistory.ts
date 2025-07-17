import { useEffect, useState } from 'react';

/**
 * Custom hook for tracking speaking history
 * @param isUserSpeaking - Whether the user is currently speaking
 * @param isAgentSpeakingDebounced - Whether the agent is speaking (debounced)
 * @param isUserSpeakingDebounced - Whether the user is speaking (debounced)
 * @param isAgentSpeaking - Whether the agent is currently speaking
 * @returns Whether the user was speaking recently
 */
export const useSpeakingHistory = (
  isUserSpeaking: boolean,
  isAgentSpeakingDebounced: boolean,
  isUserSpeakingDebounced: boolean,
  isAgentSpeaking: boolean
): boolean => {
  const [wasUserSpeaking, setWasUserSpeaking] = useState(false);

  // Track when user was speaking (only when agent is not speaking)
  useEffect(() => {
    if (isUserSpeaking && !isAgentSpeakingDebounced) {
      setWasUserSpeaking(true);
    }
  }, [isUserSpeaking, isAgentSpeakingDebounced]);

  // Reset wasUserSpeaking when agent starts speaking
  useEffect(() => {
    if (isAgentSpeaking) {
      setWasUserSpeaking(false);
    }
  }, [isAgentSpeaking]);

  // Reset wasUserSpeaking after a timeout if agent doesn't respond
  useEffect(() => {
    if (wasUserSpeaking && !isUserSpeakingDebounced && !isAgentSpeaking) {
      const timeout = setTimeout(() => {
        setWasUserSpeaking(false);
      }, 5000); // 5 second timeout

      return () => clearTimeout(timeout);
    }
  }, [wasUserSpeaking, isUserSpeakingDebounced, isAgentSpeaking]);

  return wasUserSpeaking;
}; 
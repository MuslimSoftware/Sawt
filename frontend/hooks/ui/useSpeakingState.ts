import { useEffect, useState } from 'react';

interface UseSpeakingStateProps {
  micLevel: number;
  playbackLevel: number;
  userThreshold?: number;
  agentThreshold?: number;
  userDelay?: number;
  agentDelay?: number;
}

interface SpeakingState {
  isUserSpeaking: boolean;
  isAgentSpeaking: boolean;
  isSilent: boolean;
  isLoading: boolean;
}

export const useSpeakingState = ({
  micLevel,
  playbackLevel,
  userThreshold = 0.01,
  agentThreshold = 0.01,
  userDelay = 500,
  agentDelay = 800,
}: UseSpeakingStateProps): SpeakingState => {
  const [isUserSpeakingDebounced, setIsUserSpeakingDebounced] = useState(false);
  const [isAgentSpeakingDebounced, setIsAgentSpeakingDebounced] = useState(false);
  const [wasUserSpeaking, setWasUserSpeaking] = useState(false);

  // Determine immediate speaking states
  const isUserSpeaking = micLevel > userThreshold;
  const isAgentSpeaking = playbackLevel > agentThreshold;

  // Track when user was speaking
  useEffect(() => {
    if (isUserSpeaking) {
      setWasUserSpeaking(true);
    }
  }, [isUserSpeaking]);

  // Debounce the speaking states with delays
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsUserSpeakingDebounced(isUserSpeaking);
    }, isUserSpeaking ? 0 : userDelay);

    return () => clearTimeout(timer);
  }, [isUserSpeaking, userDelay]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsAgentSpeakingDebounced(isAgentSpeaking);
      // Reset wasUserSpeaking when agent starts speaking
      if (isAgentSpeaking) {
        setWasUserSpeaking(false);
      }
    }, isAgentSpeaking ? 0 : agentDelay);

    return () => clearTimeout(timer);
  }, [isAgentSpeaking, agentDelay]);

  // Reset wasUserSpeaking after a timeout if agent doesn't respond
  useEffect(() => {
    if (wasUserSpeaking && !isUserSpeakingDebounced && !isAgentSpeaking) {
      const timeout = setTimeout(() => {
        setWasUserSpeaking(false);
      }, 5000); // 5 second timeout

      return () => clearTimeout(timeout);
    }
  }, [wasUserSpeaking, isUserSpeakingDebounced, isAgentSpeaking]);

  // Determine loading state: when user stopped speaking but agent hasn't started yet
  const isLoading = !isUserSpeakingDebounced && !isAgentSpeakingDebounced && 
                   wasUserSpeaking && !isAgentSpeaking; // Show loading when user was speaking but stopped and agent isn't speaking yet

  return {
    isUserSpeaking: isUserSpeakingDebounced,
    isAgentSpeaking: isAgentSpeakingDebounced,
    isSilent: !isUserSpeakingDebounced && !isAgentSpeakingDebounced && !isLoading,
    isLoading,
  };
}; 
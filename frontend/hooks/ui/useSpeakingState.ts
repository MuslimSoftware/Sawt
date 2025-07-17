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

  // Determine immediate speaking states
  const isUserSpeaking = micLevel > userThreshold;
  const isAgentSpeaking = playbackLevel > agentThreshold;

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
    }, isAgentSpeaking ? 0 : agentDelay);

    return () => clearTimeout(timer);
  }, [isAgentSpeaking, agentDelay]);

  return {
    isUserSpeaking: isUserSpeakingDebounced,
    isAgentSpeaking: isAgentSpeakingDebounced,
    isSilent: !isUserSpeakingDebounced && !isAgentSpeakingDebounced,
  };
}; 
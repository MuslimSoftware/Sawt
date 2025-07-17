import { useMemo } from 'react';
import { useDebouncedBoolean } from '@/hooks/base/useDebouncedBoolean';
import { useSpeakingHistory } from '@/hooks/chat/useSpeakingHistory';

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
  agentDelay = 1200, // Increased delay to prevent flickering between words
}: UseSpeakingStateProps): SpeakingState => {
  // Memoize immediate speaking states
  const isUserSpeaking = useMemo(() => micLevel > userThreshold, [micLevel, userThreshold]);
  const isAgentSpeaking = useMemo(() => playbackLevel > agentThreshold, [playbackLevel, agentThreshold]);

  // Debounce the speaking states
  const isUserSpeakingDebounced = useDebouncedBoolean(isUserSpeaking, userDelay);
  const isAgentSpeakingDebounced = useDebouncedBoolean(isAgentSpeaking, agentDelay);

  // Track speaking history
  const wasUserSpeaking = useSpeakingHistory(
    isUserSpeaking,
    isAgentSpeakingDebounced,
    isUserSpeakingDebounced,
    isAgentSpeaking
  );

  // Memoize loading state
  const isLoading = useMemo(() => 
    !isUserSpeakingDebounced && 
    !isAgentSpeakingDebounced && 
    wasUserSpeaking && 
    !isAgentSpeaking,
    [isUserSpeakingDebounced, isAgentSpeakingDebounced, wasUserSpeaking, isAgentSpeaking]
  );

  // Memoize final states with priority logic
  const finalStates = useMemo(() => {
    const finalUserSpeaking = isUserSpeakingDebounced && !isAgentSpeakingDebounced;
    const finalAgentSpeaking = isAgentSpeakingDebounced;
    const finalSilent = !finalUserSpeaking && !finalAgentSpeaking && !isLoading;

    return {
      isUserSpeaking: finalUserSpeaking,
      isAgentSpeaking: finalAgentSpeaking,
      isSilent: finalSilent,
      isLoading,
    };
  }, [isUserSpeakingDebounced, isAgentSpeakingDebounced, isLoading]);

  return finalStates;
}; 
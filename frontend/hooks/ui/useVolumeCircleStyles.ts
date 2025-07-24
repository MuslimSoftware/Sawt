"use client";

import { useMemo } from "react";
import { useChat } from "@/contexts/ChatContext";
import { useSpeakingState } from "@/hooks/ui/useSpeakingState";
import { colors } from "@/theme/colors";

type UseVolumeCircleStylesProps = {
    micLevel: number;
    playbackLevel: number;
};

export const useVolumeCircleStyles = ({ micLevel, playbackLevel }: UseVolumeCircleStylesProps) => {
    const { isLoading } = useChat();
    const { isUserSpeaking, isAgentSpeaking, isSilent } = useSpeakingState({
        micLevel,
        playbackLevel,
    });

    const activeLevel = Math.max(micLevel, playbackLevel);
    const scale = 1 + (activeLevel * 3);

    const backgroundColor = useMemo(() => {
        if (isUserSpeaking) return colors.microphone.userSpeaking;
        if (isLoading) return colors.microphone.loading;
        if (isAgentSpeaking) return colors.microphone.agentSpeaking;
        if (isSilent) return colors.microphone.silent;
        return colors.microphone.silent;
    }, [isUserSpeaking, isAgentSpeaking, isLoading, isSilent]);

    const boxShadow = useMemo(() => {
        if (isUserSpeaking) return `0 0 25px ${colors.microphoneGlow.userSpeaking}`;
        if (isLoading) return `0 0 25px ${colors.microphoneGlow.loading}`;
        if (isAgentSpeaking) return `0 0 25px ${colors.microphoneGlow.agentSpeaking}`;
        if (isSilent) return `0 0 30px ${colors.microphoneGlow.silent}`;
        return 'none';
    }, [isSilent, isLoading, isUserSpeaking, isAgentSpeaking]);

    const transform = `scale(${scale})`;

    return {
        backgroundColor,
        boxShadow,
        transform,
        isLoading,

        // TEMPORARY
        isSilent,
        isUserSpeaking,
        isAgentSpeaking,
    };
};

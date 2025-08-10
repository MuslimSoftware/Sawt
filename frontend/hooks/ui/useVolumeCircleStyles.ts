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
    const scale = 1 + activeLevel * 3;

    const backgroundColor = useMemo(() => {
        if (isUserSpeaking) return colors.microphone.userSpeaking;
        if (isAgentSpeaking) return colors.microphone.agentSpeaking;
        if (isLoading) return colors.microphone.loading;
        if (isSilent) return colors.microphone.silent;
        return colors.microphone.silent;
    }, [isUserSpeaking, isAgentSpeaking, isLoading, isSilent]);

    const boxShadow = useMemo(() => {
        if (isSilent) return 'none';
        const blur = isSilent ? '30px' : '25px';
        return `0 0 ${blur} ${backgroundColor}`;
    }, [backgroundColor, isSilent]);

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

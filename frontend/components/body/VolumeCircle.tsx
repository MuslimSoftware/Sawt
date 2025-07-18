import { useMemo } from "react";
import { useSpeakingState } from "@/hooks/ui/useSpeakingState";
import { colors } from "@/theme/colors";
import styles from "./VolumeCircle.module.css";

type VolumeCircleProps = { 
    micLevel: number; 
    playbackLevel: number; 
};

export const VolumeCircle = ({ micLevel, playbackLevel }: VolumeCircleProps) => {
    const { isUserSpeaking, isAgentSpeaking, isSilent, isLoading } = useSpeakingState({
        micLevel,
        playbackLevel,
    });
    
    const activeLevel = Math.max(micLevel, playbackLevel);
    const scale = useMemo(() => 1 + (activeLevel * 3), [activeLevel]);

    const backgroundColor = useMemo(() => {
        if (isUserSpeaking) return colors.microphone.userSpeaking;
        if (isAgentSpeaking) return colors.microphone.agentSpeaking;
        if (isLoading) return colors.microphone.loading;
        return colors.microphone.silent;
    }, [isUserSpeaking, isAgentSpeaking, isLoading]);

    const boxShadow = useMemo(() => {
        if (isSilent) return `0 0 30px ${colors.microphoneGlow.silent}`;
        if (isLoading) return `0 0 25px ${colors.microphoneGlow.loading}`;
        if (isUserSpeaking) return `0 0 25px ${colors.microphoneGlow.userSpeaking}`;
        if (isAgentSpeaking) return `0 0 25px ${colors.microphoneGlow.agentSpeaking}`;
        return 'none';
    }, [isSilent, isLoading, isUserSpeaking, isAgentSpeaking]);

    const circleClassName = useMemo(() => {
        return `${styles.circle} ${isLoading ? styles.loading : ''}`;
    }, [isLoading]);

    return (
        <div className={styles.container}>
            <div
                className={circleClassName}
                style={{
                    background: backgroundColor,
                    transform: `scale(${scale})`,
                    boxShadow: boxShadow,
                }}
            />
        </div>
    );
};

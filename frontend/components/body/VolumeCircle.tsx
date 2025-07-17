import { useMemo } from "react";
import { useSpeakingState } from "@/hooks/ui/useSpeakingState";
import { colors, animations, borderRadius, shadows } from "@/theme/colors";

type VolumeCircleProps = { 
    micLevel: number; 
    playbackLevel: number; 
};

export const VolumeCircle = ({ micLevel, playbackLevel }: VolumeCircleProps) => {
    const baseSize = 150;
    
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

  return (
    <>
      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }
      `}</style>
      <div
        style={{
          width: "20vw",
          height: "100vh",
          display: 'grid',
          placeItems: 'center',
        }}
      >
      <div
        style={{
          width: baseSize,
          height: baseSize,
          borderRadius: borderRadius.circle,
          background: backgroundColor,
          transform: `scale(${scale})`,
          transition: animations.transition.medium,
          boxShadow: boxShadow,
          animation: isLoading ? `pulse ${animations.pulse.duration} ${animations.pulse.timing} infinite` : 'none',
        }}
              />
      </div>
    </>
  );
};

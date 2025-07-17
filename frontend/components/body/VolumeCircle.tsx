import { useMemo } from "react";
import { useSpeakingState } from "@/hooks/ui/useSpeakingState";

type VolumeCircleProps = { 
    micLevel: number; 
    playbackLevel: number; 
};

export const VolumeCircle = ({ micLevel, playbackLevel }: VolumeCircleProps) => {
    const baseSize = 150;
    
    const { isUserSpeaking, isAgentSpeaking, isSilent } = useSpeakingState({
        micLevel,
        playbackLevel,
    });
    
    const activeLevel = Math.max(micLevel, playbackLevel);
    const scale = useMemo(() => 1 + (activeLevel * 3), [activeLevel]);

    const backgroundColor = useMemo(() => {
        if (isUserSpeaking) return 'rgba(76, 175, 80, 0.9)';
        if (isAgentSpeaking) return 'rgba(33, 150, 243, 0.9)';
        return 'rgba(255, 255, 255, 0.9)';
    }, [isUserSpeaking, isAgentSpeaking]);

    const boxShadow = useMemo(() => {
        return isSilent ? '0 0 20px rgba(255, 255, 255, 0.2)' : 'none';
    }, [isSilent]);

  return (
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
          borderRadius: '50%',
          background: backgroundColor,
          transform: `scale(${scale})`,
          transition: 'all 100ms ease-out',
          boxShadow: boxShadow,
        }}
      />
    </div>
  );
};

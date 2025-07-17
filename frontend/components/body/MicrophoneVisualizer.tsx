"use client";

import { useAudioLevel } from "@/hooks/ui/useAudioLevel";
import { VolumeCircle } from "@/components/body/VolumeCircle";

type MicrophoneVisualizerProps = {
    micStream: MediaStream | null;
    playbackStream: MediaStream | null;
    muted: boolean;
};

export const MicrophoneVisualizer = ({ micStream, playbackStream, muted }: MicrophoneVisualizerProps) => {
    const { micLevel, playbackLevel } = useAudioLevel(micStream, { playbackStream: playbackStream, muted });

    return <VolumeCircle micLevel={micLevel} playbackLevel={playbackLevel} />;
}; 
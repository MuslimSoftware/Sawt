"use client";

import { useAudioLevel } from "@/hooks/useAudioLevel";
import { VolumeCircle } from "@/components/VolumeCircle";

type MicrophoneVisualizerProps = {
    micStream: MediaStream | null;
    playbackStream: MediaStream | null;
};

export const MicrophoneVisualizer = ({ micStream, playbackStream }: MicrophoneVisualizerProps) => {
    const { level } = useAudioLevel(micStream, { playbackStream: playbackStream });

    return <VolumeCircle level={level} />;
}; 
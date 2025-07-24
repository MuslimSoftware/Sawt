import { useChat } from "@/contexts/ChatContext";
import { useAudioLevel } from "@/hooks/ui/useAudioLevel";
import { VolumeCircle } from "@/components/body/VolumeCircle";

export const MicrophoneVisualizer = () => {
    const { micStream, playbackStream, muted } = useChat();
    const { micLevel, playbackLevel } = useAudioLevel(micStream, { playbackStream: playbackStream, muted });

    return <VolumeCircle micLevel={micLevel} playbackLevel={playbackLevel} />;
}; 
import { LatestMessage } from "./LatestMessage";
import { MicrophoneVisualizer } from "./MicrophoneVisualizer";

interface CenterContentProps {
    micStream: MediaStream | null;
    playbackStream: MediaStream | null;
    muted: boolean;
}

export const CenterContent = ({micStream, playbackStream, muted}: CenterContentProps) => {
    return (
        <div style={{
            width: "100%",
            height: "100%",
            display: "flex",
            justifyContent: "center",
            flexDirection: "row",
            gap: "5vw",
            alignItems: "center",
        }}>
            <LatestMessage role="user" />
            <MicrophoneVisualizer
                micStream={micStream}
                playbackStream={playbackStream}
                muted={muted}
            />
            <LatestMessage role="ai" />
        </div>
    )
}
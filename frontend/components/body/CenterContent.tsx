import { LatestMessage } from "./LatestMessage";
import { MicrophoneVisualizer } from "./MicrophoneVisualizer";
import styles from "./CenterContent.module.css";

export const CenterContent = () => {
    return (
        <div className={styles.container}>
            {/* Desktop layout - horizontal */}
            <div className={styles.desktopLayout}>
                <LatestMessage role="user" />
                <MicrophoneVisualizer />
                <LatestMessage role="ai" />
            </div>

            {/* Mobile layout - vertical */}
            <div className={styles.mobileLayout}>
                {/* User message above circle */}
                <div className={styles.mobileTopMessages}>
                    <LatestMessage role="user" />
                </div>
                
                {/* Center circle */}
                <MicrophoneVisualizer />
                
                {/* Agent message below circle */}
                <div className={styles.mobileBottomMessages}>
                    <LatestMessage role="ai" />
                </div>
            </div>
        </div>
    )
}
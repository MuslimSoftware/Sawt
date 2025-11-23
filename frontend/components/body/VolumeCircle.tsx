import { useVolumeCircleStyles } from "@/hooks/ui/useVolumeCircleStyles";
import styles from "./VolumeCircle.module.css";

type VolumeCircleProps = { 
    micLevel: number; 
    playbackLevel: number; 
};

export const VolumeCircle = ({ micLevel, playbackLevel }: VolumeCircleProps) => {
    const { backgroundColor, boxShadow, transform, isLoading } = useVolumeCircleStyles({
        micLevel,
        playbackLevel,
    });

    const circleClassName = `${styles.circle} ${isLoading ? styles.loading : ''}`;

    return (
        <div className={styles.container}>
            <div
                className={circleClassName}
                style={{
                    background: backgroundColor,
                    transform: transform,
                    boxShadow: boxShadow,
                }}
            />
        </div>
    );
};

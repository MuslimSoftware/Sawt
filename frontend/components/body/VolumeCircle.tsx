import { useMemo } from "react";

type VolumeCircleProps = { level: number };

export const VolumeCircle = ({ level }: VolumeCircleProps) => {
    const baseSize = useMemo(() => 150, []);
    const scale = useMemo(() => 1 + (level * 3), [level]); // Scale from 1x to 4x based on level

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
          background: 'rgba(255,255,255,0.9)',
          transform: `scale(${scale})`,
          transition: 'transform 50ms linear',
        }}
      />
    </div>
  );
};

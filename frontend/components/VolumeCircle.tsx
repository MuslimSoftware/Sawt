import { useMemo } from "react";

type VolumeCircleProps = { level: number };

export const VolumeCircle = ({ level }: VolumeCircleProps) => {
    const initialSize = useMemo(() => 150, []);
    const volumeSize = useMemo(() => level * 500, [level]);
    const size = useMemo(() => initialSize + volumeSize, [initialSize, volumeSize]);

  return (
    <div
      style={{
        position: 'absolute',
        inset: '0',
        display: 'grid',
        placeItems: 'center',
      }}
    >
      <div
        style={{
          width:  size,
          height: size,
          borderRadius: '50%',
          background: 'hotpink',
          transition: 'width 50ms linear, height 50ms linear',
        }}
      />
    </div>
  );
};

import { useMicrophone } from '@/hooks/base/useMicrophone';
import { useCallback, useState } from 'react';

/**
 * Hook for chat microphone: streams PCM and handles mute toggle.
 */
export const useChatMicrophone = ({ send }: { send: (data: string | ArrayBuffer) => void; }) => {
  const [muted, setMuted] = useState(false);

  const toggleMute = useCallback(() => setMuted(m => !m), []);

  const onData = useCallback(
    (buf: ArrayBuffer) => !muted && send(buf),
    [muted, send]
  );

  const onStart = useCallback(() => {}, []);

  const onStop = useCallback(
    () => send(JSON.stringify({ event: 'stop' })),
    [send]
  );

  const { isMicrophoneGranted, micStream } = useMicrophone({
    onData,
    onStart,
    onStop,
    voiceThreshold: 0.5,
  });

  return { isMicrophoneGranted, micStream, muted, toggleMute } as const;
};

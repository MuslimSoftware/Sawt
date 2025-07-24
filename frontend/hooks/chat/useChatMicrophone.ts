import { useMicrophone } from '@/hooks/base/useMicrophone';
import { useCallback, useState } from 'react';

/**
 * Hook for chat microphone: streams PCM and handles mute toggle.
 */
export const useChatMicrophone = ({ send }: { send: (data: string | ArrayBuffer) => void; }) => {
  const [muted, setMuted] = useState(false);
  const [isTransmitting, setIsTransmitting] = useState(false);

  const onData = useCallback(
    (buf: ArrayBuffer) => {
      if (!muted && isTransmitting) {
        send(buf);
      }
    },
    [muted, isTransmitting, send]
  );

  const sendStopSignal = useCallback(() => {
    if (isTransmitting) {
      send(JSON.stringify({ event: 'stop' }));
      setIsTransmitting(false);
    }
  }, [isTransmitting, send]);

  const onStart = useCallback(() => {
    setIsTransmitting(true);
  }, []);

  const onStop = useCallback(() => {
    sendStopSignal();
  }, [sendStopSignal]);

  const toggleMute = useCallback(() => {
    setMuted(currentMuted => {
      const newMuted = !currentMuted;
      if (newMuted) {
        sendStopSignal();
      }
      return newMuted;
    });
  }, [sendStopSignal]);

  const { isMicrophoneGranted, micStream } = useMicrophone({
    onData,
    onStart,
    onStop,
    voiceThreshold: 0.1,
  });

  return { isMicrophoneGranted, micStream, muted, toggleMute } as const;
};

import { useMicrophone, WorkletMessage } from '@/hooks/base/useMicrophone';
import { useCallback, useState } from 'react';
import { useLatest } from '../common/useLatest';

/**
 * Hook for chat microphone: streams PCM and handles mute toggle.
 */
export const useChatMicrophone = ({ send }: { send: (data: string | ArrayBuffer) => void; }) => {
  const [muted, setMuted] = useState(false);
  const [isTransmitting, setIsTransmitting] = useState(false);

  const isTransmittingRef = useLatest(isTransmitting);
  const mutedRef = useLatest(muted);
  const sendRef = useLatest(send);

  const sendStopSignal = useCallback(() => {
    if (isTransmittingRef.current) {
      sendRef.current(JSON.stringify({ event: 'stop' }));
      setIsTransmitting(false);
    }
  }, [isTransmittingRef, sendRef]);

  const onMessage = useCallback((msg: WorkletMessage) => {
    if (msg.event === 'start') {
      setIsTransmitting(true);
    } else if (msg.event === 'stop') {
      sendStopSignal();
    } else if (msg.audio && !mutedRef.current && isTransmittingRef.current) {
      sendRef.current(msg.audio);
    }
  }, [mutedRef, isTransmittingRef, sendRef, sendStopSignal]);

  const { isMicrophoneGranted, micStream } = useMicrophone({ onMessage });

  const toggleMute = useCallback(() => {
    setMuted(currentMuted => {
      const newMuted = !currentMuted;
      if (newMuted) {
        sendStopSignal();
      }
      return newMuted;
    });
  }, [sendStopSignal]);

  return { isMicrophoneGranted, micStream, muted, toggleMute } as const;
};

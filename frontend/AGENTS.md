# Frontend Directory Map

This document provides a map of the frontend directory to help you understand the structure of the project.

## Root

- `app/`: Contains the main application logic, including pages and layouts.
- `components/`: Contains reusable React components.
- `contexts/`: Contains React contexts for state management.
- `hooks/`: Contains custom React hooks.
- `public/`: Contains static assets, such as images and audio worklets.
- `theme/`: Contains theme configuration, such as colors.
- `AGENTS.md`: This file.
- `Dockerfile`: Dockerfile for building the frontend.
- `next-env.d.ts`: TypeScript declaration file for Next.js.
- `next.config.js`: Configuration file for Next.js.
- `package.json`: NPM package configuration.
- `README.md`: README file for the frontend.
- `tsconfig.json`: TypeScript configuration.

## `app/`

- `layout.tsx`: The main layout of the application.
- `page.module.css`: CSS module for the main page.
- `page.tsx`: The main page of the application.

## `components/`

### `body/`

- `CenterContent.module.css`: CSS module for the center content component.
- `CenterContent.tsx`: A component that centers its children.
- `LatestMessage.module.css`: CSS module for the latest message component.
- `LatestMessage.tsx`: A component that displays the latest message, now applies per-message 0.5 opacity fade on stop and clears fade when the message updates.
- `MicrophoneVisualizer.tsx`: A component that visualizes the microphone input.
- `VolumeCircle.module.css`: CSS module for the volume circle component.
- `VolumeCircle.tsx`: A component that displays a circle representing the volume level. Loading state now pulses blue instead of white, ignored while user or agent speaking. VoiceActivityDetector now pre-buffers audio to capture the start of speech.

### `header/`

- `BadgeHeader.module.css`: CSS module for the badge header component.
- `BadgeHeader.tsx`: A header component with badges, now with a two-row layout.
- `MicStatusBadge.module.css`: CSS module for the mic status badge component.
- `MicStatusBadge.tsx`: A badge that displays the microphone status.
- `SystemStatePill.module.css`: CSS module for the system state pill component.
- `SystemStatePill.tsx`: A pill that displays the current state of the backend.
- `WebsocketStatusPill.module.css`: CSS module for the websocket status pill component.
- `WebsocketStatusPill.tsx`: A pill that displays the websocket status.

## `contexts/`

- `ChatContext.tsx`: A context for managing chat state, including messages, loading status, and a function for sending data.

## `hooks/`

### `chat/`

- `useChatMicrophone.ts`: A hook for managing the microphone in the chat. It intelligently handles sending a `stop` event to the backend exactly once, whether the user stops speaking naturally (detected via silence) or explicitly mutes the microphone.
- `useChatWebsocket.ts`: A hook for managing the websocket connection in the chat. It accepts a `setMessages` function and returns the websocket status, a `sendData` function, the playback stream, and a loading status. Loading state triggers on all sends, including string events and audio buffers.

### `common/`

- `useDebouncedBoolean.ts`: A hook for debouncing a boolean value.

### `core/`

- `useAudioPlayback.ts`: A hook for playing audio.
- `useMicrophone.ts`: A hook for managing the microphone.
- `useWebsocket.ts`: A hook for managing a websocket connection.

### `ui/`

- `useAudioLevel.ts`: A hook for getting the audio level.
- `useSpeakingState.ts`: A hook for managing the speaking state.

## `public/`

### `audio-worklet/`

- `down-sampler.js`: An audio worklet for down-sampling audio; fixed double flushPrebuffer transfer bug.
- `level-meter.js`: An audio worklet for measuring audio levels.

## `theme/`

- `colors.ts`: Contains the color palette for the application.

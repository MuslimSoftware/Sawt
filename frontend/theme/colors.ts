// Theme colors for the Sawt application
export const colors = {
  // Background colors
  background: {
    primary: '#1a1a1d',
    secondary: 'rgba(255, 255, 255, 0.1)',
  },
  
  // Text colors
  text: {
    primary: '#f5f5f5',
    secondary: '#fff',
  },
  
  // Microphone visualizer states
  microphone: {
    userSpeaking: '#22c55e', // More vibrant green
    agentSpeaking: '#3b82f6', // Full blue
    loading: 'rgba(59, 130, 246, 0.3)', // Transparent blue
    silent: '#ffffff', // White
  },
  
  // Microphone visualizer glows
  microphoneGlow: {
    userSpeaking: 'rgba(34, 197, 94, 0.3)', // More vibrant green glow
    agentSpeaking: 'rgba(59, 130, 246, 0.3)', // Blue glow
    loading: 'rgba(59, 130, 246, 0.2)', // Transparent blue glow
    silent: 'rgba(255, 255, 255, 0.1)', // Subtle white glow
  },
  
  // Status pill colors (original colors)
  status: {
    success: 'rgba(40, 167, 69, 0.4)', // Green
    error: 'rgba(220, 53, 69, 0.4)', // Red
    warning: 'rgba(255, 193, 7, 0.4)', // Yellow
    disabled: 'rgba(108, 117, 125, 0.5)', // Gray
  },

  // System state pill colors
  systemState: {
    transcription_start: 'rgba(146, 40, 167, 1)', // Purple
    get_agent_response_start: 'rgba(59, 130, 246, 1)', // Blue
    tts_start: 'rgb(255, 156, 7)', // Orange
    idle: 'rgba(108, 117, 125, 0.1)', // Gray
  },
  
  // UI element colors
  ui: {
    backdrop: 'rgba(255, 255, 255, 0.15)',
    shadow: 'rgba(0, 0, 0, 0.15)',
  },
} as const;

// Animation constants
export const animations = {
  transition: {
    fast: 'all 100ms ease-out',
    medium: 'all 150ms ease-out',
    slow: 'all 300ms ease-out',
  },
  pulse: {
    duration: '1.5s',
    timing: 'ease-in-out',
  },
} as const;

// Spacing constants
export const spacing = {
  xs: '4px',
  sm: '6px',
  md: '8px',
  lg: '12px',
  xl: '14px',
  xxl: '20px',
} as const;

// Border radius constants
export const borderRadius = {
  pill: '9999px',
  circle: '50%',
  sm: '4px',
  md: '8px',
  lg: '12px',
} as const;

// Shadow constants
export const shadows = {
  sm: '0 2px 6px rgba(0, 0, 0, 0.15)',
  md: '0 0 20px rgba(0, 0, 0, 0.15)',
  lg: '0 0 25px rgba(0, 0, 0, 0.15)',
  xl: '0 0 30px rgba(0, 0, 0, 0.15)',
} as const; 
import { useEffect, useState } from 'react';

/**
 * Custom hook for debouncing boolean values
 * @param value - The boolean value to debounce
 * @param delay - The delay in milliseconds for the debounce
 * @returns The debounced boolean value
 */
export const useDebouncedBoolean = (value: boolean, delay: number): boolean => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, value ? 0 : delay);

    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}; 
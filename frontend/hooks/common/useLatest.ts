import { useLayoutEffect, useRef } from 'react';

/**
 * A React hook that returns a ref with the latest value of a variable.
 * This is useful for getting the latest value of a prop or state in a callback
 * without needing to add it to the dependency array.
 * @param value The value to store in the ref.
 * @returns A ref with the latest value.
 */
export function useLatest<T>(value: T) {
  const ref = useRef(value);
  useLayoutEffect(() => {
    ref.current = value;
  });
  return ref;
}

import { useMousePosition } from './useMousePosition'

/**
 * Hook to detect if mouse is near the right edge of the screen
 * Used to show/hide reading controls similar to navbar behavior
 */
export function useMouseAtRight(threshold: number = 80): boolean {
  const { isAtRight } = useMousePosition(threshold)
  return isAtRight
}

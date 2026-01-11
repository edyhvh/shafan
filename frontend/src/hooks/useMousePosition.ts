import { useState, useEffect, useCallback } from 'react'

interface MousePosition {
  x: number
  y: number
  isAtTop: boolean
  isAtRight: boolean
}

/**
 * Shared hook to track mouse position and derived states
 * Consolidates mousemove event listeners to improve performance
 */
export function useMousePosition(threshold: number = 80): MousePosition {
  const [mousePosition, setMousePosition] = useState<MousePosition>({
    x: 0,
    y: 0,
    isAtTop: false,
    isAtRight: false,
  })

  const handleMouseMove = useCallback(
    (event: MouseEvent) => {
      const x = event.clientX
      const y = event.clientY
      const windowWidth = window.innerWidth
      const isAtRight = windowWidth - x < threshold
      const isAtTop = y < 15

      setMousePosition({ x, y, isAtTop, isAtRight })
    },
    [threshold]
  )

  useEffect(() => {
    // Add event listener
    window.addEventListener('mousemove', handleMouseMove, { passive: true })

    // Cleanup
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
    }
  }, [handleMouseMove])

  return mousePosition
}

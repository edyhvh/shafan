import { useState, useEffect } from 'react'

/**
 * Hook to maintain consistent size for UI elements when browser zoom is above 115%
 * Returns a scale value that can be applied via transform to counteract zoom
 */
export function useZoomScale(): number {
  const [scale, setScale] = useState(1)

  useEffect(() => {
    const updateScale = () => {
      // Detect zoom level using multiple methods for accuracy
      let zoomLevel = 1

      // Method 1: Use Visual Viewport API (most accurate)
      if (window.visualViewport) {
        // Compare visual viewport width to layout viewport width
        // At 100% zoom, they should be equal
        // At 115% zoom, visual viewport is smaller (zoomed in)
        const layoutWidth = window.innerWidth
        const visualWidth = window.visualViewport.width
        if (visualWidth > 0) {
          zoomLevel = layoutWidth / visualWidth
        }
      } else {
        // Method 2: Fallback - use outerWidth vs innerWidth
        // This works for some browsers
        const outerWidth = window.outerWidth
        const innerWidth = window.innerWidth
        if (outerWidth > 0 && innerWidth > 0) {
          // Estimate zoom based on difference
          // This is less accurate but works as fallback
          zoomLevel = outerWidth / innerWidth
        }
      }

      // Apply inverse scale when zoom is >= 115% (1.15)
      if (zoomLevel >= 1.15) {
        // Scale down proportionally to maintain visual size
        setScale(1 / zoomLevel)
      } else {
        setScale(1)
      }
    }

    // Initial calculation
    updateScale()

    // Listen for resize events (zoom changes trigger resize)
    window.addEventListener('resize', updateScale)

    // Use Visual Viewport API if available (more accurate for zoom)
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', updateScale)
      window.visualViewport.addEventListener('scroll', updateScale)
    }

    // Also check on orientation change
    window.addEventListener('orientationchange', updateScale)

    return () => {
      window.removeEventListener('resize', updateScale)
      window.removeEventListener('orientationchange', updateScale)
      if (window.visualViewport) {
        window.visualViewport.removeEventListener('resize', updateScale)
        window.visualViewport.removeEventListener('scroll', updateScale)
      }
    }
  }, [])

  return scale
}

import { useState, useEffect, useCallback } from 'react'

export interface ScrollState {
  isAtTop: boolean
  scrollDirection: 'up' | 'down' | null
  shouldHideForContent: boolean
}

export function useScrollState(): ScrollState {
  const [scrollState, setScrollState] = useState<ScrollState>({
    isAtTop: true,
    scrollDirection: null,
    shouldHideForContent: false,
  })

  const [lastScrollY, setLastScrollY] = useState(0)

  const handleScroll = useCallback(() => {
    const currentScrollY = window.scrollY
    const isAtTop = currentScrollY < 10

    // Check if we should hide navbar due to content collision
    // The navbar is approximately 90px tall (top-6 = 24px + navbar height ~66px)
    // We want to hide when content would be at the navbar's position
    // A good threshold is around 70-80px of scroll
    const shouldHideForContent = currentScrollY > 70

    setScrollState((prev) => ({
      ...prev,
      isAtTop,
      shouldHideForContent,
      scrollDirection: currentScrollY > lastScrollY ? 'down' : 'up',
    }))

    setLastScrollY(currentScrollY)
  }, [lastScrollY])

  useEffect(() => {
    // Set initial state
    handleScroll()

    // Add scroll event listener
    window.addEventListener('scroll', handleScroll, { passive: true })

    // Cleanup
    return () => {
      window.removeEventListener('scroll', handleScroll)
    }
  }, [handleScroll])

  return scrollState
}

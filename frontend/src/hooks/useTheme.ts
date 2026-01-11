'use client'

import { usePreference } from './usePreference'

export type Theme = 'light' | 'dark'

/**
 * Hook to manage theme preference (light/dark)
 * @returns Object with theme value, setTheme function, toggleTheme function, and isLoaded flag
 */
export function useTheme() {
  const {
    value: theme,
    setPreference: setTheme,
    isLoaded,
  } = usePreference<Theme>(
    'shafan-theme',
    'light', // Default to light theme
    'data-theme'
  )

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
  }

  return {
    theme,
    setTheme,
    toggleTheme,
    isLoaded,
  }
}

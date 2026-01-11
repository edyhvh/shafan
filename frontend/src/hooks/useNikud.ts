'use client'

import { useBooleanPreference } from './useBooleanPreference'

/**
 * Hook to manage nikud preference with localStorage persistence
 */
export function useNikud() {
  const {
    enabled: nikudEnabled,
    toggle: toggleNikud,
    isLoaded,
  } = useBooleanPreference({
    storageKey: 'shafan-nikud-enabled',
    dataAttribute: 'data-nikud',
    defaultValue: true,
  })

  return { nikudEnabled, toggleNikud, isLoaded }
}

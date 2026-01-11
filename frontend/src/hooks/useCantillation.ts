'use client'

import { useBooleanPreference } from './useBooleanPreference'

/**
 * Hook to manage cantillation preference with localStorage persistence
 */
export function useCantillation() {
  const {
    enabled: cantillationEnabled,
    toggle: toggleCantillation,
    isLoaded,
  } = useBooleanPreference({
    storageKey: 'shafan-cantillation-enabled',
    dataAttribute: 'data-cantillation',
    defaultValue: false,
  })

  return { cantillationEnabled, toggleCantillation, isLoaded }
}

'use client'

import { useBooleanPreference } from './useBooleanPreference'

/**
 * Hook to manage sefer (continuous paragraph) display preference with localStorage persistence
 * When enabled (default), verses are displayed as continuous text like a paragraph
 * When disabled, verses are displayed separately, each on its own line
 */
export function useSefer() {
  const {
    enabled: seferEnabled,
    toggle: toggleSefer,
    isLoaded,
  } = useBooleanPreference({
    storageKey: 'shafan-sefer-enabled',
    dataAttribute: 'data-sefer',
    defaultValue: true,
  })

  return { seferEnabled, toggleSefer, isLoaded }
}

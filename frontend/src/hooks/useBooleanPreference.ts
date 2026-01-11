'use client'

import { useCallback } from 'react'
import { usePreference } from './usePreference'

interface BooleanPreferenceOptions {
  storageKey: string
  dataAttribute: string
  defaultValue: boolean
}

/**
 * Generic hook for boolean preferences with localStorage persistence
 * @param options Configuration options for the preference
 * @returns Object with enabled state, toggle function, and isLoaded flag
 */
export function useBooleanPreference({
  storageKey,
  dataAttribute,
  defaultValue,
}: BooleanPreferenceOptions) {
  const { value, setPreference, isLoaded } = usePreference<string>(
    storageKey,
    defaultValue ? 'true' : 'false',
    dataAttribute
  )

  const enabled = value === 'true'

  const toggle = useCallback(() => {
    setPreference(enabled ? 'false' : 'true')
  }, [enabled, setPreference])

  return { enabled, toggle, isLoaded }
}

'use client'

import { useCallback } from 'react'
import { usePreference } from './usePreference'

const STORAGE_KEY = 'shafan-sefer-enabled'
const DATA_ATTRIBUTE = 'data-sefer'
const DEFAULT_VALUE = 'true' as const

type SeferValue = 'true' | 'false'

/**
 * Hook to manage sefer (continuous paragraph) display preference with localStorage persistence
 * When enabled (default), verses are displayed as continuous text like a paragraph
 * When disabled, verses are displayed separately, each on its own line
 */
export function useSefer() {
  const { value, setPreference, isLoaded } = usePreference<SeferValue>(
    STORAGE_KEY,
    DEFAULT_VALUE,
    DATA_ATTRIBUTE
  )

  const seferEnabled = value === 'true'

  const toggleSefer = useCallback(() => {
    setPreference(seferEnabled ? 'false' : 'true')
  }, [seferEnabled, setPreference])

  return { seferEnabled, toggleSefer, isLoaded }
}

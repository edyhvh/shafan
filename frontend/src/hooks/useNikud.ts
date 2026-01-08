'use client'

import { useCallback } from 'react'
import { usePreference } from './usePreference'

const STORAGE_KEY = 'shafan-nikud-enabled'
const DATA_ATTRIBUTE = 'data-nikud'
const DEFAULT_VALUE = 'true' as const

type NikudValue = 'true' | 'false'

/**
 * Hook to manage nikud preference with localStorage persistence
 */
export function useNikud() {
  const { value, setPreference, isLoaded } = usePreference<NikudValue>(
    STORAGE_KEY,
    DEFAULT_VALUE,
    DATA_ATTRIBUTE
  )

  const nikudEnabled = value === 'true'

  const toggleNikud = useCallback(() => {
    setPreference(nikudEnabled ? 'false' : 'true')
  }, [nikudEnabled, setPreference])

  return { nikudEnabled, toggleNikud, isLoaded }
}

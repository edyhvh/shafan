'use client'

import { useCallback } from 'react'
import { usePreference } from './usePreference'

const STORAGE_KEY = 'shafan-text-source'
const DATA_ATTRIBUTE = 'data-text-source'
const DEFAULT_VALUE = 'hutter' as const

type TextSource = 'hutter' | 'delitzsch'

/**
 * Hook to manage text source preference (Hutter vs Delitzsch) with localStorage persistence
 */
export function useTextSource() {
  const { value, setPreference, isLoaded } = usePreference<TextSource>(
    STORAGE_KEY,
    DEFAULT_VALUE,
    DATA_ATTRIBUTE
  )

  const toggleTextSource = useCallback(() => {
    setPreference((prev) => (prev === 'hutter' ? 'delitzsch' : 'hutter'))
  }, [setPreference])

  return {
    textSource: value,
    toggleTextSource,
    isLoaded,
  }
}

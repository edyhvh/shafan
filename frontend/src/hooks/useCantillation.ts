'use client'

import { useCallback } from 'react'
import { usePreference } from './usePreference'

const STORAGE_KEY = 'shafan-cantillation-enabled'
const DATA_ATTRIBUTE = 'data-cantillation'
const DEFAULT_VALUE = 'false' as const

type CantillationValue = 'true' | 'false'

/**
 * Hook to manage cantillation preference with localStorage persistence
 */
export function useCantillation() {
  const { value, setPreference, isLoaded } = usePreference<CantillationValue>(
    STORAGE_KEY,
    DEFAULT_VALUE,
    DATA_ATTRIBUTE
  )

  const cantillationEnabled = value === 'true'

  const toggleCantillation = useCallback(() => {
    setPreference(cantillationEnabled ? 'false' : 'true')
  }, [cantillationEnabled, setPreference])

  return { cantillationEnabled, toggleCantillation, isLoaded }
}

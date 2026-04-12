'use client'

import { useEffect } from 'react'

const PREFERENCE_ATTRIBUTE_MAP = [
  ['shafan-nikud-enabled', 'data-nikud'],
  ['shafan-cantillation-enabled', 'data-cantillation'],
  ['shafan-text-source', 'data-text-source'],
  ['shafan-sefer-enabled', 'data-sefer'],
  ['shafan-tth-enabled', 'data-tth'],
  ['shafan-theme', 'data-theme'],
] as const

/**
 * Sync persisted user preferences onto <html> during client navigations.
 */
export default function InitialPreferencesSync() {
  useEffect(() => {
    for (const [storageKey, dataAttribute] of PREFERENCE_ATTRIBUTE_MAP) {
      try {
        const value = localStorage.getItem(storageKey)
        if (value !== null) {
          document.documentElement.setAttribute(dataAttribute, value)
        }
      } catch {
        // Ignore storage access errors.
      }
    }
  }, [])

  return null
}

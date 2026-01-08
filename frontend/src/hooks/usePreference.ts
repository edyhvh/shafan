'use client'

import { useState, useEffect, useCallback, useRef } from 'react'

/**
 * Get initial preference state from data attribute (set by inline script) or localStorage
 */
function getInitialPreferenceState<T extends string>(
  storageKey: string,
  defaultValue: T,
  dataAttribute: string
): T {
  if (typeof window === 'undefined') return defaultValue

  // First check the data attribute set by the inline script in layout
  const dataAttr = document.documentElement.getAttribute(dataAttribute)
  if (dataAttr !== null) {
    return dataAttr as T
  }

  // Fallback to localStorage
  try {
    const stored = localStorage.getItem(storageKey)
    if (stored !== null) {
      return stored as T
    }
  } catch {
    // Storage error
  }

  return defaultValue
}

/**
 * Generic hook to manage any localStorage preference with data attribute sync
 * @param storageKey - localStorage key to store the preference
 * @param defaultValue - Default value if no preference is stored
 * @param dataAttribute - HTML data attribute name to sync with (e.g., 'data-nikud')
 * @returns Object with value, setValue function, toggle function (if boolean), and isLoaded flag
 */
export function usePreference<T extends string>(
  storageKey: string,
  defaultValue: T,
  dataAttribute: string
) {
  const [value, setValue] = useState<T>(() =>
    getInitialPreferenceState(storageKey, defaultValue, dataAttribute)
  )
  const [isLoaded, setIsLoaded] = useState(false)
  const valueRef = useRef(value)

  // Keep ref in sync with value
  useEffect(() => {
    valueRef.current = value
  }, [value])

  // Mark as loaded on mount
  useEffect(() => {
    setIsLoaded(true)
  }, [])

  // Save to localStorage and update data attribute when value changes
  useEffect(() => {
    if (typeof window === 'undefined') return

    try {
      localStorage.setItem(storageKey, value)
      document.documentElement.setAttribute(dataAttribute, value)
    } catch {
      // Storage error (e.g., quota exceeded)
    }
  }, [value, storageKey, dataAttribute])

  // Listen for storage changes from other tabs/windows and custom events for same-tab sync
  useEffect(() => {
    if (typeof window === 'undefined') return

    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === storageKey && e.newValue !== null) {
        setValue(e.newValue as T)
      }
    }

    // Listen for custom storage events (for same-tab updates)
    const handleCustomStorageChange = (e: Event) => {
      const customEvent = e as CustomEvent<{ key: string; value: T }>
      if (customEvent.detail?.key === storageKey) {
        setValue(customEvent.detail.value)
      }
    }

    window.addEventListener('storage', handleStorageChange)
    window.addEventListener('preference-change', handleCustomStorageChange)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('preference-change', handleCustomStorageChange)
    }
  }, [storageKey])

  // Dispatch custom event when value changes (for same-tab sync between components)
  useEffect(() => {
    if (typeof window === 'undefined' || !isLoaded) return

    const event = new CustomEvent('preference-change', {
      detail: { key: storageKey, value },
    })
    window.dispatchEvent(event)
  }, [value, storageKey, isLoaded])

  const setPreference = useCallback((newValue: T | ((prev: T) => T)) => {
    setValue((prev) => {
      if (typeof newValue === 'function') {
        return (newValue as (prev: T) => T)(prev)
      }
      return newValue
    })
  }, [])

  return { value, setPreference, isLoaded }
}

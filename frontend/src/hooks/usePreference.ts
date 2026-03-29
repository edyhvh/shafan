'use client'

import { useState, useEffect, useCallback, useRef } from 'react'

/**
 * Read preference from data attribute (set by inline script) or localStorage.
 * Only called inside useEffect (client-side) to avoid hydration mismatches.
 */
function readPreferenceFromDOM<T extends string>(
  storageKey: string,
  dataAttribute: string
): T | null {
  // Read localStorage first — it is the source of truth.
  // Data attributes on <html> are set by the inline script but React hydration
  // reconciles them back to the JSX-hardcoded defaults, making them unreliable.
  try {
    const stored = localStorage.getItem(storageKey)
    if (stored !== null) {
      return stored as T
    }
  } catch {
    // Storage error
  }

  // Fallback to data attribute (useful on very first visit with no localStorage)
  const dataAttr = document.documentElement.getAttribute(dataAttribute)
  if (dataAttr !== null) {
    return dataAttr as T
  }

  return null
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
  const [value, setValue] = useState<T>(defaultValue)
  const [isLoaded, setIsLoaded] = useState(false)
  const valueRef = useRef(value)

  // Keep ref in sync with value
  useEffect(() => {
    valueRef.current = value
  }, [value])

  // On mount: read real value from DOM/localStorage, then mark loaded
  useEffect(() => {
    const stored = readPreferenceFromDOM<T>(storageKey, dataAttribute)
    if (stored !== null) {
      setValue(stored)
    }
    setIsLoaded(true)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Save to localStorage and update data attribute when value changes.
  // Guard with isLoaded so the default value doesn't overwrite the real stored
  // value before the on-mount read effect has had a chance to run.
  useEffect(() => {
    if (typeof window === 'undefined') return
    if (!isLoaded) return

    try {
      localStorage.setItem(storageKey, value)
      document.documentElement.setAttribute(dataAttribute, value)
    } catch {
      // Storage error (e.g., quota exceeded)
    }
  }, [value, storageKey, dataAttribute, isLoaded])

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

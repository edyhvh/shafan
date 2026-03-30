'use client'

import { useEffect, useRef } from 'react'
import { usePathname } from 'next/navigation'
import { useBooleanPreference } from './useBooleanPreference'

const STORAGE_KEY = 'shafan-tth-enabled'
const DATA_ATTRIBUTE = 'data-tth'

/**
 * Sync ?tth=true in the browser URL without triggering navigation.
 */
function syncTTHParam(enabled: boolean) {
  if (typeof window === 'undefined') return
  const url = new URL(window.location.href)
  if (enabled) {
    url.searchParams.set('tth', 'true')
  } else {
    url.searchParams.delete('tth')
  }
  if (url.href !== window.location.href) {
    window.history.replaceState(window.history.state, '', url.href)
  }
}

/**
 * Hook to manage TTH (Spanish translation) mode with localStorage persistence
 * and URL query-param sync (?tth=true).
 */
export function useTTH() {
  const {
    enabled: tthEnabled,
    toggle: toggleTTH,
    isLoaded,
  } = useBooleanPreference({
    storageKey: STORAGE_KEY,
    dataAttribute: DATA_ATTRIBUTE,
    defaultValue: false,
  })

  const pathname = usePathname()
  const hasReadUrl = useRef(false)
  // Keep initial server/client render deterministic to avoid hydration mismatch.
  const effectiveTTHEnabled = isLoaded ? tthEnabled : false

  // On first load: if ?tth=true is in the URL, enable TTH (URL overrides localStorage)
  useEffect(() => {
    if (hasReadUrl.current || !isLoaded) return
    hasReadUrl.current = true

    const params = new URLSearchParams(window.location.search)
    if (params.get('tth') === 'true' && !tthEnabled) {
      toggleTTH() // enable
    }
    // Sync URL to current state (handles case where localStorage already had it enabled)
    syncTTHParam(params.get('tth') === 'true' || tthEnabled)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoaded])

  // Keep URL in sync whenever tthEnabled changes (e.g. user toggles)
  useEffect(() => {
    if (!isLoaded) return
    syncTTHParam(tthEnabled)
  }, [tthEnabled, isLoaded])

  // Re-apply ?tth=true after client-side navigations (Next.js strips query params)
  useEffect(() => {
    if (!isLoaded) return
    syncTTHParam(tthEnabled)
  }, [pathname, tthEnabled, isLoaded])

  return { tthEnabled, effectiveTTHEnabled, toggleTTH, isLoaded }
}

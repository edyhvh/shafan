'use client';

import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'shafan-nikud-enabled';

/**
 * Get initial nikud state from data attribute (set by inline script) or localStorage
 */
function getInitialNikudState(): boolean {
  if (typeof window === 'undefined') return true;

  // First check the data attribute set by the inline script in layout
  const dataAttr = document.documentElement.getAttribute('data-nikud');
  if (dataAttr !== null) {
    return dataAttr === 'true';
  }

  // Fallback to localStorage
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored !== null) {
      return stored === 'true';
    }
  } catch {
    // Storage error
  }

  return true;
}

/**
 * Hook to manage nikud preference with localStorage persistence
 */
export function useNikud() {
  const [nikudEnabled, setNikudEnabled] = useState(getInitialNikudState);
  const [isLoaded, setIsLoaded] = useState(false);

  // Mark as loaded on mount
  useEffect(() => {
    setIsLoaded(true);
  }, []);

  // Save to localStorage and update data attribute when value changes
  useEffect(() => {
    if (typeof window === 'undefined') return;

    try {
      localStorage.setItem(STORAGE_KEY, String(nikudEnabled));
      document.documentElement.setAttribute('data-nikud', String(nikudEnabled));
    } catch {
      // Storage error (e.g., quota exceeded)
    }
  }, [nikudEnabled]);

  const toggleNikud = useCallback(() => {
    setNikudEnabled((prev) => !prev);
  }, []);

  return { nikudEnabled, toggleNikud, isLoaded };
}


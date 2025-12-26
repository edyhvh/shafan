'use client';

import { useEffect, useCallback } from 'react';

const STORAGE_KEY = 'shafan-last-book';

export interface LastBookLocation {
  bookId: string;
  chapterId: string;
}

/**
 * Hook to manage the last visited book/chapter in localStorage
 */
export function useLastBook() {
  const getLastBook = useCallback((): LastBookLocation | null => {
    if (typeof window === 'undefined') return null;

    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        return JSON.parse(stored) as LastBookLocation;
      }
    } catch {
      // Invalid JSON or storage error
    }
    return null;
  }, []);

  const saveLastBook = useCallback((bookId: string, chapterId: string) => {
    if (typeof window === 'undefined') return;

    try {
      const location: LastBookLocation = { bookId, chapterId };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(location));
    } catch {
      // Storage error (e.g., quota exceeded)
    }
  }, []);

  return { getLastBook, saveLastBook };
}

/**
 * Get the last visited book location (can be called outside of hooks)
 */
export function getLastBookLocation(): LastBookLocation | null {
  if (typeof window === 'undefined') return null;

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored) as LastBookLocation;
    }
  } catch {
    // Invalid JSON or storage error
  }
  return null;
}


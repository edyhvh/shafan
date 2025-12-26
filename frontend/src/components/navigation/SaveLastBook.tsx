'use client'

import { useEffect } from 'react'
import { useLastBook } from '@/hooks/useLastBook'

interface SaveLastBookProps {
  bookId: string
  chapterId: string
}

/**
 * Client component that saves the current book/chapter location to localStorage
 */
export default function SaveLastBook({ bookId, chapterId }: SaveLastBookProps) {
  const { saveLastBook } = useLastBook()

  useEffect(() => {
    saveLastBook(bookId, chapterId)
  }, [bookId, chapterId, saveLastBook])

  return null
}

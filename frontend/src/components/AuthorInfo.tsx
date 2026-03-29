'use client'

import { useTextSource } from '@/hooks/useTextSource'
import { isNewTestament, type BookName } from '@/lib/books'
import { useState, useEffect } from 'react'
import { useTTH } from '@/hooks/useTTH'

interface AuthorInfoProps {
  bookName: BookName
  hutterAuthor: string
  hutterYear: string
}

/**
 * Component that displays author and publication year information
 * Dynamically shows Hutter or Delitzsch info based on text source for New Testament
 * Shows Masoretic Text info for Tanaj books
 */
export default function AuthorInfo({
  bookName,
  hutterAuthor,
  hutterYear,
}: AuthorInfoProps) {
  const { textSource, isLoaded } = useTextSource()
  const { tthEnabled } = useTTH()
  const isNT = isNewTestament(bookName)
  const [mounted, setMounted] = useState(false)

  // Ensure component is mounted before rendering dynamic content
  useEffect(() => {
    setMounted(true)
  }, [])

  // If TTH is enabled, show TTH author
  if (tthEnabled) {
    return (
      <div className="mt-12 flex justify-center">
        <p
          className="font-ui-latin text-sm text-gray text-center"
          suppressHydrationWarning
        >
          Traducción Textual del Hebreo
        </p>
      </div>
    )
  }

  // For New Testament: show Hutter or Delitzsch based on textSource
  // For Tanaj: show Masoretic Text info
  let author: string
  let year: string

  if (isNT) {
    // During SSR and initial render, use hutter to match server
    // After hydration, use the actual textSource
    if (mounted && isLoaded && textSource === 'delitzsch') {
      author = 'Franz Delitzsch'
      year = '1877'
    } else {
      author = hutterAuthor || 'Elias Hutter'
      year = hutterYear || '1599–1602'
    }
  } else {
    // Tanaj - Masoretic Text
    author = 'Masoretic Text'
    year = ''
  }

  // Don't show empty author/year
  if (!author) {
    return null
  }

  return (
    <div className="mt-12 flex justify-center">
      <p
        className="font-ui-latin text-sm text-gray text-center"
        suppressHydrationWarning
      >
        {author}
        {year && ` (${year})`}
      </p>
    </div>
  )
}

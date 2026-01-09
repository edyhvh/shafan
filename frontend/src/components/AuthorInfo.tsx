'use client'

import { useTextSource } from '@/hooks/useTextSource'
import { isNewTestament, type BookName } from '@/lib/books'

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
  const { textSource } = useTextSource()
  const isNT = isNewTestament(bookName)

  // For New Testament: show Hutter or Delitzsch based on textSource
  // For Tanaj: show Masoretic Text info
  let author: string
  let year: string

  if (isNT) {
    if (textSource === 'delitzsch') {
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
      <p className="font-ui-latin text-sm text-gray text-center">
        {author}
        {year && ` (${year})`}
      </p>
    </div>
  )
}

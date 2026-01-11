import { useState, useEffect } from 'react'
import { AVAILABLE_BOOKS, searchBooks, type BookName } from '@/lib/books'

/**
 * Hook to manage book search functionality
 */
export function useBookSearch() {
  const [bookSearchQuery, setBookSearchQuery] = useState('')
  const [filteredBooks, setFilteredBooks] = useState<BookName[]>([
    ...AVAILABLE_BOOKS,
  ])

  // Filter books based on search query
  useEffect(() => {
    if (bookSearchQuery.trim()) {
      const results = searchBooks(bookSearchQuery)
      setFilteredBooks(results)
    } else {
      setFilteredBooks([...AVAILABLE_BOOKS])
    }
  }, [bookSearchQuery])

  const clearBookSearch = () => setBookSearchQuery('')

  return {
    bookSearchQuery,
    setBookSearchQuery,
    filteredBooks,
    clearBookSearch,
  }
}

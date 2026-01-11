import { useState, useEffect } from 'react'

interface Chapter {
  number: number
  hebrew_letter: string
}

/**
 * Hook to manage chapter search functionality
 */
export function useChapterSearch(chapters: Chapter[]) {
  const [chapterSearchQuery, setChapterSearchQuery] = useState('')
  const [filteredChapters, setFilteredChapters] = useState<Chapter[]>(chapters)

  // Filter chapters based on search query
  useEffect(() => {
    if (chapterSearchQuery.trim()) {
      const query = chapterSearchQuery.toLowerCase()
      const filtered = chapters.filter(
        (chapter) =>
          chapter.number.toString().includes(query) ||
          chapter.hebrew_letter.includes(chapterSearchQuery)
      )
      setFilteredChapters(filtered)
    } else {
      setFilteredChapters(chapters)
    }
  }, [chapterSearchQuery, chapters])

  const clearChapterSearch = () => setChapterSearchQuery('')

  return {
    chapterSearchQuery,
    setChapterSearchQuery,
    filteredChapters,
    clearChapterSearch,
  }
}

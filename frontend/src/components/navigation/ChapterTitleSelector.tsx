'use client'

import { useState, useRef, useEffect } from 'react'
import { useClickOutside } from '@/hooks/useClickOutside'
import { useBookSearch } from '@/hooks/useBookSearch'
import { useChapterSearch } from '@/hooks/useChapterSearch'
import SearchableDropdown from '@/components/SearchableDropdown'
import {
  BOOK_DISPLAY_NAMES,
  BOOK_HEBREW_INFO,
  type BookName,
} from '@/lib/books'

interface ChapterTitleSelectorProps {
  bookDisplayName: string
  currentChapter: number
  hebrewLetter?: string
  chapters: { number: number; hebrew_letter: string }[]
  bookName: BookName
  locale: string
}

export default function ChapterTitleSelector({
  bookDisplayName,
  currentChapter,
  hebrewLetter,
  chapters,
  bookName,
  locale,
}: ChapterTitleSelectorProps) {
  const [isChapterOpen, setIsChapterOpen] = useState(false)
  const [isBookOpen, setIsBookOpen] = useState(false)
  const chapterDropdownRef = useRef<HTMLDivElement>(null)
  const bookDropdownRef = useRef<HTMLDivElement>(null)

  // Use custom hooks for search functionality
  const {
    bookSearchQuery,
    setBookSearchQuery,
    filteredBooks,
    clearBookSearch,
  } = useBookSearch()
  const {
    chapterSearchQuery,
    setChapterSearchQuery,
    filteredChapters,
    clearChapterSearch,
  } = useChapterSearch(chapters)

  // Clear search when closing dropdowns
  useEffect(() => {
    if (!isBookOpen) clearBookSearch()
  }, [isBookOpen, clearBookSearch])

  useEffect(() => {
    if (!isChapterOpen) clearChapterSearch()
  }, [isChapterOpen, clearChapterSearch])

  // Close dropdowns when clicking outside
  useClickOutside(
    chapterDropdownRef,
    () => setIsChapterOpen(false),
    isChapterOpen
  )
  useClickOutside(bookDropdownRef, () => setIsBookOpen(false), isBookOpen)

  // Close dropdowns when navbar dropdowns open
  useEffect(() => {
    const handleClosePageDropdowns = () => {
      setIsChapterOpen(false)
      setIsBookOpen(false)
    }

    window.addEventListener('close-page-dropdowns', handleClosePageDropdowns)
    return () => {
      window.removeEventListener(
        'close-page-dropdowns',
        handleClosePageDropdowns
      )
    }
  }, [])

  // Get Hebrew info for the current book (for en/es locales)
  const hebrewInfo = BOOK_HEBREW_INFO[bookName]
  const transliteration =
    locale === 'es'
      ? hebrewInfo?.transliteration.es
      : hebrewInfo?.transliteration.en

  return (
    <div className="text-center mb-8 pt-12">
      {/* Hebrew name and transliteration (only for en/es locales) */}
      {locale !== 'he' && hebrewInfo && (
        <div className="mb-3 text-center">
          <div className="font-bible-hebrew text-xl text-black/70 dark:text-[#d5c4a1]/80 leading-tight">
            {hebrewInfo.hebrew}
          </div>
          <div className="text-[11px] text-black/35 dark:text-[#d5c4a1]/50 font-light tracking-wide">
            {transliteration}
          </div>
        </div>
      )}
      <h1 className="font-ui-latin text-lg text-black dark:text-[#d5c4a1] mb-1 inline-flex items-center gap-2">
        {/* Book selector with SearchableDropdown */}
        <div ref={bookDropdownRef}>
          <SearchableDropdown
            triggerLabel={bookDisplayName}
            triggerClassName={`h-[36px] px-3 flex items-center justify-center font-semibold text-base cursor-pointer transition-all duration-200 neumorphism ${
              locale === 'he' ? 'font-ui-hebrew' : ''
            }`}
            triggerAriaLabel="Select book"
            isOpen={isBookOpen}
            onToggle={() => {
              setIsBookOpen(!isBookOpen)
              setIsChapterOpen(false)
            }}
            searchQuery={bookSearchQuery}
            onSearchChange={setBookSearchQuery}
            searchPlaceholder="Search for..."
            items={filteredBooks.map((book) => {
              const displayName = BOOK_DISPLAY_NAMES[book]
              return {
                id: book,
                label:
                  displayName[locale as 'he' | 'es' | 'en'] || displayName.en,
                href: `/${locale}/book/${book}/chapter/1`,
                isCurrent: book === bookName,
                onClick: () => setIsBookOpen(false),
              }
            })}
            emptyMessage="No books found"
          />
        </div>

        {/* Chapter selector with SearchableDropdown */}
        <div ref={chapterDropdownRef}>
          <SearchableDropdown
            triggerLabel={
              locale === 'he' && hebrewLetter
                ? hebrewLetter
                : currentChapter.toString()
            }
            triggerClassName={`min-w-[36px] h-[36px] px-2 flex items-center justify-center font-semibold text-base cursor-pointer transition-all duration-200 neumorphism ${
              locale === 'he' && hebrewLetter ? 'font-ui-hebrew' : ''
            }`}
            triggerAriaLabel="Select chapter"
            isOpen={isChapterOpen && chapters.length > 1}
            onToggle={() => {
              setIsChapterOpen(!isChapterOpen)
              setIsBookOpen(false)
            }}
            searchQuery={chapterSearchQuery}
            onSearchChange={setChapterSearchQuery}
            searchPlaceholder="Search for..."
            items={filteredChapters.map((chapter) => ({
              id: chapter.number.toString(),
              label: chapter.number.toString(),
              href: `/${locale}/book/${bookName}/chapter/${chapter.number}`,
              isCurrent: chapter.number === currentChapter,
              onClick: () => setIsChapterOpen(false),
            }))}
            emptyMessage="No chapters found"
            gridCols={4}
            dropdownClassName="dropdown-panel"
          />
        </div>
      </h1>
    </div>
  )
}

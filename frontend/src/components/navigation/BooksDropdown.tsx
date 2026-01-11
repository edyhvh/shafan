'use client'

import { useState, useEffect, useRef } from 'react'
import {
  AVAILABLE_BOOKS,
  BOOK_DISPLAY_NAMES,
  loadBookClient,
  searchBooks,
  type BookName,
} from '@/lib/books'
import { Book } from '@/lib/types'
import ChaptersDropdown from './ChaptersDropdown'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { getLocaleFromPath } from '@/lib/locale'
import { ChevronRight, LoadingSpinner } from '@/components/icons'

interface BooksDropdownProps {
  isOpen: boolean
  onClose: () => void
}

export default function BooksDropdown({ isOpen, onClose }: BooksDropdownProps) {
  const [hoveredBook, setHoveredBook] = useState<BookName | null>(null)
  const [hoveredBookTop, setHoveredBookTop] = useState<number>(0)
  const [loadedBooks, setLoadedBooks] = useState<Record<string, Book | null>>(
    {}
  )
  const [loadingBooks, setLoadingBooks] = useState<Set<BookName>>(new Set())
  const [searchQuery, setSearchQuery] = useState('')
  const [filteredBooks, setFilteredBooks] = useState<BookName[]>([
    ...AVAILABLE_BOOKS,
  ])
  const containerRef = useRef<HTMLDivElement>(null)
  const searchInputRef = useRef<HTMLInputElement>(null)
  const closeTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const pathname = usePathname()
  const locale = getLocaleFromPath(pathname)

  // Filter books based on search query
  useEffect(() => {
    if (searchQuery.trim()) {
      const results = searchBooks(searchQuery)
      setFilteredBooks(results)
    } else {
      setFilteredBooks([...AVAILABLE_BOOKS])
    }
  }, [searchQuery])

  // Focus search input when dropdown opens
  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      setTimeout(() => searchInputRef.current?.focus(), 100)
    } else {
      setSearchQuery('')
    }
  }, [isOpen])

  const handleBookHover = (bookName: BookName, element: HTMLElement) => {
    setHoveredBook(bookName)
    if (containerRef.current) {
      const containerRect = containerRef.current.getBoundingClientRect()
      const elementRect = element.getBoundingClientRect()
      setHoveredBookTop(elementRect.top - containerRect.top)
    }
  }

  useEffect(() => {
    if (
      hoveredBook &&
      !(hoveredBook in loadedBooks) &&
      !loadingBooks.has(hoveredBook)
    ) {
      setLoadingBooks((prev) => new Set(prev).add(hoveredBook))

      loadBookClient(hoveredBook).then((book) => {
        // Store the result (even if null) to indicate loading is complete
        setLoadedBooks((prev) => ({ ...prev, [hoveredBook]: book }))
        setLoadingBooks((prev) => {
          const next = new Set(prev)
          next.delete(hoveredBook)
          return next
        })
      })
    }
  }, [hoveredBook, loadedBooks, loadingBooks])

  // Clear timeout on unmount
  useEffect(() => {
    return () => {
      if (closeTimeoutRef.current) {
        clearTimeout(closeTimeoutRef.current)
      }
    }
  }, [])

  if (!isOpen) return null

  const book = hoveredBook ? loadedBooks[hoveredBook] : null
  const isLoading = hoveredBook && loadingBooks.has(hoveredBook)
  const hasLoadedBook = hoveredBook && hoveredBook in loadedBooks
  const bookNotAvailable = hasLoadedBook && !book

  const handleMouseLeave = () => {
    setHoveredBook(null)
    // Clear any existing timeout
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current)
    }
    // Set a new timeout to close
    closeTimeoutRef.current = setTimeout(() => {
      onClose()
    }, 200)
  }

  const handleMouseEnter = () => {
    // Cancel any pending close when mouse enters dropdown
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current)
      closeTimeoutRef.current = null
    }
  }

  return (
    <div
      ref={containerRef}
      className="books-dropdown-container relative min-w-[280px] z-50"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Dropdown panel with search and books list */}
      <div className="dropdown-panel overflow-hidden">
        {/* Search input */}
        <div className="p-2 border-b border-black/5">
          <div className="relative">
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted z-10"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              ref={searchInputRef}
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for..."
              className="w-full pl-10 pr-4 py-2 text-sm font-ui-latin text-primary neumorphism-inset outline-none placeholder:text-muted rounded-lg"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        </div>

        {/* Scrollable books list */}
        <div className="max-h-[500px] overflow-y-auto py-1 scroll-smooth scroll-smooth-enhanced scrollbar-thin scrollbar-thumb-black/20 scrollbar-track-transparent hover:scrollbar-thumb-black/30">
          {filteredBooks.length > 0 ? (
            filteredBooks.map((bookName) => {
              const displayName = BOOK_DISPLAY_NAMES[bookName]
              const isHovered = hoveredBook === bookName

              return (
                <div
                  key={bookName}
                  onMouseEnter={(e) =>
                    handleBookHover(bookName, e.currentTarget)
                  }
                >
                  <Link
                    href={`/${locale}/book/${bookName}/chapter/1`}
                    className={`flex items-center justify-between px-6 py-3 text-base font-ui-latin font-semibold text-primary hover:bg-primary/5 transition-all border-b border-primary/8 last:border-b-0 ${
                      isHovered ? 'bg-primary/5' : ''
                    } ${locale === 'he' ? 'flex-row-reverse' : ''}`}
                    onClick={onClose}
                  >
                    <span>
                      {displayName[locale as 'he' | 'es' | 'en'] ||
                        displayName.en}
                    </span>
                    <ChevronRight
                      className={`text-muted ${locale === 'he' ? 'scale-x-[-1]' : ''}`}
                    />
                  </Link>
                </div>
              )
            })
          ) : (
            <div className="px-6 py-4 text-sm text-muted text-center">
              No books found
            </div>
          )}
        </div>
      </div>

      {/* Chapters dropdown - positioned next to hovered book */}
      {hoveredBook && book && book.chapters.length >= 1 && (
        <div
          className={`absolute z-[60] ${locale === 'he' ? 'right-full pr-2' : 'left-full pl-2'}`}
          style={{ top: hoveredBookTop }}
          onMouseEnter={() => setHoveredBook(hoveredBook)}
        >
          <ChaptersDropdown
            chapters={book.chapters}
            bookName={hoveredBook}
            isOpen={true}
            onClose={() => setHoveredBook(null)}
            onCloseAll={onClose}
          />
        </div>
      )}

      {/* Loading indicator */}
      {isLoading && (
        <div
          className={`absolute z-[60] ${locale === 'he' ? 'right-full pr-2' : 'left-full pl-2'}`}
          style={{ top: hoveredBookTop }}
        >
          <div className="dropdown-panel px-6 py-4 text-sm text-secondary min-w-[150px] flex items-center gap-3">
            <LoadingSpinner className="text-muted" />
            <span>Loading...</span>
          </div>
        </div>
      )}

      {/* Book not available message */}
      {bookNotAvailable && (
        <div
          className={`absolute z-[60] ${locale === 'he' ? 'right-full pr-2' : 'left-full pl-2'}`}
          style={{ top: hoveredBookTop }}
        >
          <div className="dropdown-panel px-6 py-4 text-sm text-muted min-w-[150px]">
            Coming soon
          </div>
        </div>
      )}
    </div>
  )
}

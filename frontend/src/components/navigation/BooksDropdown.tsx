'use client'

import { useState, useEffect, useRef } from 'react'
import {
  AVAILABLE_BOOKS,
  BOOK_DISPLAY_NAMES,
  loadBookClient,
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
  const containerRef = useRef<HTMLDivElement>(null)
  const pathname = usePathname()
  const locale = getLocaleFromPath(pathname)

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

  if (!isOpen) return null

  const book = hoveredBook ? loadedBooks[hoveredBook] : null
  const isLoading = hoveredBook && loadingBooks.has(hoveredBook)
  const hasLoadedBook = hoveredBook && hoveredBook in loadedBooks
  const bookNotAvailable = hasLoadedBook && !book

  return (
    <div
      ref={containerRef}
      className="relative min-w-[280px] z-50"
      onMouseLeave={() => {
        setHoveredBook(null)
        setTimeout(() => onClose(), 200)
      }}
    >
      {/* Scrollable books list */}
      <div className="dropdown-panel max-h-[500px] overflow-y-auto py-1 scroll-smooth scroll-smooth-enhanced scrollbar-thin scrollbar-thumb-black/20 scrollbar-track-transparent hover:scrollbar-thumb-black/30">
        {AVAILABLE_BOOKS.map((bookName) => {
          const displayName = BOOK_DISPLAY_NAMES[bookName]
          const isHovered = hoveredBook === bookName

          return (
            <div
              key={bookName}
              onMouseEnter={(e) => handleBookHover(bookName, e.currentTarget)}
            >
              <Link
                href={`/${locale}/book/${bookName}/chapter/1`}
                className={`flex items-center justify-between px-6 py-3 text-base font-ui-latin font-semibold text-black/90 hover:text-black hover:bg-black/5 transition-all border-b border-black/8 last:border-b-0 ${
                  isHovered ? 'bg-black/5 text-black' : ''
                } ${locale === 'he' ? 'flex-row-reverse' : ''}`}
                onClick={onClose}
              >
                <span>
                  {displayName[locale as 'he' | 'es' | 'en'] || displayName.en}
                </span>
                <ChevronRight
                  className={`text-gray/60 ${locale === 'he' ? 'scale-x-[-1]' : ''}`}
                />
              </Link>
            </div>
          )
        })}
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
          <div className="dropdown-panel px-6 py-4 text-sm text-black/70 min-w-[150px] flex items-center gap-3">
            <LoadingSpinner className="text-black/50" />
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
          <div className="dropdown-panel px-6 py-4 text-sm text-black/60 min-w-[150px]">
            Coming soon
          </div>
        </div>
      )}
    </div>
  )
}

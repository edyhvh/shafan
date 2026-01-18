'use client'

import { useState, useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
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
  isMobile?: boolean
}

export default function BooksDropdown({
  isOpen,
  onClose,
  isMobile = false,
}: BooksDropdownProps) {
  const [hoveredBook, setHoveredBook] = useState<BookName | null>(null)
  const [selectedBook, setSelectedBook] = useState<BookName | null>(null) // For sequential flow (mobile and desktop)
  const [hoveredBookTop, setHoveredBookTop] = useState<number>(0)
  const [mounted, setMounted] = useState(false)
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

  useEffect(() => {
    setMounted(true)
  }, [])

  // Reset selected book and hovered book when dropdown closes
  useEffect(() => {
    if (!isOpen) {
      setSelectedBook(null)
      setHoveredBook(null)
      setSearchQuery('')
    }
  }, [isOpen])

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

  // Load book on selection or hover (hover preloads for faster selection)
  useEffect(() => {
    // Priority: selected book, then hovered book (for preloading)
    const bookToLoad = selectedBook || (!isMobile ? hoveredBook : null)
    if (
      bookToLoad &&
      !(bookToLoad in loadedBooks) &&
      !loadingBooks.has(bookToLoad)
    ) {
      setLoadingBooks((prev) => new Set(prev).add(bookToLoad))

      loadBookClient(bookToLoad).then((book) => {
        // Store the result (even if null) to indicate loading is complete
        setLoadedBooks((prev) => ({ ...prev, [bookToLoad]: book }))
        setLoadingBooks((prev) => {
          const next = new Set(prev)
          next.delete(bookToLoad)
          return next
        })
      })
    }
  }, [selectedBook, hoveredBook, loadedBooks, loadingBooks, isMobile])

  // Clear timeout on unmount
  useEffect(() => {
    return () => {
      if (closeTimeoutRef.current) {
        clearTimeout(closeTimeoutRef.current)
      }
    }
  }, [])

  if (!isOpen) return null

  const book = selectedBook ? loadedBooks[selectedBook] : null
  const isLoading = selectedBook && loadingBooks.has(selectedBook)
  const hasLoadedBook = selectedBook && selectedBook in loadedBooks
  const bookNotAvailable = hasLoadedBook && !book

  // If book is selected, show chapters instead of books (both mobile and desktop)
  const showChapters = selectedBook && book

  const handleMouseLeave = () => {
    // Only clear hovered book if no book is selected (to allow navigation)
    if (!selectedBook) {
      setHoveredBook(null)
    }
    // On desktop, don't manage closing here - let Navbar handle it
    // On mobile, we can still manage it
    if (isMobile) {
      // Clear any existing timeout
      if (closeTimeoutRef.current) {
        clearTimeout(closeTimeoutRef.current)
      }
      // Set a new timeout to close (only if no book is selected)
      if (!selectedBook) {
        closeTimeoutRef.current = setTimeout(() => {
          onClose()
        }, 200)
      }
    }
  }

  const handleMouseEnter = () => {
    // Cancel any pending close when mouse enters dropdown
    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current)
      closeTimeoutRef.current = null
    }
  }

  // Dropdown content
  const dropdownContent = (
    <div
      ref={containerRef}
      className={`books-dropdown-container ${isMobile ? '' : 'relative'} min-w-[280px] ${isMobile ? 'z-10' : 'z-50'}`}
      onMouseEnter={isMobile ? handleMouseEnter : undefined}
      onMouseLeave={isMobile ? handleMouseLeave : undefined}
      onClick={(e) => {
        // Prevent clicks inside dropdown from closing parent menus
        e.stopPropagation()
      }}
    >
        {/* Dropdown panel with search and books list */}
        <div
          className={`dropdown-panel ${isMobile ? 'max-h-[85vh] flex flex-col' : 'max-h-[600px] flex flex-col'}`}
        >
          {/* Search input - only show when not showing chapters */}
          {!showChapters && (
            <div
              className={`p-2 border-b border-black/5 ${isMobile ? 'flex-shrink-0' : 'flex-shrink-0'}`}
            >
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
          )}

          {/* Scrollable books list or chapters */}
          <div
            className={`flex-1 overflow-y-auto min-h-0 py-1 scroll-smooth scroll-smooth-enhanced scrollbar-thin scrollbar-thumb-black/20 scrollbar-track-transparent hover:scrollbar-thumb-black/30 relative`}
          >
            {showChapters ? (
              // Show chapters for selected book (both mobile and desktop)
              <div
                key={`chapters-${selectedBook}`}
                className={`${locale === 'he' ? 'slide-in-from-left' : 'slide-in-from-right'}`}
              >
                <button
                  onClick={() => setSelectedBook(null)}
                  className="w-full text-left px-6 py-3 text-sm font-medium text-muted hover:text-primary transition-all border-b border-primary/8 flex items-center gap-2"
                >
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path d="M19 12H5M12 19l-7-7 7-7" />
                  </svg>
                  {locale === 'he' ? 'חזור' : 'Back'}
                </button>
                {book && book.chapters.length > 0 ? (
                  <ChaptersDropdown
                    chapters={book.chapters}
                    bookName={selectedBook!}
                    isOpen={true}
                    onClose={() => setSelectedBook(null)}
                    onCloseAll={onClose}
                    isMobile={isMobile}
                  />
                ) : (
                  <div className="px-6 py-4 text-sm text-muted text-center">
                    {isLoading ? 'Loading...' : 'No chapters available'}
                  </div>
                )}
              </div>
            ) : (
              // Show books list
              <div
                key="books-list"
                className={`${locale === 'he' ? 'slide-in-from-right' : 'slide-in-from-left'}`}
              >
                {filteredBooks.length > 0 ? filteredBooks.map((bookName) => {
                const displayName = BOOK_DISPLAY_NAMES[bookName]
                const isHovered = hoveredBook === bookName
                const isSelected = selectedBook === bookName

                const handleBookClick = (e: React.MouseEvent) => {
                  e.preventDefault()
                  setSelectedBook(bookName)
                  setHoveredBook(null) // Clear hover state when selecting
                }

                return (
                  <div
                    key={bookName}
                    onMouseEnter={(e) =>
                      !isMobile && handleBookHover(bookName, e.currentTarget)
                    }
                  >
                    <Link
                      href={`/${locale}/book/${bookName}/chapter/1`}
                      className={`flex items-center justify-between px-6 py-3 text-base font-ui-latin font-semibold text-primary hover:bg-primary/5 transition-all border-b border-primary/8 last:border-b-0 ${
                        isHovered || isSelected ? 'bg-primary/5' : ''
                      } ${locale === 'he' ? 'flex-row-reverse' : ''}`}
                      onClick={handleBookClick}
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
            }) : (
              <div className="px-6 py-4 text-sm text-muted text-center">
                No books found
              </div>
            )}
              </div>
            )}
          </div>
        </div>

      {/* Loading indicator - show in main container when loading */}
      {isLoading && !showChapters && (
        <div className="px-6 py-4 text-sm text-muted text-center flex items-center justify-center gap-3">
          <LoadingSpinner className="text-muted" />
          <span>Loading...</span>
        </div>
      )}

      {/* Book not available message - show in main container */}
      {bookNotAvailable && !showChapters && (
        <div className="px-6 py-4 text-sm text-muted text-center">
          Coming soon
        </div>
      )}
    </div>
  )

  // On mobile, render in portal centered on screen; on desktop, render normally
  if (isMobile && mounted) {
    return createPortal(
      <div
        className="fixed top-24 left-0 right-0 bottom-0 z-[1000]"
        onClick={(e) => {
          // Close if clicking backdrop
          if (e.target === e.currentTarget) {
            onClose()
          }
        }}
      >
        {/* Backdrop - covers the entire modal area */}
        <div className="absolute inset-0 bg-black/50 backdrop-blur-sm animate-in fade-in duration-300" />

        {/* Dropdown content - centered in the modal area */}
        <div
          className="relative z-10 flex justify-center items-start pt-4 px-4 h-full animate-in fade-in slide-in-from-top-4 duration-300 ease-out"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="w-full max-w-md max-h-full">{dropdownContent}</div>
        </div>
      </div>,
      document.body
    )
  }

  // Desktop: render normally
  return dropdownContent
}

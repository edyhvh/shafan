'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { searchBooks, BOOK_DISPLAY_NAMES, type BookName } from '@/lib/books'
import { getLocaleFromPath } from '@/lib/locale'
import { useClickOutside } from '@/hooks/useClickOutside'

export default function Search() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<BookName[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const searchRef = useRef<HTMLDivElement>(null)
  const router = useRouter()
  const pathname = usePathname()
  const locale = getLocaleFromPath(pathname)

  useEffect(() => {
    if (query.trim()) {
      const searchResults = searchBooks(query)
      setResults(searchResults)
      setIsOpen(true)
    } else {
      setResults([])
      setIsOpen(false)
    }
  }, [query])

  useClickOutside(searchRef, () => setIsOpen(false), isOpen)

  const handleBookSelect = (bookName: BookName) => {
    setQuery('')
    setIsOpen(false)
    router.push(`/${locale}/book/${bookName}/chapter/1`)
  }

  return (
    <div className="relative" ref={searchRef}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => query.trim() && setIsOpen(true)}
        placeholder="Search books..."
        className="w-full px-0 py-2 text-base font-ui-latin text-primary bg-transparent border-b border-primary/20 focus:outline-none focus:border-primary/40 transition-colors placeholder:text-secondary/50"
      />
      {isOpen && results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 dropdown-panel max-h-80 overflow-y-auto z-50 rounded-sm">
          {results.map((bookName) => {
            const displayName = BOOK_DISPLAY_NAMES[bookName]
            return (
              <button
                key={bookName}
                onClick={() => handleBookSelect(bookName)}
                className="w-full text-left px-6 py-3 text-base font-ui-latin text-primary hover:bg-primary/5 transition-colors border-b border-primary/5 last:border-b-0"
              >
                <div className="font-medium">
                  {displayName[locale as 'he' | 'es' | 'en'] || displayName.en}
                </div>
                <div className="text-sm text-muted mt-1">{bookName}</div>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

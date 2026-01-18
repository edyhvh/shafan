'use client'

import { Chapter } from '@/lib/types'
import { useState, useEffect } from 'react'
import VersesDropdown from './VersesDropdown'
import { usePathname } from 'next/navigation'
import { getLocaleFromPath } from '@/lib/locale'

interface ChaptersDropdownProps {
  chapters: Chapter[]
  bookName: string
  isOpen: boolean
  onClose: () => void
  onCloseAll?: () => void
  isMobile?: boolean
}

export default function ChaptersDropdown({
  chapters,
  bookName,
  isOpen,
  onClose,
  onCloseAll,
  isMobile = false,
}: ChaptersDropdownProps) {
  const [selectedChapter, setSelectedChapter] = useState<number | null>(null)
  const pathname = usePathname()
  const locale = getLocaleFromPath(pathname)

  // Reset selected chapter when dropdown closes
  useEffect(() => {
    if (!isOpen) {
      setSelectedChapter(null)
    }
  }, [isOpen])

  if (!isOpen) return null

  const chapter = selectedChapter
    ? chapters.find((c) => c.number === selectedChapter)
    : null

  // If no chapters, show message
  if (!chapters || chapters.length === 0) {
    return (
      <div className="dropdown-panel z-[60] p-4">
        <span className="text-sm text-black/60">No chapters</span>
      </div>
    )
  }

  // Calculate grid columns based on number of chapters
  const gridCols =
    chapters.length === 1
      ? 1
      : chapters.length <= 4
        ? 2
        : chapters.length <= 9
          ? 3
          : chapters.length <= 16
            ? 4
            : 5

  // For single chapter books, just show link without verse selection
  const isSingleChapter = chapters.length === 1

  const handleChapterClick = (e: React.MouseEvent, chapterNumber: number) => {
    e.preventDefault()
    e.stopPropagation()

    if (isSingleChapter) {
      // Single chapter: navigate directly and close all dropdowns
      onCloseAll?.()
      return
    }

    // Multi-chapter: always show verses (both mobile and desktop)
    setSelectedChapter(chapterNumber)
  }

  // On mobile or desktop, if chapter is selected, show only verses; otherwise show chapters
  if (selectedChapter && chapter) {
    return (
      <div className="relative dropdown-panel z-[60] p-3">
        {/* Back button */}
        <button
          onClick={() => setSelectedChapter(null)}
          className="mb-3 text-sm text-muted hover:text-primary transition-all flex items-center gap-2"
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
          {locale === 'he' ? 'חזור לפרקים' : 'Back to chapters'}
        </button>

        {/* Verses only */}
        {chapter.verses && chapter.verses.length > 0 ? (
          <VersesDropdown
            verses={chapter.verses}
            bookName={bookName}
            chapterNumber={chapter.number}
            isOpen={true}
            onClose={() => setSelectedChapter(null)}
            onCloseAll={() => {
              onClose()
              onCloseAll?.()
            }}
            isMobile={isMobile}
          />
        ) : (
          <div className="p-4 text-sm text-muted">
            {locale === 'he' ? 'אין פסוקים זמינים' : 'No verses available'}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="relative dropdown-panel z-[60] p-3">
      {/* Grid of chapters */}
      <div
        className="grid gap-2"
        style={{ gridTemplateColumns: `repeat(${gridCols}, 1fr)` }}
      >
        {chapters.map((ch) => {
          const isSelected = selectedChapter === ch.number

          return (
            <button
              key={ch.number}
              className={`flex items-center justify-center w-10 h-10 text-sm font-semibold transition-all duration-150 rounded-lg cursor-pointer ${
                isSelected
                  ? 'bg-gray text-white scale-105 shadow-md'
                  : 'bg-black/5 text-black hover:bg-black/30 hover:text-black hover:scale-110 hover:shadow-sm hover:animate-pulse-subtle active:scale-95'
              } ${locale === 'he' ? 'font-ui-hebrew' : 'font-ui-latin'}`}
              onClick={(e) => handleChapterClick(e, ch.number)}
            >
              {locale === 'he' ? ch.hebrew_letter : ch.number}
            </button>
          )
        })}
      </div>
    </div>
  )
}

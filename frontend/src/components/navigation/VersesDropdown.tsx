'use client'

import { Verse } from '@/lib/types'
import { usePathname, useRouter } from 'next/navigation'
import { getLocaleFromPath } from '@/lib/locale'
import { scrollToVerse } from '@/lib/smooth-scroll'

interface VersesDropdownProps {
  verses: Verse[]
  bookName: string
  chapterNumber: number
  isOpen: boolean
  onClose: () => void
  onCloseAll?: () => void
  isMobile?: boolean
}

export default function VersesDropdown({
  verses,
  bookName,
  chapterNumber,
  isOpen,
  onClose,
  onCloseAll,
}: VersesDropdownProps) {
  const pathname = usePathname()
  const router = useRouter()
  const locale = getLocaleFromPath(pathname)

  // Check if we're already on the target chapter page
  const currentChapterPath = `/${locale}/book/${bookName}/chapter/${chapterNumber}`
  const isOnCurrentChapter = pathname === currentChapterPath

  if (!isOpen) return null

  // If no verses, show message
  if (!verses || verses.length === 0) {
    return (
      <div className="dropdown-panel z-[70] p-4">
        <span className="text-sm text-black/60">No verses</span>
      </div>
    )
  }

  // Calculate grid columns - limit to 4 max for better height distribution
  const gridCols = verses.length <= 4 ? 2 : verses.length <= 9 ? 3 : 4

  // Calculate max height - taller for more verses to create rectangular shape
  const maxHeight =
    verses.length > 16 ? '400px' : verses.length > 9 ? '350px' : '300px'

  const handleVerseClick = (verseNumber: number) => {
    onClose()
    onCloseAll?.()

    if (isOnCurrentChapter) {
      // Already on the page, scroll immediately
      // Use a small delay to ensure dropdown closes first
      setTimeout(() => {
        scrollToVerse(verseNumber, 128)
      }, 150)
    } else {
      // Navigate to the chapter page with hash
      // The ChapterContent component will handle scrolling via useEffect
      router.push(`${currentChapterPath}#verse-${verseNumber}`)
    }
  }

  return (
    <div className="dropdown-panel z-[70] p-3">
      <div
        className="grid gap-2 overflow-y-auto scrollbar-thin scrollbar-thumb-black/20 scrollbar-track-transparent"
        style={{
          gridTemplateColumns: `repeat(${gridCols}, 1fr)`,
          maxHeight: maxHeight,
        }}
      >
        {verses.map((verse) => (
          <button
            key={verse.number}
            onClick={() => handleVerseClick(verse.number)}
            className="flex items-center justify-center w-9 h-9 text-xs font-ui-latin font-medium text-black bg-black/[0.04] hover:bg-black/[0.08] hover:scale-105 active:scale-95 transition-all duration-200 rounded-lg cursor-pointer hover:shadow-sm"
          >
            {verse.number}
          </button>
        ))}
      </div>
    </div>
  )
}

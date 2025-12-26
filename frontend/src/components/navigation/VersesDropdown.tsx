'use client'

import { Verse } from '@/lib/types'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { getLocaleFromPath } from '@/lib/locale'

interface VersesDropdownProps {
  verses: Verse[]
  bookName: string
  chapterNumber: number
  isOpen: boolean
  onClose: () => void
  onCloseAll?: () => void
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
  const locale = getLocaleFromPath(pathname)

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
          <Link
            key={verse.number}
            href={`/${locale}/book/${bookName}/chapter/${chapterNumber}#verse-${verse.number}`}
            className="flex items-center justify-center w-9 h-9 text-xs font-ui-latin font-medium text-black bg-black/5 hover:bg-black/10 hover:scale-105 active:scale-95 transition-all duration-150 rounded-lg"
            onClick={() => {
              onClose()
              onCloseAll?.()
            }}
          >
            {verse.number}
          </Link>
        ))}
      </div>
    </div>
  )
}

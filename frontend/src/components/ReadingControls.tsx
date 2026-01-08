'use client'

import { useNikud } from '@/hooks/useNikud'
import { useTextSource } from '@/hooks/useTextSource'
import { usePathname } from 'next/navigation'
import { isNewTestament, AVAILABLE_BOOKS, type BookName } from '@/lib/books'
import TextSourceToggle from './TextSourceToggle'

/**
 * Component for reading controls (nikud and text source toggles)
 * Positioned as floating controls in the top right
 */
export default function ReadingControls() {
  const { nikudEnabled, toggleNikud } = useNikud()
  const { textSource, toggleTextSource } = useTextSource()
  const pathname = usePathname()

  // Extract bookId from pathname to check if it's New Testament
  const pathParts = pathname.split('/')
  const bookIndex = pathParts.indexOf('book')
  const bookId =
    bookIndex !== -1 && pathParts[bookIndex + 1]
      ? pathParts[bookIndex + 1]
      : null
  const bookName =
    bookId && AVAILABLE_BOOKS.includes(bookId as BookName)
      ? (bookId as BookName)
      : null
  const showTextSourceToggle = bookName && isNewTestament(bookName)

  return (
    <>
      {/* Text Source Toggle (Hutter/Delitzsch) - Only for New Testament */}
      {showTextSourceToggle && (
        <TextSourceToggle
          enabled={textSource === 'hutter'}
          onToggle={toggleTextSource}
          position="top-6 right-5"
        />
      )}

      {/* Nikud Button - Always shown, positioned below text source toggle if both are visible */}
      <div
        className={`fixed ${showTextSourceToggle ? 'top-[72px]' : 'top-6'} right-5 z-40 flex flex-col items-center gap-0.5`}
      >
        <button
          onClick={toggleNikud}
          className="cursor-pointer group relative"
          aria-label="Toggle nikud (vowel points)"
          aria-pressed={nikudEnabled}
          title="Toggle nikud"
        >
          {/* Outer ring/border */}
          <div
            className={`
              w-[36px] h-[36px]
              rounded-full
              border-[2.5px]
              transition-all duration-300 ease-out
              ${
                nikudEnabled
                  ? 'bg-gray border-gray shadow-[inset_0_2px_4px_rgba(0,0,0,0.2)]'
                  : 'bg-white border-gray/30 group-hover:border-gray/50 shadow-[0_2px_8px_rgba(0,0,0,0.1)]'
              }
            `}
          >
            {/* Inner circle - power symbol */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div
                className={`
                  w-[14px] h-[14px]
                  rounded-full
                  transition-all duration-300 ease-out
                  ${
                    nikudEnabled
                      ? 'bg-white/90'
                      : 'bg-gray/40 group-hover:bg-gray/60'
                  }
                `}
              />
            </div>
          </div>
        </button>
        {/* Label below button */}
        <span className="text-[10px] font-ui-hebrew font-bold text-gray/80 select-none">
          נקוד
        </span>
      </div>
    </>
  )
}

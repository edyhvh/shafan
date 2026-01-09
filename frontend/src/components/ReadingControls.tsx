'use client'

import { useNikud } from '@/hooks/useNikud'
import { useCantillation } from '@/hooks/useCantillation'
import { useTextSource } from '@/hooks/useTextSource'
import { useSefer } from '@/hooks/useSefer'
import { usePathname } from 'next/navigation'
import { isNewTestament, AVAILABLE_BOOKS, type BookName } from '@/lib/books'
import TextSourceToggle from './TextSourceToggle'

/**
 * Component for reading controls (nikud and text source toggles)
 * Positioned as floating controls in the top right
 */
export default function ReadingControls() {
  const { nikudEnabled, toggleNikud } = useNikud()
  const { cantillationEnabled, toggleCantillation } = useCantillation()
  const { textSource, toggleTextSource } = useTextSource()
  const { seferEnabled, toggleSefer } = useSefer()
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
  const showCantillationToggle = bookName && !isNewTestament(bookName)

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
        className={`fixed ${showTextSourceToggle ? 'top-[72px]' : 'top-6'} right-5 z-40 flex flex-col items-center gap-1`}
      >
        <button
          onClick={toggleNikud}
          className="cursor-pointer group relative"
          aria-label="Toggle nikud (vowel points)"
          aria-pressed={nikudEnabled}
          title="Toggle nikud"
        >
          {/* Neumorphic outer ring */}
          <div
            className={`
              w-[40px] h-[40px]
              rounded-full
              transition-all duration-300 ease-out
              bg-background
              group-hover:scale-105
              ${
                nikudEnabled
                  ? 'shadow-[inset_4px_4px_8px_rgba(180,160,140,0.5),inset_-4px_-4px_8px_rgba(255,255,255,1)] group-hover:shadow-[inset_3px_3px_6px_rgba(180,160,140,0.4),inset_-3px_-3px_6px_rgba(255,255,255,0.95)]'
                  : 'shadow-[6px_6px_12px_rgba(180,160,140,0.5),-6px_-6px_12px_rgba(255,255,255,1)] group-hover:shadow-[8px_8px_16px_rgba(180,160,140,0.6),-8px_-8px_16px_rgba(255,255,255,1)]'
              }
            `}
          >
            {/* Inner circle - dark when ON */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div
                className={`
                  w-[16px] h-[16px]
                  rounded-full
                  transition-all duration-300 ease-out
                  group-hover:scale-110
                  ${
                    nikudEnabled
                      ? 'bg-gray shadow-[inset_1px_1px_2px_rgba(0,0,0,0.3)] group-hover:shadow-[inset_1px_1px_3px_rgba(0,0,0,0.4)]'
                      : 'bg-background shadow-[inset_2px_2px_4px_rgba(180,160,140,0.4),inset_-2px_-2px_4px_rgba(255,255,255,0.9)] group-hover:shadow-[inset_2px_2px_5px_rgba(180,160,140,0.5),inset_-2px_-2px_5px_rgba(255,255,255,1)]'
                  }
                `}
              />
            </div>
          </div>
        </button>
        {/* Label below button */}
        <span className="text-[10px] font-ui-hebrew font-bold text-gray/70 select-none">
          נקוד
        </span>
      </div>

      {/* Cantillation Button - Only shown for Tanaj books, positioned below sefer button */}
      {showCantillationToggle && (
        <div
          className={`fixed ${showTextSourceToggle ? 'top-[200px]' : 'top-[154px]'} right-5 z-40 flex flex-col items-center gap-1`}
        >
          <button
            onClick={toggleCantillation}
            className="cursor-pointer group relative"
            aria-label="Toggle cantillation marks"
            aria-pressed={cantillationEnabled}
            title="Toggle cantillation marks"
          >
            {/* Neumorphic outer ring */}
            <div
              className={`
                w-[40px] h-[40px]
                rounded-full
                transition-all duration-300 ease-out
                bg-background
                group-hover:scale-105
                ${
                  cantillationEnabled
                    ? 'shadow-[inset_4px_4px_8px_rgba(180,160,140,0.5),inset_-4px_-4px_8px_rgba(255,255,255,1)] group-hover:shadow-[inset_3px_3px_6px_rgba(180,160,140,0.4),inset_-3px_-3px_6px_rgba(255,255,255,0.95)]'
                    : 'shadow-[6px_6px_12px_rgba(180,160,140,0.5),-6px_-6px_12px_rgba(255,255,255,1)] group-hover:shadow-[8px_8px_16px_rgba(180,160,140,0.6),-8px_-8px_16px_rgba(255,255,255,1)]'
                }
              `}
            >
              {/* Inner circle - dark when ON */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div
                  className={`
                    w-[16px] h-[16px]
                    rounded-full
                    transition-all duration-300 ease-out
                    group-hover:scale-110
                    ${
                      cantillationEnabled
                        ? 'bg-gray shadow-[inset_1px_1px_2px_rgba(0,0,0,0.3)] group-hover:shadow-[inset_1px_1px_3px_rgba(0,0,0,0.4)]'
                        : 'bg-background shadow-[inset_2px_2px_4px_rgba(180,160,140,0.4),inset_-2px_-2px_4px_rgba(255,255,255,0.9)] group-hover:shadow-[inset_2px_2px_5px_rgba(180,160,140,0.5),inset_-2px_-2px_5px_rgba(255,255,255,1)]'
                    }
                  `}
                />
              </div>
            </div>
          </button>
          {/* Label below button */}
          <span className="text-[10px] font-ui-hebrew font-bold text-gray/70 select-none">
            טעמים
          </span>
        </div>
      )}

      {/* Sefer Button - Always shown, positioned below nikud button */}
      <div
        className={`fixed ${showTextSourceToggle ? 'top-[140px]' : 'top-[94px]'} right-5 z-40 flex flex-col items-center gap-1`}
      >
        <button
          onClick={toggleSefer}
          className="cursor-pointer group relative"
          aria-label="Toggle sefer (continuous paragraph) display"
          aria-pressed={seferEnabled}
          title="Toggle sefer (continuous text) display"
        >
          {/* Neumorphic outer ring */}
          <div
            className={`
              w-[40px] h-[40px]
              rounded-full
              transition-all duration-300 ease-out
              bg-background
              group-hover:scale-105
              ${
                seferEnabled
                  ? 'shadow-[inset_4px_4px_8px_rgba(180,160,140,0.5),inset_-4px_-4px_8px_rgba(255,255,255,1)] group-hover:shadow-[inset_3px_3px_6px_rgba(180,160,140,0.4),inset_-3px_-3px_6px_rgba(255,255,255,0.95)]'
                  : 'shadow-[6px_6px_12px_rgba(180,160,140,0.5),-6px_-6px_12px_rgba(255,255,255,1)] group-hover:shadow-[8px_8px_16px_rgba(180,160,140,0.6),-8px_-8px_16px_rgba(255,255,255,1)]'
              }
            `}
          >
            {/* Inner circle - dark when ON */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div
                className={`
                  w-[16px] h-[16px]
                  rounded-full
                  transition-all duration-300 ease-out
                  group-hover:scale-110
                  ${
                    seferEnabled
                      ? 'bg-gray shadow-[inset_1px_1px_2px_rgba(0,0,0,0.3)] group-hover:shadow-[inset_1px_1px_3px_rgba(0,0,0,0.4)]'
                      : 'bg-background shadow-[inset_2px_2px_4px_rgba(180,160,140,0.4),inset_-2px_-2px_4px_rgba(255,255,255,0.9)] group-hover:shadow-[inset_2px_2px_5px_rgba(180,160,140,0.5),inset_-2px_-2px_5px_rgba(255,255,255,1)]'
                  }
                `}
              />
            </div>
          </div>
        </button>
        {/* Label below button */}
        <span className="text-[10px] font-ui-hebrew font-bold text-gray/70 select-none">
          ספר
        </span>
      </div>
    </>
  )
}

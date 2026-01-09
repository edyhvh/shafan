'use client'

import dynamic from 'next/dynamic'
import {
  removeNikud,
  removeCantillation,
  removeWordSeparators,
} from '@/lib/hebrew'
import { useNikud } from '@/hooks/useNikud'
import { useCantillation } from '@/hooks/useCantillation'
import { useTextSource } from '@/hooks/useTextSource'
import { useSefer } from '@/hooks/useSefer'
import { type BookName } from '@/lib/books'
import type { Verse } from '@/lib/types'

// Dynamically import ReadingControls with SSR disabled to prevent hydration issues
const ReadingControls = dynamic(() => import('./ReadingControls'), {
  ssr: false,
  loading: () => null,
})

interface ChapterContentProps {
  hebrewLetter: string
  verses: Verse[]
  bookName: BookName
}

export default function ChapterContent({
  hebrewLetter,
  verses,
  bookName: _bookName,
}: ChapterContentProps) {
  const { nikudEnabled, isLoaded: nikudLoaded } = useNikud()
  const { cantillationEnabled, isLoaded: cantillationLoaded } =
    useCantillation()
  const { textSource, isLoaded: textSourceLoaded } = useTextSource()
  const { seferEnabled, isLoaded: seferLoaded } = useSefer()

  // Wait for all preference hooks to be loaded before rendering to prevent hydration mismatches
  const allPreferencesLoaded =
    nikudLoaded && cantillationLoaded && textSourceLoaded && seferLoaded

  const getDisplayText = (verse: Verse): string => {
    // Select text source: Hutter (text_nikud) or Delitzsch (text_nikud_delitzsch)
    const sourceText =
      textSource === 'delitzsch' && verse.text_nikud_delitzsch
        ? verse.text_nikud_delitzsch
        : verse.text_nikud

    if (!sourceText) return 'No text available'

    // Always remove word separators first
    let displayText = removeWordSeparators(sourceText)

    // Apply cantillation filtering first (before nikud) to preserve correct order
    // Cantillation marks should be removed before nikud marks for proper rendering
    if (!cantillationEnabled) {
      displayText = removeCantillation(displayText)
    }

    // Apply nikud filtering after cantillation
    if (!nikudEnabled) {
      displayText = removeNikud(displayText)
    }

    return displayText
  }

  return (
    <>
      <ReadingControls />

      <div className="mb-12">
        <h2 className="font-bible-hebrew text-[64px] text-center mb-8 text-black">
          {hebrewLetter}
        </h2>

        <div className={seferEnabled ? '' : 'space-y-8'} dir="rtl">
          {seferEnabled ? (
            // Sefer mode: continuous paragraph display
            <p className="font-bible-hebrew text-[32px] md:text-[36px] leading-[1.9] text-black">
              {verses.map((verse, index) => (
                <span
                  key={verse.number}
                  id={`verse-${verse.number}`}
                  className="scroll-mt-32 target:bg-amber-100/50 target:rounded target:px-1 transition-colors duration-500"
                >
                  {verse.number > 0 && (
                    <span className="text-gray/60 font-ui-latin text-base ml-2">
                      {verse.number}
                    </span>
                  )}
                  <span className="font-bible-hebrew">
                    {allPreferencesLoaded ? getDisplayText(verse) : '...'}
                  </span>
                  {index < verses.length - 1 && ' '}
                </span>
              ))}
            </p>
          ) : (
            // Standard mode: separate verse blocks
            verses.map((verse) => (
              <div
                key={verse.number}
                id={`verse-${verse.number}`}
                className="font-bible-hebrew text-[32px] md:text-[36px] leading-[1.9] text-black scroll-mt-32 target:bg-amber-100/50 target:rounded-lg target:px-4 target:-mx-4 transition-colors duration-500"
              >
                {verse.number > 0 && (
                  <span className="text-gray/60 font-ui-latin text-base ml-3">
                    {verse.number}
                  </span>
                )}
                <span className="font-bible-hebrew">
                  {allPreferencesLoaded ? getDisplayText(verse) : '...'}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  )
}

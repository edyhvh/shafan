'use client'

import { removeNikud, removeWordSeparators } from '@/lib/hebrew'
import { useNikud } from '@/hooks/useNikud'
import NikudToggle from './NikudToggle'
import type { Verse } from '@/lib/types'

interface ChapterContentProps {
  hebrewLetter: string
  verses: Verse[]
}

export default function ChapterContent({
  hebrewLetter,
  verses,
}: ChapterContentProps) {
  const { nikudEnabled, toggleNikud } = useNikud()

  const getDisplayText = (text: string): string => {
    if (!text) return 'No text available'
    const displayText = removeWordSeparators(text) // Always remove word separators
    return nikudEnabled ? displayText : removeNikud(displayText)
  }

  return (
    <>
      <NikudToggle enabled={nikudEnabled} onToggle={toggleNikud} />

      <div className="mb-12">
        <h2 className="font-bible-hebrew text-[64px] text-center mb-8 text-black">
          {hebrewLetter}
        </h2>

        <div className="space-y-8" dir="rtl">
          {verses.map((verse) => (
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
                {getDisplayText(verse.text_nikud)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}

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
import { getChristianVerse } from '@/lib/versification'
import { useEffect, useState } from 'react'
import { scrollToVerse } from '@/lib/smooth-scroll'

// Dynamically import ReadingControls with SSR disabled to prevent hydration issues
const ReadingControls = dynamic(() => import('./ReadingControls'), {
  ssr: false,
  loading: () => null,
})

interface ChapterContentProps {
  hebrewLetter: string
  verses: Verse[]
  bookName: BookName
  chapterNumber: number
}

export default function ChapterContent({
  hebrewLetter,
  verses,
  bookName: _bookName,
  chapterNumber,
}: ChapterContentProps) {
  const { nikudEnabled, isLoaded: nikudLoaded } = useNikud()
  const { cantillationEnabled, isLoaded: cantillationLoaded } =
    useCantillation()
  const { textSource, isLoaded: textSourceLoaded } = useTextSource()
  const { seferEnabled, isLoaded: seferLoaded } = useSefer()

  // State for Christian Bible verse mappings with optimized loading
  const [christianVerses, setChristianVerses] = useState<
    Record<number, string | null>
  >({})

  // Load Christian verse mappings - optimized to load all at once per chapter change
  useEffect(() => {
    async function loadChristianMappings() {
      // Load all mappings for the chapter in parallel instead of sequential
      const mappingPromises = verses.map(async (verse) => {
        if (verse.number > 0) {
          const christianRef = await getChristianVerse(
            _bookName,
            chapterNumber,
            verse.number
          )
          return [verse.number, christianRef] as [number, string | null]
        }
        return null
      })

      const results = await Promise.all(mappingPromises)
      const mappings: Record<number, string | null> = {}

      results.forEach((result) => {
        if (result) {
          const [verseNumber, christianRef] = result
          mappings[verseNumber] = christianRef
        }
      })

      setChristianVerses(mappings)
    }

    loadChristianMappings()
  }, [_bookName, chapterNumber, verses])

  // Wait for all preference hooks to be loaded before rendering to prevent hydration mismatches
  const allPreferencesLoaded =
    nikudLoaded && cantillationLoaded && textSourceLoaded && seferLoaded

  // Track highlighted verse for temporary highlight animation
  const [highlightedVerse, setHighlightedVerse] = useState<number | null>(null)

  // Listen for verse highlight events from scrollToVerse
  useEffect(() => {
    if (typeof window === 'undefined') return

    const handleVerseHighlight = (event: Event) => {
      const customEvent = event as CustomEvent<{ verseNumber: number }>
      const verseNumber = customEvent.detail?.verseNumber
      if (verseNumber) {
        setHighlightedVerse(verseNumber)
        // Remove highlight after animation completes
        setTimeout(() => {
          setHighlightedVerse(null)
        }, 1600) // 1.6 seconds to match animation duration
      }
    }

    window.addEventListener('verse-highlight', handleVerseHighlight)
    return () => window.removeEventListener('verse-highlight', handleVerseHighlight)
  }, [])

  // Handle hash scrolling when page loads with a verse hash (e.g., #verse-5)
  useEffect(() => {
    if (typeof window === 'undefined' || !allPreferencesLoaded) return

    const handleHashScroll = () => {
      const hash = window.location.hash
      if (hash && hash.startsWith('#verse-')) {
        const verseNumber = parseInt(hash.replace('#verse-', ''), 10)
        if (!isNaN(verseNumber) && verseNumber > 0) {
          // Delay to ensure content is rendered
          setTimeout(() => {
            scrollToVerse(verseNumber, 128)
            // Clear hash after scrolling to prevent persistent highlight
            window.history.replaceState(null, '', window.location.pathname)
          }, 300)
        }
      }
    }

    // Handle initial hash
    handleHashScroll()

    // Also handle hash changes (e.g., when navigating with browser back/forward)
    window.addEventListener('hashchange', handleHashScroll)
    return () => window.removeEventListener('hashchange', handleHashScroll)
  }, [chapterNumber, allPreferencesLoaded])

  // Component to display verse numbers with Christian equivalents
  const VerseNumber = ({
    verseNumber,
    className = '',
  }: {
    verseNumber: number
    className?: string
  }) => {
    const christianRef = christianVerses[verseNumber]

    return (
      <span
        className={`font-ui-latin text-base whitespace-nowrap ${className}`}
      >
        {christianRef && (
          <span className="text-muted">{'{' + christianRef + '}'}</span>
        )}
        {christianRef && <span className="mx-1"></span>}
        <span className={christianRef ? 'font-bold' : ''}>[{verseNumber}]</span>
      </span>
    )
  }

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
        <h2 className="font-bible-hebrew text-[64px] text-center mb-8 text-primary">
          {hebrewLetter}
        </h2>

        <div className={`${seferEnabled ? '' : 'space-y-8'}`} dir="rtl">
          {seferEnabled ? (
            // Sefer mode: continuous paragraph display
            <p className="font-bible-hebrew text-[32px] md:text-[36px] leading-[1.9] text-primary text-right">
              {verses.map((verse, index) => {
                const isHighlighted = highlightedVerse === verse.number
                return (
                  <span
                    key={verse.number}
                    id={`verse-${verse.number}`}
                    className={`scroll-mt-32 transition-all duration-500 ${
                      isHighlighted
                        ? 'verse-highlight-animate rounded px-1'
                        : ''
                    }`}
                  >
                    {verse.number > 0 && (
                      <VerseNumber
                        verseNumber={verse.number}
                        className="text-muted ml-2"
                      />
                    )}
                    <span className="font-bible-hebrew">
                      {allPreferencesLoaded ? getDisplayText(verse) : '...'}
                    </span>
                    {index < verses.length - 1 && ' '}
                  </span>
                )
              })}
            </p>
          ) : (
            // Standard mode: separate verse blocks
            verses.map((verse) => {
              const isHighlighted = highlightedVerse === verse.number
              return (
                <div
                  key={verse.number}
                  id={`verse-${verse.number}`}
                  className={`font-bible-hebrew text-[32px] md:text-[36px] leading-[1.9] text-primary text-right scroll-mt-32 transition-all duration-500 ${
                    isHighlighted
                      ? 'verse-highlight-animate rounded-lg px-4 -mx-4'
                      : ''
                  }`}
                >
                  {verse.number > 0 && (
                    <VerseNumber
                      verseNumber={verse.number}
                      className="text-muted ml-3"
                    />
                  )}
                  <span className="font-bible-hebrew">
                    {allPreferencesLoaded ? getDisplayText(verse) : '...'}
                  </span>
                </div>
              )
            })
          )}
        </div>
      </div>
    </>
  )
}

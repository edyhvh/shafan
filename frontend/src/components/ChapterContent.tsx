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
import { useTTH } from '@/hooks/useTTH'
import { type BookName } from '@/lib/books'
import type { Verse, TTHChapter, TTHFootnote } from '@/lib/types'
import { getChristianVerse } from '@/lib/versification'
import { useEffect, useState } from 'react'
import { scrollToVerse } from '@/lib/smooth-scroll'
import FootnoteTooltip from './FootnoteTooltip'
import { usePathname } from 'next/navigation'
import { getLocaleFromPath } from '@/lib/locale'
import { t } from '@/lib/translations'

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
  tthChapter?: TTHChapter | null
  tthAvailable?: boolean
}

export default function ChapterContent({
  hebrewLetter,
  verses,
  bookName: _bookName,
  chapterNumber,
  tthChapter,
  tthAvailable,
}: ChapterContentProps) {
  const { nikudEnabled, isLoaded: nikudLoaded } = useNikud()
  const { cantillationEnabled, isLoaded: cantillationLoaded } =
    useCantillation()
  const { textSource, isLoaded: textSourceLoaded } = useTextSource()
  const { seferEnabled, isLoaded: seferLoaded } = useSefer()
  const { tthEnabled, isLoaded: tthLoaded } = useTTH()
  const pathname = usePathname()
  const locale = getLocaleFromPath(pathname) as 'he' | 'es' | 'en'

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
    nikudLoaded &&
    cantillationLoaded &&
    textSourceLoaded &&
    seferLoaded &&
    tthLoaded

  // Determine if we're in TTH mode with data available
  // Gate on allPreferencesLoaded to prevent hydration mismatch (server always renders Hebrew)
  const showTTH =
    allPreferencesLoaded &&
    tthEnabled &&
    tthChapter &&
    tthChapter.verses.length > 0

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
    return () =>
      window.removeEventListener('verse-highlight', handleVerseHighlight)
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

  // Block rendering entirely when TTH is enabled but book is not available
  if (tthEnabled && !tthAvailable) {
    return (
      <section className="mb-12 pt-12">
        <div
          className="text-center text-muted text-base font-ui-latin px-4"
          dir="ltr"
        >
          {t('tth_book_unavailable_message', locale)}
        </div>
      </section>
    )
  }

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

  /**
   * Render TTH verse text with inline footnote tooltips
   */
  const renderTTHText = (
    tthText: string,
    footnotes: TTHFootnote[]
  ) => {
    if (!footnotes || footnotes.length === 0) {
      return <span dangerouslySetInnerHTML={{ __html: tthText }} />
    }

    // Split the text by footnote markers to insert tooltip components
    const parts: (
      | string
      | { type: 'footnote'; footnote: TTHFootnote }
    )[] = []
    let remaining = tthText

    // Sort footnotes by their position in the text (find each marker)
    const sortedFootnotes = [...footnotes].sort((a, b) => {
      const posA = tthText.indexOf(a.marker)
      const posB = tthText.indexOf(b.marker)
      return posA - posB
    })

    for (const fn of sortedFootnotes) {
      const idx = remaining.indexOf(fn.marker)
      if (idx !== -1) {
        if (idx > 0) {
          parts.push(remaining.slice(0, idx))
        }
        parts.push({ type: 'footnote', footnote: fn })
        remaining = remaining.slice(idx + fn.marker.length)
      }
    }
    if (remaining) {
      parts.push(remaining)
    }

    return (
      <>
        {parts.map((part, i) =>
          typeof part === 'string' ? (
            <span key={i} dangerouslySetInnerHTML={{ __html: part }} />
          ) : (
            <FootnoteTooltip key={`fn-${i}`} footnote={part.footnote} />
          )
        )}
      </>
    )
  }

  return (
    <section className="mb-12" aria-labelledby="chapter-hebrew-letter">
      <ReadingControls />

      <h2
        id="chapter-hebrew-letter"
        className="font-bible-hebrew text-[64px] text-center mb-8 text-primary"
      >
        {hebrewLetter}
      </h2>

      {/* TTH "not available" message for chapter */}
      {tthEnabled && !showTTH && tthAvailable && (
        <div
          className="text-center text-muted text-sm mb-6 font-ui-latin"
          dir="ltr"
        >
          {t('tth_not_available_chapter', locale)}
        </div>
      )}

      {/* TTH Spanish content */}
      {showTTH ? (
        <article className={`${seferEnabled ? '' : 'space-y-8'}`} dir="ltr">
          {seferEnabled ? (
            // Sefer mode: continuous paragraph display for TTH
            <p className="font-bible-hebrew text-[28px] md:text-[32px] leading-[2] text-primary text-left">
              {tthChapter.verses.map((tthVerse, index) => {
                const isHighlighted = highlightedVerse === tthVerse.verse
                const firstOccurrenceIndex = tthChapter.verses.findIndex(
                  (verse) => verse.verse === tthVerse.verse
                )
                const verseId =
                  firstOccurrenceIndex === index
                    ? `verse-${tthVerse.verse}`
                    : `verse-${tthVerse.verse}-${index}`
                return (
                  <span
                    key={`${tthVerse.verse}-${index}`}
                    id={verseId}
                    className={`scroll-mt-32 transition-all duration-500 ${
                      isHighlighted
                        ? 'verse-highlight-animate rounded px-1'
                        : ''
                    }`}
                  >
                    {tthVerse.verse > 0 && (
                      <span className="font-ui-latin text-base whitespace-nowrap text-muted mr-2">
                        [{tthVerse.verse}]
                      </span>
                    )}
                    <span className="font-ui-latin">
                      {allPreferencesLoaded
                        ? renderTTHText(tthVerse.tth, tthVerse.footnotes)
                        : '...'}
                    </span>
                    {index < tthChapter.verses.length - 1 && ' '}
                  </span>
                )
              })}
            </p>
          ) : (
            // Standard mode: separate verse blocks for TTH
            tthChapter.verses.map((tthVerse, index) => {
              const isHighlighted = highlightedVerse === tthVerse.verse
              const firstOccurrenceIndex = tthChapter.verses.findIndex(
                (verse) => verse.verse === tthVerse.verse
              )
              const verseId =
                firstOccurrenceIndex === index
                  ? `verse-${tthVerse.verse}`
                  : `verse-${tthVerse.verse}-${index}`
              return (
                <div
                  key={`${tthVerse.verse}-${index}`}
                  id={verseId}
                  className={`font-ui-latin text-[28px] md:text-[32px] leading-[2] text-primary text-left scroll-mt-32 transition-all duration-500 ${
                    isHighlighted
                      ? 'verse-highlight-animate rounded-lg px-4 -mx-4'
                      : ''
                  }`}
                >
                  {tthVerse.verse > 0 && (
                    <span className="font-ui-latin text-base whitespace-nowrap text-muted mr-3">
                      [{tthVerse.verse}]
                    </span>
                  )}
                  <span>
                    {allPreferencesLoaded
                      ? renderTTHText(tthVerse.tth, tthVerse.footnotes)
                      : '...'}
                  </span>
                </div>
              )
            })
          )}
        </article>
      ) : (
        /* Hebrew content (original) */
        <article className={`${seferEnabled ? '' : 'space-y-8'}`} dir="rtl">
          {seferEnabled ? (
            // Sefer mode: continuous paragraph display
            <p className="font-bible-hebrew text-[50px] md:text-[54px] leading-[1.9] text-primary text-right">
              {verses.map((verse, index) => {
                const isHighlighted = highlightedVerse === verse.number
                const firstOccurrenceIndex = verses.findIndex(
                  (entry) => entry.number === verse.number
                )
                const verseId =
                  firstOccurrenceIndex === index
                    ? `verse-${verse.number}`
                    : `verse-${verse.number}-${index}`
                return (
                  <span
                    key={`${verse.number}-${index}`}
                    id={verseId}
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
            verses.map((verse, index) => {
              const isHighlighted = highlightedVerse === verse.number
              const firstOccurrenceIndex = verses.findIndex(
                (entry) => entry.number === verse.number
              )
              const verseId =
                firstOccurrenceIndex === index
                  ? `verse-${verse.number}`
                  : `verse-${verse.number}-${index}`
              return (
                <div
                  key={`${verse.number}-${index}`}
                  id={verseId}
                  className={`font-bible-hebrew text-[50px] md:text-[54px] leading-[1.9] text-primary text-right scroll-mt-32 transition-all duration-500 ${
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
        </article>
      )}
    </section>
  )
}

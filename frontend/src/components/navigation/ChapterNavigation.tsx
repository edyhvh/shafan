'use client'

import Link from 'next/link'
import { useTTH } from '@/hooks/useTTH'

interface ChapterNavigationProps {
  locale: string
  bookName: string
  currentChapter: number
  totalChapters: number
  className?: string
}

export default function ChapterNavigation({
  locale,
  bookName,
  currentChapter,
  totalChapters,
  className = 'mb-8 flex justify-between items-center px-4 sm:px-8',
}: ChapterNavigationProps) {
  const { effectiveTTHEnabled } = useTTH()
  const isLTRNavigation = effectiveTTHEnabled

  // Navigation follows active reading mode: Hebrew mode is RTL, TTH mode is LTR.
  const prevArrow = isLTRNavigation ? '←' : '→'
  const nextArrow = isLTRNavigation ? '→' : '←'

  const prevLink =
    currentChapter > 1 ? (
      <Link
        href={`/${locale}/book/${bookName}/chapter/${currentChapter - 1}`}
        className="w-10 h-10 flex items-center justify-center text-lg font-ui-latin neumorphism transition-all duration-200"
        aria-label="Previous Chapter"
      >
        {prevArrow}
      </Link>
    ) : (
      <div className="w-10 h-10" />
    )

  const nextLink =
    currentChapter < totalChapters ? (
      <Link
        href={`/${locale}/book/${bookName}/chapter/${currentChapter + 1}`}
        className="w-10 h-10 flex items-center justify-center text-lg font-ui-latin neumorphism transition-all duration-200"
        aria-label="Next Chapter"
      >
        {nextArrow}
      </Link>
    ) : (
      <div className="w-10 h-10" />
    )

  return (
    <div className={className} dir="ltr">
      {isLTRNavigation ? prevLink : nextLink}
      {isLTRNavigation ? nextLink : prevLink}
    </div>
  )
}

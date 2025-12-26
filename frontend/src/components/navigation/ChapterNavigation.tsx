import Link from 'next/link'

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
  const isRTL = locale === 'he'
  const prevArrow = isRTL ? '→' : '←'
  const nextArrow = isRTL ? '←' : '→'

  return (
    <div className={className}>
      {currentChapter > 1 ? (
        <Link
          href={`/${locale}/book/${bookName}/chapter/${currentChapter - 1}`}
          className="w-10 h-10 flex items-center justify-center text-lg font-ui-latin border border-black/10 rounded-lg hover:bg-black/5 transition-colors"
          aria-label="Previous Chapter"
        >
          {prevArrow}
        </Link>
      ) : (
        <div className="w-10 h-10" />
      )}
      {currentChapter < totalChapters ? (
        <Link
          href={`/${locale}/book/${bookName}/chapter/${currentChapter + 1}`}
          className="w-10 h-10 flex items-center justify-center text-lg font-ui-latin border border-black/10 rounded-lg hover:bg-black/5 transition-colors"
          aria-label="Next Chapter"
        >
          {nextArrow}
        </Link>
      ) : (
        <div className="w-10 h-10" />
      )}
    </div>
  )
}

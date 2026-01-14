'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { getLocaleFromPath } from '@/lib/locale'
import { t } from '@/lib/translations'
import { useScrollState } from '@/hooks/useScrollState'
import { useTextSource } from '@/hooks/useTextSource'
import { isNewTestament, AVAILABLE_BOOKS, type BookName } from '@/lib/books'
import { WarningIcon } from './icons'

const GITHUB_ISSUES_URL = 'https://github.com/edyhvh/shafan/issues'

export default function CorrectionWarning() {
  const pathname = usePathname()
  const locale = getLocaleFromPath(pathname)
  const { shouldHideForContent } = useScrollState()
  const { textSource, isLoaded } = useTextSource()
  const [isErrorPage, setIsErrorPage] = useState(false)

  // Detect if we're on an error page by checking for error-specific content
  useEffect(() => {
    // Check for error page indicators
    const errorIndicators = [
      'נראה שהייתה שגיאה', // Hebrew error title
      'Parece que hubo un error', // Spanish error title
      'It seems there was an error', // English error title
    ]

    const checkForError = () => {
      const mainContent = document.querySelector('main')
      if (mainContent) {
        const text = mainContent.textContent || ''
        const hasError = errorIndicators.some((indicator) =>
          text.includes(indicator)
        )
        setIsErrorPage(hasError)
      }
    }

    // Check immediately and after a short delay to catch async rendering
    checkForError()
    const timeout = setTimeout(checkForError, 100)

    return () => clearTimeout(timeout)
  }, [pathname])

  // Extract bookId from pathname (format: /[locale]/book/[bookId]/chapter/[chapterId])
  const bookMatch = pathname.match(/\/book\/([^/]+)/)
  const bookId = bookMatch ? (bookMatch[1] as BookName) : null
  const isNTBook =
    bookId && AVAILABLE_BOOKS.includes(bookId) && isNewTestament(bookId)

  // Only show warning in books section, not on error pages, AND only for Hutter text in New Testament books
  if (
    !pathname.includes('/book/') ||
    isErrorPage ||
    pathname.includes('/error') ||
    pathname.includes('/not-found') ||
    !isLoaded ||
    textSource === 'delitzsch' ||
    !isNTBook
  ) {
    return null
  }

  // Hide when scrolled down
  if (shouldHideForContent) {
    return null
  }

  return (
    <div className="fixed top-4 left-4 z-40 transition-all duration-300 ease-out animate-in fade-in slide-in-from-top-2">
      <div className="bg-yellow-200/80 backdrop-blur-sm border-2 border-yellow-300/60 rounded-lg px-1.5 py-2 shadow-lg flex items-start gap-1.5 max-w-[180px]">
        <WarningIcon className="w-3.5 h-3.5 warning-text flex-shrink-0 mt-0.5" />
        <p className="text-[9px] sm:text-[10px] warning-text font-medium leading-tight">
          {t('correction_warning_text', locale)}{' '}
          <Link
            href={GITHUB_ISSUES_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="underline font-semibold warning-text hover:opacity-80 transition-opacity"
          >
            {t('correction_warning_link', locale)}
          </Link>
        </p>
      </div>
    </div>
  )
}

'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { getLocaleFromPath } from '@/lib/locale'
import { t } from '@/lib/translations'
import { WarningIcon } from './icons'

const GITHUB_ISSUES_URL = 'https://github.com/edyhvh/shafan/issues'

export default function CorrectionWarning() {
  const pathname = usePathname()
  const locale = getLocaleFromPath(pathname)
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

  // Only show warning in books section, not on error pages
  if (
    !pathname.includes('/book/') ||
    isErrorPage ||
    pathname.includes('/error') ||
    pathname.includes('/not-found')
  ) {
    return null
  }

  return (
    <div className="fixed top-4 left-4 z-40">
      <div className="bg-yellow-200/80 backdrop-blur-sm border-2 border-yellow-300/60 rounded-lg px-2 py-2.5 shadow-lg flex items-start gap-1.5 max-w-[200px]">
        <WarningIcon className="w-4 h-4 text-black flex-shrink-0 mt-0.5" />
        <p className="text-[10px] sm:text-[11px] text-black font-medium leading-tight">
          {t('correction_warning_text', locale)}{' '}
          <Link
            href={GITHUB_ISSUES_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="underline font-semibold hover:text-black/80 transition-colors"
          >
            {t('correction_warning_link', locale)}
          </Link>
        </p>
      </div>
    </div>
  )
}

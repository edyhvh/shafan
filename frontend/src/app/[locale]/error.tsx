'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { getLocaleFromPath } from '@/lib/locale'
import { logger } from '@/lib/logger'

/**
 * Error page for locale-specific routes
 * Automatically shown when an error occurs in locale routes
 */
export default function LocaleError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  const pathname = usePathname()
  const locale = getLocaleFromPath(pathname)

  useEffect(() => {
    // Log the error
    logger.error('Locale route error', error, {
      digest: error.digest,
      pathname,
      locale,
    })
  }, [error, pathname, locale])

  const translations = {
    he: {
      title: 'משהו השתבש',
      message: 'אנו מצטערים, אך אירעה שגיאה בלתי צפויה.',
      tryAgain: 'נסה שוב',
      home: 'חזרה לדף הבית',
    },
    es: {
      title: 'Algo salió mal',
      message: 'Lo sentimos, pero ocurrió un error inesperado.',
      tryAgain: 'Intentar de nuevo',
      home: 'Volver al inicio',
    },
    en: {
      title: 'Something went wrong',
      message: "We're sorry, but an unexpected error occurred.",
      tryAgain: 'Try again',
      home: 'Back to home',
    },
  }

  const t = translations[locale as keyof typeof translations] || translations.en

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="max-w-md w-full text-center">
        <h1 className="text-4xl font-bold text-black mb-4">{t.title}</h1>
        <p className="text-lg text-gray mb-8">{t.message}</p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={reset}
            className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray transition-colors"
          >
            {t.tryAgain}
          </button>
          <Link
            href={`/${locale}`}
            className="px-6 py-3 bg-white text-black border border-black/20 rounded-lg hover:bg-black/5 transition-colors"
          >
            {t.home}
          </Link>
        </div>

        {process.env.NODE_ENV === 'development' && error.message && (
          <div className="mt-8 p-4 bg-red-50 border border-red-200 rounded-lg text-left">
            <p className="text-sm font-mono text-red-800 break-all">
              {error.message}
            </p>
            {error.digest && (
              <p className="text-xs text-red-600 mt-2">
                Digest: {error.digest}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { getLocaleFromPath } from '@/lib/locale'

/**
 * Client component for locale-specific not found content
 * Uses usePathname to detect locale from URL
 */
export default function LocaleNotFoundContent() {
  const pathname = usePathname()
  const locale = getLocaleFromPath(pathname || '')

  const translations = {
    he: {
      title: 'נראה שהייתה שגיאה',
      subtitle: 'שמור על קור רוח וישוע המשיח',
      home: 'חזרה לדף הבית',
    },
    es: {
      title: 'Parece que hubo un error',
      subtitle: "Mantén la calma y Yeshua Ha'Mashiaj",
      home: 'Volver al inicio',
    },
    en: {
      title: 'It seems there was an error',
      subtitle: "Keep Calm and Yeshua Ha'Mashiaj",
      home: 'Back to home',
    },
  }

  const t = translations[locale as keyof typeof translations] || translations.en
  const isHebrew = locale === 'he'

  return (
    <div className="min-h-screen flex items-start justify-center bg-background px-4 pt-32">
      <div className="max-w-2xl w-full text-center">
        <div className="text-8xl font-bold text-black/20 mb-6">404</div>

        {/* Main error message - Large text */}
        <h1
          className={`text-5xl md:text-6xl font-bold text-black mb-8 ${isHebrew ? 'font-ui-hebrew' : ''}`}
          dir={isHebrew ? 'rtl' : 'ltr'}
        >
          {t.title}
        </h1>

        {/* Subtitle - Smaller text */}
        <p
          className={`text-2xl md:text-3xl text-gray mb-8 ${isHebrew ? 'font-ui-hebrew' : ''}`}
          dir={isHebrew ? 'rtl' : 'ltr'}
        >
          {t.subtitle}
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href={`/${locale}`}
            className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray transition-colors"
          >
            {t.home}
          </Link>
        </div>
      </div>
    </div>
  )
}

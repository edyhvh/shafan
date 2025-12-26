'use client'

import { usePathname, useRouter } from 'next/navigation'
import { useState } from 'react'
import { getLocaleFromPath, removeLocaleFromPath } from '@/lib/locale'
import { ChevronDown } from '@/components/icons'

const languages = [
  { code: 'he', label: 'עברית', nativeLabel: 'עברית' },
  { code: 'es', label: 'Español', nativeLabel: 'Español' },
  { code: 'en', label: 'English', nativeLabel: 'English' },
]

export default function LanguageSelector() {
  const pathname = usePathname()
  const router = useRouter()
  const [isOpen, setIsOpen] = useState(false)

  const currentLocale = getLocaleFromPath(pathname)
  const currentLanguage =
    languages.find((lang) => lang.code === currentLocale) || languages[0]

  const handleLanguageChange = (locale: string) => {
    setIsOpen(false)
    const pathWithoutLocale = removeLocaleFromPath(pathname)
    const newPath = `/${locale}${pathWithoutLocale === '/' ? '' : pathWithoutLocale}`
    router.push(newPath)
  }

  return (
    <div
      className="relative"
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
    >
      <button
        className="flex items-center gap-1.5 px-2 py-1.5 text-xs font-ui-latin font-bold text-black/80 hover:text-black transition-colors rounded-full hover:bg-black/5"
        aria-label="Select language"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <span>{currentLanguage.nativeLabel}</span>
        <ChevronDown
          className={`transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {/* Invisible hover bridge - always present to extend hover area */}
      <div className="absolute right-0 top-full w-[120px] h-3" />

      {/* Dropdown menu */}
      {isOpen && (
        <div className="absolute right-0 top-[calc(100%+4px)] z-50 dropdown-panel min-w-[120px] overflow-hidden">
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => handleLanguageChange(lang.code)}
              className={`w-full text-left px-4 py-2.5 text-sm font-ui-latin hover:bg-black/5 transition-colors ${
                currentLocale === lang.code
                  ? 'font-bold text-black bg-black/5'
                  : 'font-medium text-black/80'
              }`}
            >
              {lang.nativeLabel}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

'use client'

import { usePathname, useRouter } from 'next/navigation'
import { useState, useRef } from 'react'
import { getLocaleFromPath, removeLocaleFromPath } from '@/lib/locale'
import { ChevronDown } from '@/components/icons'
import { useIsMobile } from '@/hooks/useIsMobile'
import { useClickOutside } from '@/hooks/useClickOutside'

const languages = [
  { code: 'he', label: 'עברית', nativeLabel: 'עברית' },
  { code: 'es', label: 'Español', nativeLabel: 'Español' },
  { code: 'en', label: 'English', nativeLabel: 'English' },
]

export default function LanguageSelector() {
  const pathname = usePathname()
  const router = useRouter()
  const [isOpen, setIsOpen] = useState(false)
  const isMobile = useIsMobile()
  const containerRef = useRef<HTMLDivElement>(null)
  const buttonRef = useRef<HTMLButtonElement>(null)

  const currentLocale = getLocaleFromPath(pathname)
  const currentLanguage =
    languages.find((lang) => lang.code === currentLocale) || languages[0]

  // Close dropdown when clicking outside
  useClickOutside(containerRef, () => setIsOpen(false), isOpen)

  const handleLanguageChange = (locale: string) => {
    setIsOpen(false)
    const pathWithoutLocale = removeLocaleFromPath(pathname)
    const newPath = `/${locale}${pathWithoutLocale === '/' ? '' : pathWithoutLocale}`
    router.push(newPath)
  }

  const handleToggle = () => {
    setIsOpen(!isOpen)
  }

  return (
    <div
      ref={containerRef}
      className="relative"
      onMouseEnter={!isMobile ? () => setIsOpen(true) : undefined}
      onMouseLeave={!isMobile ? () => setIsOpen(false) : undefined}
    >
      <button
        ref={buttonRef}
        onClick={isMobile ? handleToggle : undefined}
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

      {/* Invisible hover bridge - only on desktop */}
      {!isMobile && <div className="absolute right-0 top-full w-[120px] h-3" />}

      {/* Dropdown menu */}
      {isOpen && (
        <div
          className={`${isMobile ? 'mt-2' : 'absolute right-0 top-[calc(100%+4px)] z-[60]'} dropdown-panel min-w-[120px] overflow-hidden shadow-lg`}
        >
          {languages.map((lang) => {
            const isSelected = currentLocale === lang.code
            return (
              <button
                key={lang.code}
                onClick={() => handleLanguageChange(lang.code)}
                className={`w-full text-left px-4 py-2.5 text-sm font-ui-latin transition-colors ${
                  isSelected
                    ? 'font-bold text-black bg-primary/10 border-l-2 border-primary'
                    : 'font-medium text-black/80 hover:bg-black/5'
                }`}
              >
                {lang.nativeLabel}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

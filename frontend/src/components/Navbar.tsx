'use client'

import { useState, useCallback, useEffect, useRef } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { getLocaleFromPath } from '@/lib/locale'
import { t } from '@/lib/translations'
import BooksDropdown from './navigation/BooksDropdown'
import LanguageSelector from './LanguageSelector'
import Logo from './Logo'
import { MenuIcon } from './icons'
import { getLastBookLocation } from '@/hooks/useLastBook'
import { useScrollState } from '@/hooks/useScrollState'

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [booksDropdownOpen, setBooksDropdownOpen] = useState(false)
  const booksTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const isBooksHoveredRef = useRef(false)
  const pathname = usePathname()
  const locale = getLocaleFromPath(pathname)
  const router = useRouter()
  const { shouldHideForContent } = useScrollState()

  // Clear timeouts on unmount
  useEffect(() => {
    return () => {
      if (booksTimeoutRef.current) {
        clearTimeout(booksTimeoutRef.current)
      }
    }
  }, [])

  const handleBooksMouseEnter = () => {
    isBooksHoveredRef.current = true
    setBooksDropdownOpen(true)
    // Clear any pending close
    if (booksTimeoutRef.current) {
      clearTimeout(booksTimeoutRef.current)
      booksTimeoutRef.current = null
    }
  }

  const handleBooksMouseLeave = () => {
    isBooksHoveredRef.current = false
    // Clear any existing timeout
    if (booksTimeoutRef.current) {
      clearTimeout(booksTimeoutRef.current)
    }
    // Set timeout to close dropdown
    booksTimeoutRef.current = setTimeout(() => {
      // Check if still not hovered before closing
      if (!isBooksHoveredRef.current) {
        setBooksDropdownOpen(false)
      }
    }, 300)
  }

  const handleBooksClick = useCallback(() => {
    const lastBook = getLastBookLocation()
    if (lastBook) {
      router.push(
        `/${locale}/book/${lastBook.bookId}/chapter/${lastBook.chapterId}`
      )
    }
  }, [locale, router])

  const handleLogoClick = useCallback(
    (e: React.MouseEvent) => {
      // Check if we're already on a chapter page
      const isOnChapterPage = /\/book\/[^/]+\/chapter\/[^/]+/.test(pathname)

      // If already on a chapter page, do nothing (stay on same page)
      if (isOnChapterPage) {
        e.preventDefault()
        return
      }

      // Otherwise, navigate to the last book/chapter or default to john/1
      e.preventDefault()
      const lastBook = getLastBookLocation()
      if (lastBook) {
        router.push(
          `/${locale}/book/${lastBook.bookId}/chapter/${lastBook.chapterId}`
        )
      } else {
        router.push(`/${locale}/book/john/chapter/1`)
      }
    },
    [locale, pathname, router]
  )

  // Determine if navbar should be hidden
  const shouldHideNavbar = shouldHideForContent

  return (
    <nav
      className={`fixed top-6 left-1/2 -translate-x-1/2 z-50 transition-all duration-300 ease-in-out ${
        shouldHideNavbar
          ? '-translate-y-[calc(100%+2rem)] opacity-0'
          : 'translate-y-0 opacity-100'
      }`}
    >
      <div className="flex items-center gap-2 px-3 py-2 rounded-lg neumorphism navbar-container">
        {/* Logo */}
        <button
          onClick={handleLogoClick}
          className="px-2 cursor-pointer hover:opacity-80 transition-opacity duration-200"
          aria-label="Go to chapter"
        >
          <Logo size="compact" />
        </button>

        {/* Books Link */}
        <div
          className="relative"
          onMouseEnter={handleBooksMouseEnter}
          onMouseLeave={handleBooksMouseLeave}
        >
          <button
            onClick={handleBooksClick}
            className="px-3 py-1.5 text-xs font-medium text-black/80 hover:text-black transition-all duration-200 rounded-lg hover:bg-black/5"
          >
            {t('books', locale)}
          </button>
          <div
            className={`absolute top-full ${locale === 'he' ? 'right-0' : 'left-0'} pt-1`}
            onMouseEnter={handleBooksMouseEnter}
            onMouseLeave={handleBooksMouseLeave}
          >
            <div
              className={`books-dropdown-float ${booksDropdownOpen ? 'open' : ''}`}
            >
              <BooksDropdown
                isOpen={booksDropdownOpen}
                onClose={() => {
                  isBooksHoveredRef.current = false
                  setBooksDropdownOpen(false)
                }}
              />
            </div>
          </div>
        </div>

        {/* Navigation Links - Desktop */}
        <div className="hidden md:flex items-center">
          {/* Info Link */}
          <Link
            href={`/${locale}/info`}
            className="px-3 py-1.5 text-xs font-medium text-black/80 hover:text-black transition-all duration-200 rounded-lg hover:bg-black/5"
          >
            {t('info', locale)}
          </Link>

          {/* Donate Link */}
          <Link
            href={`/${locale}/donate`}
            className="px-3 py-1.5 text-xs font-medium text-black/80 hover:text-black transition-all duration-200 rounded-lg hover:bg-black/5"
          >
            {t('donate', locale)}
          </Link>
        </div>

        {/* Language Selector - Desktop */}
        <div className="hidden md:block border-s border-black/10 ps-2 ms-1">
          <LanguageSelector />
        </div>

        {/* Hamburger Menu Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2.5 text-black/70 hover:text-black transition-all duration-200 rounded-full hover:bg-black/5"
          aria-label="Toggle menu"
        >
          <MenuIcon isOpen={mobileMenuOpen} />
        </button>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="absolute top-full left-1/2 -translate-x-1/2 mt-3 w-56 rounded-2xl bg-gradient-to-b from-white/40 to-white/25 backdrop-blur-3xl backdrop-saturate-200 border border-white/40 shadow-[0_8px_32px_rgba(0,0,0,0.08),inset_0_1px_1px_rgba(255,255,255,0.6)] ring-1 ring-white/30 overflow-hidden">
          <div className="py-2">
            <button
              onClick={() => {
                const lastBook = getLastBookLocation()
                if (lastBook) {
                  router.push(
                    `/${locale}/book/${lastBook.bookId}/chapter/${lastBook.chapterId}`
                  )
                  setMobileMenuOpen(false)
                } else {
                  setBooksDropdownOpen(!booksDropdownOpen)
                }
              }}
              className="w-full text-left px-5 py-3 text-sm font-medium text-black/80 hover:text-black transition-all duration-200 hover:bg-black/5"
            >
              {t('books', locale)}
            </button>
            {booksDropdownOpen && (
              <div className="px-5 pb-2">
                <BooksDropdown
                  isOpen={booksDropdownOpen}
                  onClose={() => setBooksDropdownOpen(false)}
                />
              </div>
            )}
            <Link
              href={`/${locale}/info`}
              onClick={() => setMobileMenuOpen(false)}
              className="block px-5 py-3 text-sm font-medium text-black/80 hover:text-black transition-all duration-200 hover:bg-black/5"
            >
              {t('info', locale)}
            </Link>
            <Link
              href={`/${locale}/donate`}
              onClick={() => setMobileMenuOpen(false)}
              className="block px-5 py-3 text-sm font-medium text-black/80 hover:text-black transition-all duration-200 hover:bg-black/5"
            >
              {t('donate', locale)}
            </Link>
            <div className="border-t border-black/10 mt-2 pt-2 px-5 py-3">
              <LanguageSelector />
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}

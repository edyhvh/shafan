'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { getLocaleFromPath } from '@/lib/locale';
import { t } from '@/lib/translations';
import BooksDropdown from './navigation/BooksDropdown';
import LanguageSelector from './LanguageSelector';
import Logo from './Logo';
import { MenuIcon } from './icons';
import { getLastBookLocation } from '@/hooks/useLastBook';

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [booksDropdownOpen, setBooksDropdownOpen] = useState(false);
  const pathname = usePathname();
  const locale = getLocaleFromPath(pathname);
  const router = useRouter();

  const handleBooksClick = useCallback(() => {
    const lastBook = getLastBookLocation();
    if (lastBook) {
      router.push(`/${locale}/book/${lastBook.bookId}/chapter/${lastBook.chapterId}`);
    }
  }, [locale, router]);

  return (
    <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50">
      <div className="flex items-center gap-2 px-3 py-2 rounded-full bg-gradient-to-b from-white/35 to-white/20 backdrop-blur-3xl backdrop-saturate-200 border border-white/40 shadow-[0_8px_32px_rgba(0,0,0,0.08),inset_0_1px_1px_rgba(255,255,255,0.6)] ring-1 ring-white/30">
        {/* Logo */}
        <div className="px-2">
          <Logo size="compact" />
        </div>

        {/* Navigation Links - Desktop */}
        <div className="hidden md:flex items-center">
          {/* Books Link */}
          <div className="relative">
            <button
              onClick={handleBooksClick}
              onMouseEnter={() => setBooksDropdownOpen(true)}
              onMouseLeave={() => {
                setTimeout(() => {
                  if (!document.querySelector('.books-dropdown-float:hover')) {
                    setBooksDropdownOpen(false);
                  }
                }, 150);
              }}
              className="px-4 py-2 text-sm font-medium text-black/80 hover:text-black transition-all duration-200 rounded-full hover:bg-black/5"
            >
              {t('books', locale)}
            </button>
            <div className={`books-dropdown-float absolute top-full mt-2 ${locale === 'he' ? 'right-0' : 'left-0'}`}>
              <BooksDropdown
                isOpen={booksDropdownOpen}
                onClose={() => setBooksDropdownOpen(false)}
              />
            </div>
          </div>

          {/* Info Link */}
          <Link
            href={`/${locale}/info`}
            className="px-4 py-2 text-sm font-medium text-black/80 hover:text-black transition-all duration-200 rounded-full hover:bg-black/5"
          >
            {t('info', locale)}
          </Link>

          {/* Donate Link */}
          <Link
            href={`/${locale}/donate`}
            className="px-4 py-2 text-sm font-medium text-black/80 hover:text-black transition-all duration-200 rounded-full hover:bg-black/5"
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
                const lastBook = getLastBookLocation();
                if (lastBook) {
                  router.push(`/${locale}/book/${lastBook.bookId}/chapter/${lastBook.chapterId}`);
                  setMobileMenuOpen(false);
                } else {
                  setBooksDropdownOpen(!booksDropdownOpen);
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
  );
}

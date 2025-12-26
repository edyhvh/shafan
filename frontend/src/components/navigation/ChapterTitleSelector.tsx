'use client';

import { useState, useRef } from 'react';
import Link from 'next/link';
import { useClickOutside } from '@/hooks/useClickOutside';
import { ChevronDown } from '@/components/icons';
import { AVAILABLE_BOOKS, BOOK_DISPLAY_NAMES, BOOK_HEBREW_INFO, type BookName } from '@/lib/books';

interface ChapterTitleSelectorProps {
  bookDisplayName: string;
  currentChapter: number;
  hebrewLetter?: string;
  chapters: { number: number; hebrew_letter: string }[];
  bookName: string;
  locale: string;
}

export default function ChapterTitleSelector({
  bookDisplayName,
  currentChapter,
  hebrewLetter,
  chapters,
  bookName,
  locale,
}: ChapterTitleSelectorProps) {
  const [isChapterOpen, setIsChapterOpen] = useState(false);
  const [isBookOpen, setIsBookOpen] = useState(false);
  const chapterDropdownRef = useRef<HTMLDivElement>(null);
  const bookDropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdowns when clicking outside
  useClickOutside(chapterDropdownRef, () => setIsChapterOpen(false), isChapterOpen);
  useClickOutside(bookDropdownRef, () => setIsBookOpen(false), isBookOpen);

  // Get Hebrew info for the current book (for en/es locales)
  const hebrewInfo = BOOK_HEBREW_INFO[bookName as BookName];

  return (
    <div className="text-center mb-8 pt-12">
      {/* Hebrew name and transliteration (only for en/es locales) */}
      {locale !== 'he' && hebrewInfo && (
        <div className="mb-3 text-center">
          <div className="font-bible-hebrew text-xl text-black/70 leading-tight">{hebrewInfo.hebrew}</div>
          <div className="text-[11px] text-black/35 font-light tracking-wide">{hebrewInfo.transliteration}</div>
        </div>
      )}
      <h1 className="font-ui-latin text-lg text-black mb-1 inline-flex items-center gap-2">
        {/* Book selector with click dropdown */}
        <div className="relative inline-block" ref={bookDropdownRef}>
          <button
            onClick={() => {
              setIsBookOpen(!isBookOpen);
              setIsChapterOpen(false);
            }}
            className={`
              h-[36px] px-3
              flex items-center justify-center
              font-semibold text-base
              bg-black/5 hover:bg-black/10
              border border-black/10 hover:border-black/20
              rounded-lg
              cursor-pointer
              transition-all duration-200
              ${isBookOpen ? 'bg-black/10 border-black/20 shadow-sm' : ''}
            `}
            aria-expanded={isBookOpen}
            aria-haspopup="listbox"
          >
            <span className={locale === 'he' ? 'font-ui-hebrew' : ''}>{bookDisplayName}</span>
            <ChevronDown className={`ml-1 transition-transform duration-200 ${isBookOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* Books dropdown */}
          {isBookOpen && (
            <div className="absolute left-1/2 -translate-x-1/2 top-full mt-2 dropdown-panel overflow-hidden z-50 min-w-[200px] max-h-[400px] overflow-y-auto">
              <div className="py-1">
                {AVAILABLE_BOOKS.map((book) => {
                  const displayName = BOOK_DISPLAY_NAMES[book];
                  const isCurrentBook = book === bookName;
                  return (
                    <Link
                      key={book}
                      href={`/${locale}/book/${book}/chapter/1`}
                      onClick={() => setIsBookOpen(false)}
                      className={`block px-4 py-2 text-sm font-semibold transition-all duration-200 ${
                        isCurrentBook
                          ? 'bg-black text-white'
                          : 'text-black hover:bg-black/5'
                      } ${locale === 'he' ? 'font-ui-hebrew text-right' : ''}`}
                    >
                      {displayName[locale as 'he' | 'es' | 'en'] || displayName.en}
                    </Link>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Chapter selector with click dropdown */}
        <div className="relative inline-block" ref={chapterDropdownRef}>
          <button
            onClick={() => {
              setIsChapterOpen(!isChapterOpen);
              setIsBookOpen(false);
            }}
            className={`
              min-w-[36px] h-[36px] px-2
              flex items-center justify-center
              font-semibold text-base
              bg-black/5 hover:bg-black/10
              border border-black/10 hover:border-black/20
              rounded-lg
              cursor-pointer
              transition-all duration-200
              ${isChapterOpen ? 'bg-black/10 border-black/20 shadow-sm' : ''}
            `}
            aria-expanded={isChapterOpen}
            aria-haspopup="listbox"
          >
            {locale === 'he' && hebrewLetter ? (
              <span className="font-ui-hebrew">{hebrewLetter}</span>
            ) : (
              currentChapter
            )}
            <ChevronDown className={`ml-1 transition-transform duration-200 ${isChapterOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* Chapters dropdown */}
          {isChapterOpen && chapters.length > 1 && (
            <div className="absolute left-1/2 -translate-x-1/2 top-full mt-2 dropdown-panel overflow-hidden z-50 min-w-[180px] max-h-[400px] overflow-y-auto">
              <div className="py-2">
                <div className="px-4 py-2 text-xs font-medium text-black/50 uppercase tracking-wide border-b border-black/5">
                  Chapters
                </div>
                <div className="grid grid-cols-4 gap-1 p-2">
                  {chapters.map((chapter) => (
                    <Link
                      key={chapter.number}
                      href={`/${locale}/book/${bookName}/chapter/${chapter.number}`}
                      onClick={() => setIsChapterOpen(false)}
                      className={`flex items-center justify-center p-2 text-sm font-semibold rounded-lg transition-all duration-200 ${
                        chapter.number === currentChapter
                          ? 'bg-black text-white'
                          : 'text-black hover:bg-black/5'
                      }`}
                    >
                      {chapter.number}
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </h1>
    </div>
  );
}




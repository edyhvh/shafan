'use client';

import { Chapter } from '@/lib/types';
import { useState } from 'react';
import VersesDropdown from './VersesDropdown';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { getLocaleFromPath } from '@/lib/locale';

interface ChaptersDropdownProps {
  chapters: Chapter[];
  bookName: string;
  isOpen: boolean;
  onClose: () => void;
  onCloseAll?: () => void;
}

export default function ChaptersDropdown({
  chapters,
  bookName,
  isOpen,
  onClose,
  onCloseAll,
}: ChaptersDropdownProps) {
  const [selectedChapter, setSelectedChapter] = useState<number | null>(null);
  const pathname = usePathname();
  const locale = getLocaleFromPath(pathname);

  if (!isOpen) return null;

  const chapter = selectedChapter ? chapters.find(c => c.number === selectedChapter) : null;

  // If no chapters, show message
  if (!chapters || chapters.length === 0) {
    return (
      <div className="dropdown-panel z-[60] p-4">
        <span className="text-sm text-black/60">No chapters</span>
      </div>
    );
  }

  // Calculate grid columns based on number of chapters
  const gridCols = chapters.length === 1 ? 1 : chapters.length <= 4 ? 2 : chapters.length <= 9 ? 3 : chapters.length <= 16 ? 4 : 5;

  // For single chapter books, just show link without verse selection
  const isSingleChapter = chapters.length === 1;

  const handleChapterClick = (e: React.MouseEvent, chapterNumber: number) => {
    if (isSingleChapter) {
      // Single chapter: navigate directly
      return;
    }

    // Multi-chapter: toggle selection to show verses
    e.preventDefault();
    if (selectedChapter === chapterNumber) {
      setSelectedChapter(null);
    } else {
      setSelectedChapter(chapterNumber);
    }
  };

  return (
    <div
      className="relative dropdown-panel z-[60] p-3"
    >
      {/* Grid of chapters */}
      <div
        className="grid gap-2"
        style={{ gridTemplateColumns: `repeat(${gridCols}, 1fr)` }}
      >
        {chapters.map((ch) => {
          const isSelected = selectedChapter === ch.number;

          return (
            <Link
              key={ch.number}
              href={`/${locale}/book/${bookName}/chapter/${ch.number}`}
              className={`flex items-center justify-center w-10 h-10 text-sm font-semibold transition-all duration-150 rounded-lg cursor-pointer ${
                isSelected
                  ? 'bg-gray text-white scale-105 shadow-md'
                  : 'bg-black/5 text-black hover:bg-black/30 hover:text-black hover:scale-110 hover:shadow-sm hover:animate-pulse-subtle active:scale-95'
              } ${locale === 'he' ? 'font-ui-hebrew' : 'font-ui-latin'}`}
              onClick={(e) => handleChapterClick(e, ch.number)}
            >
              {locale === 'he' ? ch.hebrew_letter : ch.number}
            </Link>
          );
        })}
      </div>

      {/* Verses dropdown - positioned outside, appears on chapter selection */}
      {chapter && chapter.verses.length > 0 && (
        <div
          className="absolute left-full top-0 pl-2 z-[70] animate-slide-in"
        >
          <VersesDropdown
            verses={chapter.verses}
            bookName={bookName}
            chapterNumber={chapter.number}
            isOpen={true}
            onClose={() => setSelectedChapter(null)}
            onCloseAll={() => {
              onClose();
              onCloseAll?.();
            }}
          />
        </div>
      )}
    </div>
  );
}

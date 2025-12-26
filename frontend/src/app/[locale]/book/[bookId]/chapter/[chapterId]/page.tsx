import { notFound } from 'next/navigation'
import { AVAILABLE_BOOKS, BOOK_DISPLAY_NAMES, type BookName } from '@/lib/books'
import { loadBookServer } from '@/lib/books-server'
import ChapterTitleSelector from '@/components/navigation/ChapterTitleSelector'
import ChapterNavigation from '@/components/navigation/ChapterNavigation'
import ChapterContent from '@/components/ChapterContent'
import SaveLastBook from '@/components/navigation/SaveLastBook'

interface PageProps {
  params: Promise<{
    locale: string
    bookId: string
    chapterId: string
  }>
}

export async function generateMetadata({ params }: PageProps) {
  const resolvedParams = await params
  const { locale, bookId, chapterId } = resolvedParams

  // Runtime validation to prevent path traversal attacks
  if (!AVAILABLE_BOOKS.includes(bookId as BookName)) {
    return {
      title: 'Shafan',
      description: "Read Elias Hutter's Hebrew Besorah Translation",
      openGraph: {
        title: 'Shafan',
        description: "Read Elias Hutter's Hebrew Besorah Translation",
        type: 'website',
      },
      twitter: {
        card: 'summary',
        title: 'Shafan',
        description: "Read Elias Hutter's Hebrew Besorah Translation",
      },
    }
  }

  const bookName = bookId as BookName
  const chapterNumber = parseInt(chapterId)

  if (isNaN(chapterNumber) || chapterNumber < 1) {
    return {
      title: 'Shafan',
      description: "Read Elias Hutter's Hebrew Besorah Translation",
      openGraph: {
        title: 'Shafan',
        description: "Read Elias Hutter's Hebrew Besorah Translation",
        type: 'website',
      },
      twitter: {
        card: 'summary',
        title: 'Shafan',
        description: "Read Elias Hutter's Hebrew Besorah Translation",
      },
    }
  }

  // Get book display name based on locale
  const displayName = BOOK_DISPLAY_NAMES[bookName] || {
    en: bookName,
    he: bookName,
    es: bookName,
  }
  const bookDisplayName =
    displayName[locale as 'he' | 'es' | 'en'] || displayName.en

  const pageTitle = `Shafan - ${bookDisplayName}`

  return {
    title: pageTitle,
    description: "Read Elias Hutter's Hebrew Besorah Translation",
    openGraph: {
      title: pageTitle,
      description: "Read Elias Hutter's Hebrew Besorah Translation",
      type: 'website',
    },
    twitter: {
      card: 'summary',
      title: pageTitle,
      description: "Read Elias Hutter's Hebrew Besorah Translation",
    },
  }
}

export default async function BookChapterPage({ params }: PageProps) {
  const resolvedParams = await params
  const { locale, bookId, chapterId } = resolvedParams

  // Runtime validation to prevent path traversal attacks
  if (!AVAILABLE_BOOKS.includes(bookId as BookName)) {
    notFound()
  }

  const bookName = bookId as BookName
  const chapterNumber = parseInt(chapterId)

  // Validate parameters
  if (isNaN(chapterNumber) || chapterNumber < 1) {
    notFound()
  }

  // Load book data (Server Component - use server method)
  const book = await loadBookServer(bookName)

  if (!book) {
    notFound()
  }

  // Check if chapter exists
  const chapter = book.chapters.find((ch) => ch.number === chapterNumber)
  if (!chapter) {
    notFound()
  }

  const displayName = BOOK_DISPLAY_NAMES[bookName] || {
    en: bookName,
    he: bookName,
    es: bookName,
  }
  const bookDisplayName =
    displayName[locale as 'he' | 'es' | 'en'] || displayName.en

  return (
    <div className="max-w-4xl mx-auto">
      {/* Save current location to localStorage for "Back to reading" feature */}
      <SaveLastBook bookId={bookId} chapterId={chapterId} />

      {/* Title - Centered, with interactive chapter selector */}
      <ChapterTitleSelector
        bookDisplayName={bookDisplayName}
        currentChapter={chapterNumber}
        hebrewLetter={chapter.hebrew_letter}
        chapters={book.chapters.map((ch) => ({
          number: ch.number,
          hebrew_letter: ch.hebrew_letter,
        }))}
        bookName={bookName}
        locale={locale}
      />

      {/* Chapter Navigation */}
      <ChapterNavigation
        locale={locale}
        bookName={bookName}
        currentChapter={chapterNumber}
        totalChapters={book.chapters.length}
      />

      {/* Chapter Content */}
      <ChapterContent
        hebrewLetter={chapter.hebrew_letter}
        verses={chapter.verses}
      />

      {/* Chapter Navigation Footer */}
      <ChapterNavigation
        locale={locale}
        bookName={bookName}
        currentChapter={chapterNumber}
        totalChapters={book.chapters.length}
        className="mt-8 flex gap-4 justify-center"
      />

      {/* Author info at the end */}
      <div className="mt-12 text-center">
        <p className="font-ui-latin text-sm text-gray">
          {book.author} ({book.publication_year})
        </p>
      </div>
    </div>
  )
}

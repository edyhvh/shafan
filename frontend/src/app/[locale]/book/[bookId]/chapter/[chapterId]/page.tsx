import { notFound } from 'next/navigation'
import { AVAILABLE_BOOKS, BOOK_DISPLAY_NAMES, type BookName } from '@/lib/books'
import { loadBookServer } from '@/lib/books-server'
import ChapterTitleSelector from '@/components/navigation/ChapterTitleSelector'
import ChapterNavigation from '@/components/navigation/ChapterNavigation'
import ChapterContent from '@/components/ChapterContent'
import SaveLastBook from '@/components/navigation/SaveLastBook'
import AuthorInfo from '@/components/AuthorInfo'
import { Locale, locales } from '@/lib/locale'
import { t } from '@/lib/translations'

export const revalidate = 604800

export async function generateStaticParams() {
  const bookData = await Promise.all(
    AVAILABLE_BOOKS.map(async (bookId) => {
      const book = await loadBookServer(bookId)
      const chapterCount = book?.chapters.length ?? 0
      return { bookId, chapterCount }
    })
  )

  return bookData.flatMap(({ bookId, chapterCount }) =>
    locales.flatMap((locale) =>
      Array.from({ length: chapterCount }, (_, index) => ({
        locale,
        bookId,
        chapterId: String(index + 1),
      }))
    )
  )
}

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
      title: 'Shafan – Pure Hebrew for Scripture Study',
      description:
        'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.',
      keywords: [
        'hebrew tanakh online',
        'besorah hebrew hutter',
        'hebrew bible study',
        'tanakh hebrew text',
        'besorah hebrew',
      ],
      robots: { index: true, follow: true },
      openGraph: {
        title: 'Shafan – Bible in Hebrew for Scripture Study',
        description:
          'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.',
        type: 'website',
        url: 'https://shafan.xyz',
        images: [
          {
            url: '/og-image.png',
            alt: 'Shafan – Bible in Hebrew for Scripture Study',
          },
        ],
      },
      twitter: {
        card: 'summary_large_image',
        title: 'Shafan – Bible in Hebrew for Scripture Study',
        description:
          'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.',
        images: ['/og-image.png'],
      },
    }
  }

  const bookName = bookId as BookName
  const chapterNumber = parseInt(chapterId)

  if (isNaN(chapterNumber) || chapterNumber < 1) {
    return {
      title: 'Shafan – Pure Hebrew for Scripture Study',
      description:
        'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.',
      keywords: [
        'hebrew tanakh online',
        'besorah hebrew hutter',
        'hebrew bible study',
        'tanakh hebrew text',
        'besorah hebrew',
      ],
      robots: { index: true, follow: true },
      openGraph: {
        title: 'Shafan – Pure Hebrew for Scripture Study',
        description:
          'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.',
        type: 'website',
        url: 'https://shafan.xyz',
        images: [
          {
            url: '/og-image.png',
            alt: 'Shafan – Pure Hebrew for Scripture Study',
          },
        ],
      },
      twitter: {
        card: 'summary_large_image',
        title: 'Shafan – Pure Hebrew for Scripture Study',
        description:
          'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.',
        images: ['/og-image.png'],
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

  const hebrewBibleLabel = t('hebrew_bible_title', locale as Locale)
  const pageTitle = `${bookDisplayName} ${chapterNumber} – ${hebrewBibleLabel}`
  const description =
    'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.'
  const canonicalUrl = `https://shafan.xyz/${locale}/book/${bookId}/chapter/${chapterNumber}`

  return {
    title: pageTitle,
    description,
    keywords: [
      `${bookDisplayName} ${chapterNumber}`,
      `${bookDisplayName} Hebrew`,
      'hebrew tanakh online',
      'besorah hebrew hutter',
    ],
    robots: { index: true, follow: true },
    alternates: {
      canonical: canonicalUrl,
    },
    openGraph: {
      title: pageTitle,
      description,
      type: 'website',
      url: canonicalUrl,
      images: [
        {
          url: '/og-image.png',
          alt: 'Shafan – Pure Hebrew for Scripture Study',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: pageTitle,
      description,
      images: ['/og-image.png'],
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
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
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
        bookName={bookName}
        chapterNumber={chapterNumber}
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
      <AuthorInfo
        bookName={bookName}
        hutterAuthor={book.author}
        hutterYear={book.publication_year}
      />
    </div>
  )
}

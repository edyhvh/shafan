import { notFound } from 'next/navigation'
import { AVAILABLE_BOOKS, BOOK_DISPLAY_NAMES, type BookName } from '@/lib/books'
import { loadBookServer } from '@/lib/books-server'
import { loadTTHServer } from '@/lib/tth-server'
import { hasTTH } from '@/lib/tth'
import ChapterTitleSelector from '@/components/navigation/ChapterTitleSelector'
import ChapterNavigation from '@/components/navigation/ChapterNavigation'
import ChapterContent from '@/components/ChapterContent'
import SaveLastBook from '@/components/navigation/SaveLastBook'
import AuthorInfo from '@/components/AuthorInfo'
import { locales } from '@/lib/locale'
import { BRAND_CONFIG } from '@/lib/config'
import Script from 'next/script'

export const revalidate = 604800
const SOCIAL_IMAGE_URL = BRAND_CONFIG.socialImageUrl

// Generate only the first chapter of each book for initial build
// Other pages will be generated on-demand (ISR) to reduce deployment size
export async function generateStaticParams() {
  // Only pre-generate first chapter of each book
  // This dramatically reduces build size while still enabling SSG
  return AVAILABLE_BOOKS.flatMap((bookId) =>
    locales.map((locale) => ({
      locale,
      bookId,
      chapterId: '1',
    }))
  )
}

// Enable dynamic params for on-demand generation
export const dynamicParams = true

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
        title: 'Shafan – Pure Hebrew for Scripture Study',
        description:
          'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.',
        type: 'website',
        url: 'https://shafan.xyz',
        siteName: 'Shafan',
        images: [
          {
            url: SOCIAL_IMAGE_URL,
            width: 1200,
            height: 630,
            alt: 'Shafan – Pure Hebrew for Scripture Study',
            type: 'image/png',
          },
        ],
      },
      twitter: {
        card: 'summary_large_image',
        title: 'Shafan – Pure Hebrew for Scripture Study',
        description:
          'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.',
        images: [SOCIAL_IMAGE_URL],
        site: '@shafanxyz',
        creator: '@shafanxyz',
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
        siteName: 'Shafan',
        images: [
          {
            url: SOCIAL_IMAGE_URL,
            width: 1200,
            height: 630,
            alt: 'Shafan – Pure Hebrew for Scripture Study',
            type: 'image/png',
          },
        ],
      },
      twitter: {
        card: 'summary_large_image',
        title: 'Shafan – Pure Hebrew for Scripture Study',
        description:
          'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.',
        images: [SOCIAL_IMAGE_URL],
        site: '@shafanxyz',
        creator: '@shafanxyz',
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

  const pageTitle = `${bookDisplayName} ${chapterNumber}`
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
      type: 'article',
      url: canonicalUrl,
      siteName: 'Shafan',
      images: [
        {
          url: SOCIAL_IMAGE_URL,
          width: 1200,
          height: 630,
          alt: 'Shafan – Pure Hebrew for Scripture Study',
          type: 'image/png',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: pageTitle,
      description,
      images: [SOCIAL_IMAGE_URL],
      site: '@shafanxyz',
      creator: '@shafanxyz',
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

  // Load TTH data if available for this book
  const tthBook = hasTTH(bookName) ? await loadTTHServer(bookName) : null
  const tthChapter =
    tthBook?.chapters.find((ch) => ch.chapter === chapterNumber) ?? null
  const tthAvailable = hasTTH(bookName)

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

  // Generate JSON-LD structured data
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: `${bookDisplayName} ${chapterNumber}`,
    description:
      'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.',
    url: `https://shafan.xyz/${locale}/book/${bookId}/chapter/${chapterNumber}`,
    image: SOCIAL_IMAGE_URL,
    author: {
      '@type': 'Organization',
      name: 'Shafan',
      url: 'https://shafan.xyz',
    },
    publisher: {
      '@type': 'Organization',
      name: 'Shafan',
      url: 'https://shafan.xyz',
      logo: {
        '@type': 'ImageObject',
        url: 'https://shafan.xyz/icon.png',
      },
    },
    inLanguage: locale,
    isPartOf: {
      '@type': 'Book',
      name: bookDisplayName,
    },
  }

  const breadcrumbJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      {
        '@type': 'ListItem',
        position: 1,
        name: 'Home',
        item: `https://shafan.xyz/${locale}`,
      },
      {
        '@type': 'ListItem',
        position: 2,
        name: bookDisplayName,
        item: `https://shafan.xyz/${locale}/book/${bookId}/chapter/1`,
      },
      {
        '@type': 'ListItem',
        position: 3,
        name: `${bookDisplayName} ${chapterNumber}`,
        item: `https://shafan.xyz/${locale}/book/${bookId}/chapter/${chapterNumber}`,
      },
    ],
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <Script
        id={`jsonld-article-${locale}-${bookId}-${chapterNumber}`}
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <Script
        id={`jsonld-breadcrumb-${locale}-${bookId}-${chapterNumber}`}
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
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
        tthChapter={tthChapter}
        tthAvailable={tthAvailable}
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

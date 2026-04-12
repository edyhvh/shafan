import { BOOK_DISPLAY_NAMES, type BookName } from '@/lib/books'
import { BRAND_CONFIG } from '@/lib/config'

interface HeadProps {
  params: Promise<{
    locale: string
    bookId: string
    chapterId: string
  }>
}

export default async function Head({ params }: HeadProps) {
  const { locale, bookId, chapterId } = await params
  const chapterNumber = parseInt(chapterId, 10)
  const socialImageUrl = BRAND_CONFIG.socialImageUrl

  const displayName = BOOK_DISPLAY_NAMES[bookId as BookName] || {
    en: bookId,
    he: bookId,
    es: bookId,
  }
  const bookDisplayName =
    displayName[locale as 'he' | 'es' | 'en'] || displayName.en

  const articleJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: `${bookDisplayName} ${chapterNumber}`,
    description:
      'Read Tanakh and Besorah in Hebrew. Fast, clean, distraction-free for deep study.',
    url: `https://shafan.xyz/${locale}/book/${bookId}/chapter/${chapterNumber}`,
    image: socialImageUrl,
    datePublished: BRAND_CONFIG.contentPublishedTime,
    dateModified: BRAND_CONFIG.contentModifiedTime,
    author: {
      '@type': 'Person',
      name: BRAND_CONFIG.authorName,
      url: BRAND_CONFIG.authorUrl,
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
    <>
      <script
        id={`jsonld-article-${locale}-${bookId}-${chapterNumber}`}
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(articleJsonLd) }}
      />
      <script
        id={`jsonld-breadcrumb-${locale}-${bookId}-${chapterNumber}`}
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
    </>
  )
}

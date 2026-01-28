import { MetadataRoute } from 'next'
import { AVAILABLE_BOOKS } from '@/lib/books'
import { locales } from '@/lib/locale'
import { loadBookServer } from '@/lib/books-server'

const BASE_URL = 'https://shafan.xyz'

export const revalidate = 604800 // 7 days

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const lastmod = new Date().toISOString()
  const urls: MetadataRoute.Sitemap = []

  // Root URL
  urls.push({
    url: BASE_URL,
    lastModified: lastmod,
    changeFrequency: 'weekly',
    priority: 1.0,
  })

  // Locale home pages and info/donate pages
  locales.forEach((locale) => {
    urls.push({
      url: `${BASE_URL}/${locale}`,
      lastModified: lastmod,
      changeFrequency: 'weekly',
      priority: 0.9,
    })
    urls.push({
      url: `${BASE_URL}/${locale}/info`,
      lastModified: lastmod,
      changeFrequency: 'weekly',
      priority: 0.8,
    })
    urls.push({
      url: `${BASE_URL}/${locale}/donate`,
      lastModified: lastmod,
      changeFrequency: 'weekly',
      priority: 0.8,
    })
  })

  // Load all books and their chapters
  const books = await Promise.all(
    AVAILABLE_BOOKS.map(async (bookId) => {
      const book = await loadBookServer(bookId)
      return { bookId, chapterCount: book?.chapters.length ?? 0 }
    })
  )

  // Generate URLs for all book chapters
  books.forEach(({ bookId, chapterCount }) => {
    if (chapterCount < 1) return

    locales.forEach((locale) => {
      for (let chapter = 1; chapter <= chapterCount; chapter += 1) {
        urls.push({
          url: `${BASE_URL}/${locale}/book/${bookId}/chapter/${chapter}`,
          lastModified: lastmod,
          changeFrequency: 'weekly',
          priority: 0.85,
        })
      }
    })
  })

  return urls
}

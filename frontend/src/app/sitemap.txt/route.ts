import { AVAILABLE_BOOKS } from '@/lib/books'
import { locales } from '@/lib/locale'
import { loadBookServer } from '@/lib/books-server'

const BASE_URL = 'https://shafan.xyz'

export const revalidate = 604800

async function buildSitemapText(): Promise<string> {
  const urls = new Set<string>()

  urls.add(BASE_URL)

  locales.forEach((locale) => {
    urls.add(`${BASE_URL}/${locale}`)
    urls.add(`${BASE_URL}/${locale}/info`)
    urls.add(`${BASE_URL}/${locale}/donate`)
    urls.add(`${BASE_URL}/${locale}/terms`)
    urls.add(`${BASE_URL}/${locale}/privacy`)
  })

  const books = await Promise.all(
    AVAILABLE_BOOKS.map(async (bookId) => {
      const book = await loadBookServer(bookId)
      return { bookId, chapterCount: book?.chapters.length ?? 0 }
    })
  )

  books.forEach(({ bookId, chapterCount }) => {
    if (chapterCount < 1) return

    locales.forEach((locale) => {
      for (let chapter = 1; chapter <= chapterCount; chapter += 1) {
        urls.add(`${BASE_URL}/${locale}/book/${bookId}/chapter/${chapter}`)
      }
    })
  })

  return Array.from(urls).join('\n')
}

export async function GET() {
  const body = await buildSitemapText()

  return new Response(body, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control':
        'public, s-maxage=604800, stale-while-revalidate=1209600',
    },
  })
}

import { AVAILABLE_BOOKS, type BookName } from './books'

export function parseBookFromPath(pathname: string): BookName | null {
  const match = pathname.match(/\/book\/([^/]+)/)
  if (!match) return null
  const bookId = match[1]
  return AVAILABLE_BOOKS.includes(bookId as BookName)
    ? (bookId as BookName)
    : null
}

/**
 * Book data utilities for loading and managing Shafan book data
 * Client-safe version (no fs imports)
 */

import { Book } from './types'
import { logger } from './logger'

export const AVAILABLE_BOOKS = [
  'matthew',
  'mark',
  'luke',
  'john',
  'acts',
  'romans',
  'corinthians1',
  'corinthians2',
  'galatians',
  'ephesians',
  'philippians',
  'colossians',
  'thessalonians1',
  'thessalonians2',
  'timothy1',
  'timothy2',
  'titus',
  'philemon',
  'hebrews',
  'james',
  'peter1',
  'peter2',
  'john1',
  'john2',
  'john3',
  'jude',
  'revelation',
] as const

export type BookName = (typeof AVAILABLE_BOOKS)[number]

/**
 * Book name mappings for display
 * Maps internal book names to Hebrew display names
 */
export const BOOK_DISPLAY_NAMES: Record<
  BookName,
  { he: string; en: string; es: string }
> = {
  matthew: { he: 'מתי', en: 'Matthew', es: 'Mateo' },
  mark: { he: 'מרקוס', en: 'Mark', es: 'Marcos' },
  luke: { he: 'לוקס', en: 'Luke', es: 'Lucas' },
  john: { he: 'יוחנן', en: 'John', es: 'Juan' },
  acts: { he: 'מעשי השליחים', en: 'Acts', es: 'Hechos' },
  romans: { he: 'אל הרומים', en: 'Romans', es: 'Romanos' },
  corinthians1: { he: 'הקורינתים א', en: '1 Corinthians', es: '1 Corintios' },
  corinthians2: { he: 'הקורינתים ב', en: '2 Corinthians', es: '2 Corintios' },
  galatians: { he: 'אל הגלטים', en: 'Galatians', es: 'Gálatas' },
  ephesians: { he: 'אל האפסים', en: 'Ephesians', es: 'Efesios' },
  philippians: { he: 'אל הפיליפים', en: 'Philippians', es: 'Filipenses' },
  colossians: { he: 'אל הקולוסים', en: 'Colossians', es: 'Colosenses' },
  thessalonians1: {
    he: 'התסלוניקים א',
    en: '1 Thessalonians',
    es: '1 Tesalonicenses',
  },
  thessalonians2: {
    he: 'התסלוניקים ב',
    en: '2 Thessalonians',
    es: '2 Tesalonicenses',
  },
  timothy1: { he: 'טימותיוס א', en: '1 Timothy', es: '1 Timoteo' },
  timothy2: { he: 'טימותיוס ב', en: '2 Timothy', es: '2 Timoteo' },
  titus: { he: 'טיטוס', en: 'Titus', es: 'Tito' },
  philemon: { he: 'פילימון', en: 'Philemon', es: 'Filemón' },
  hebrews: { he: 'אל העברים', en: 'Hebrews', es: 'Hebreos' },
  james: { he: 'יעקב', en: 'James', es: 'Santiago' },
  peter1: { he: 'פטרוס א', en: '1 Peter', es: '1 Pedro' },
  peter2: { he: 'פטרוס ב', en: '2 Peter', es: '2 Pedro' },
  john1: { he: 'יוחנן א', en: '1 John', es: '1 Juan' },
  john2: { he: 'יוחנן ב', en: '2 John', es: '2 Juan' },
  john3: { he: 'יוחנן ג', en: '3 John', es: '3 Juan' },
  jude: { he: 'יהודה', en: 'Jude', es: 'Judas' },
  revelation: { he: 'ההתגלות (סודות)', en: 'Revelation', es: 'Apocalipsis' },
}

/**
 * Hebrew book names with Latin transliteration
 * For display in English and Spanish locales
 */
export const BOOK_HEBREW_INFO: Record<
  BookName,
  { hebrew: string; transliteration: string }
> = {
  matthew: { hebrew: 'מתי', transliteration: 'matai' },
  mark: { hebrew: 'מרקוס', transliteration: 'markus' },
  luke: { hebrew: 'לוקס', transliteration: 'lukas' },
  john: { hebrew: 'יוחנן', transliteration: 'yojanan' },
  acts: { hebrew: 'מעשי השליחים', transliteration: 'maase hashelijim' },
  romans: { hebrew: 'אל הרומים', transliteration: 'el haromim' },
  corinthians1: { hebrew: 'הקורינתים א', transliteration: 'hakorintim alef' },
  corinthians2: { hebrew: 'הקורינתים ב', transliteration: 'hakorintim bet' },
  galatians: { hebrew: 'אל הגלטים', transliteration: 'el hagalatim' },
  ephesians: { hebrew: 'אל האפסים', transliteration: 'el haefsim' },
  philippians: { hebrew: 'אל הפיליפים', transliteration: 'el hafilipim' },
  colossians: { hebrew: 'אל הקולוסים', transliteration: 'el hakolosim' },
  thessalonians1: {
    hebrew: 'התסלוניקים א',
    transliteration: 'hatesalonikim alef',
  },
  thessalonians2: {
    hebrew: 'התסלוניקים ב',
    transliteration: 'hatesalonikim bet',
  },
  timothy1: { hebrew: 'טימותיוס א', transliteration: 'timoteos alef' },
  timothy2: { hebrew: 'טימותיוס ב', transliteration: 'timoteos bet' },
  titus: { hebrew: 'טיטוס', transliteration: 'titos' },
  philemon: { hebrew: 'פילימון', transliteration: 'filimon' },
  hebrews: { hebrew: 'אל העברים', transliteration: 'el haivrim' },
  james: { hebrew: 'יעקב', transliteration: 'yaakov' },
  peter1: { hebrew: 'פטרוס א', transliteration: 'petros alef' },
  peter2: { hebrew: 'פטרוס ב', transliteration: 'petros bet' },
  john1: { hebrew: 'יוחנן א', transliteration: 'yojanan alef' },
  john2: { hebrew: 'יוחנן ב', transliteration: 'yojanan bet' },
  john3: { hebrew: 'יוחנן ג', transliteration: 'yojanan gimel' },
  jude: { hebrew: 'יהודה', transliteration: 'yehuda' },
  revelation: {
    hebrew: 'ההתגלות (סודות)',
    transliteration: 'hahitgalut (sodot)',
  },
}

/**
 * Load book data from JSON file (Client-side only)
 * Uses fetch to load from /data/ directory
 */
export async function loadBookClient(bookName: BookName): Promise<Book | null> {
  try {
    const response = await fetch(`/data/${bookName}.json`)
    if (!response.ok) {
      logger.error(
        `Failed to load book ${bookName}: ${response.statusText}`,
        undefined,
        {
          bookName,
          status: response.status,
          statusText: response.statusText,
        }
      )
      return null
    }
    const data: Book = await response.json()
    return data
  } catch (error) {
    logger.error(`Error loading book ${bookName}`, error, { bookName })
    return null
  }
}

/**
 * Get book metadata (name, author, publication year)
 */
export function getBookMetadata(book: Book) {
  return {
    name: book.book_name,
    author: book.author,
    publicationYear: book.publication_year,
    displayName: BOOK_DISPLAY_NAMES[book.book_name as BookName],
  }
}

/**
 * Get book index from book name
 */
export function getBookIndex(bookName: BookName): number {
  return AVAILABLE_BOOKS.indexOf(bookName)
}

/**
 * Get book name from index
 */
export function getBookNameByIndex(index: number): BookName | null {
  if (index < 0 || index >= AVAILABLE_BOOKS.length) {
    return null
  }
  return AVAILABLE_BOOKS[index]
}

/**
 * Search books by name (case-insensitive)
 */
export function searchBooks(query: string): BookName[] {
  const lowerQuery = query.toLowerCase()
  return AVAILABLE_BOOKS.filter((bookName) => {
    const displayNames = BOOK_DISPLAY_NAMES[bookName]
    return (
      bookName.toLowerCase().includes(lowerQuery) ||
      displayNames.en.toLowerCase().includes(lowerQuery) ||
      displayNames.es.toLowerCase().includes(lowerQuery) ||
      displayNames.he.includes(query)
    )
  })
}

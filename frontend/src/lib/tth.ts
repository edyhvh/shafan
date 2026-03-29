/**
 * TTH (Traducción del Texto Hebreo) utilities
 * Maps frontend book IDs to TTH file IDs and tracks availability
 */

import type { BookName } from './books'

/**
 * Mapping from frontend book IDs to TTH JSON file IDs (Hebrew transliteration)
 * null means no TTH translation is available for that book
 */
export const TTH_BOOK_MAP: Record<BookName, string | null> = {
  // Torah
  genesis: 'bereshit',
  exodus: 'shemot',
  leviticus: 'vaikra',
  numbers: 'bamidbar',
  deuteronomy: 'devarim',
  // Nevi'im
  joshua: 'iehoshua',
  judges: 'shoftim',
  ruth: null,
  isamuel: 'shemuel_alef',
  iisamuel: 'shemuel_bet',
  ikings: 'melajim_alef',
  iikings: 'melajim_bet',
  ichronicles: null,
  iichronicles: null,
  ezra: null,
  nehemiah: null,
  esther: null,
  job: null,
  psalms: 'tehilim',
  proverbs: 'mishlei',
  ecclesiastes: null,
  songofsolomon: null,
  isaiah: 'ieshaiahu',
  jeremiah: 'irmeiahu',
  lamentations: null,
  ezekiel: 'iejezkel',
  daniel: null,
  hosea: 'hoshea',
  joel: 'ioel',
  amos: 'amos',
  obadiah: null,
  jonah: 'ionah',
  micah: 'micah',
  nahum: 'najum',
  habakkuk: 'jabakuk',
  zephaniah: 'tzefaniah',
  haggai: 'jagai',
  zechariah: 'zejariah',
  malachi: 'malaji',
  // Besorah (NT)
  matthew: 'matityahu',
  mark: 'markos',
  luke: 'lukas',
  john: 'iojanan',
  acts: 'maasei_hashlijim',
  romans: 'romanos',
  corinthians1: null,
  corinthians2: null,
  galatians: null,
  ephesians: null,
  philippians: null,
  colossians: null,
  thessalonians1: null,
  thessalonians2: null,
  timothy1: null,
  timothy2: null,
  titus: null,
  philemon: null,
  hebrews: null,
  james: null,
  peter1: null,
  peter2: null,
  john1: null,
  john2: null,
  john3: null,
  jude: null,
  revelation: 'sodot',
}

/**
 * Pre-computed set of books that have TTH translations available
 */
export const TTH_AVAILABLE_BOOKS: Set<BookName> = new Set(
  (Object.entries(TTH_BOOK_MAP) as [BookName, string | null][])
    .filter(([, tthId]) => tthId !== null)
    .map(([bookName]) => bookName)
)

/**
 * Pre-computed map of TTH chapter counts per book
 * Some TTH books may have fewer chapters than the Hebrew version (e.g., Acts has only 2)
 */
export const TTH_CHAPTER_COUNTS: Partial<Record<BookName, number>> = {
  genesis: 52,
  exodus: 40,
  leviticus: 27,
  numbers: 36,
  deuteronomy: 34,
  joshua: 24,
  judges: 21,
  isamuel: 31,
  iisamuel: 24,
  ikings: 22,
  iikings: 25,
  isaiah: 66,
  jeremiah: 52,
  ezekiel: 48,
  hosea: 14,
  joel: 4,
  amos: 9,
  jonah: 4,
  micah: 7,
  nahum: 3,
  habakkuk: 3,
  zephaniah: 3,
  haggai: 2,
  zechariah: 14,
  malachi: 3,
  psalms: 150,
  proverbs: 31,
  matthew: 28,
  mark: 16,
  luke: 24,
  john: 21,
  acts: 2,
  romans: 16,
  revelation: 22,
}

/**
 * Check if a book has a TTH translation available
 */
export function hasTTH(bookName: BookName): boolean {
  return TTH_AVAILABLE_BOOKS.has(bookName)
}

/**
 * Get the TTH file ID for a given book name
 */
export function getTTHBookId(bookName: BookName): string | null {
  return TTH_BOOK_MAP[bookName]
}

/**
 * Get the number of TTH chapters available for a book (null if no TTH)
 */
export function getTTHChapterCount(bookName: BookName): number | null {
  return TTH_CHAPTER_COUNTS[bookName] ?? null
}

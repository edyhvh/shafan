/**
 * Book metadata - Static chapter counts for all books
 * This file contains lightweight metadata to avoid loading full JSON files during build
 */

import type { BookName } from './books'

/**
 * Chapter counts for each book
 * Extracted from the JSON data files to avoid loading them during generateStaticParams
 */
export const BOOK_CHAPTER_COUNTS: Record<BookName, number> = {
  // Tanaj (Hebrew Bible/Old Testament)
  genesis: 50,
  exodus: 40,
  leviticus: 27,
  numbers: 36,
  deuteronomy: 34,
  joshua: 24,
  judges: 21,
  ruth: 4,
  isamuel: 31,
  iisamuel: 24,
  ikings: 22,
  iikings: 25,
  ichronicles: 29,
  iichronicles: 36,
  ezra: 10,
  nehemiah: 13,
  esther: 10,
  job: 42,
  psalms: 150,
  proverbs: 31,
  ecclesiastes: 12,
  songofsolomon: 8,
  isaiah: 66,
  jeremiah: 52,
  lamentations: 5,
  ezekiel: 48,
  daniel: 12,
  hosea: 14,
  joel: 4,
  amos: 9,
  obadiah: 1,
  jonah: 4,
  micah: 7,
  nahum: 3,
  habakkuk: 3,
  zephaniah: 3,
  haggai: 2,
  zechariah: 14,
  malachi: 3,
  // Besorah (New Testament)
  matthew: 28,
  mark: 16,
  luke: 24,
  john: 21,
  acts: 28,
  romans: 16,
  corinthians1: 16,
  corinthians2: 13,
  galatians: 6,
  ephesians: 6,
  philippians: 4,
  colossians: 4,
  thessalonians1: 5,
  thessalonians2: 3,
  timothy1: 6,
  timothy2: 4,
  titus: 3,
  philemon: 1,
  hebrews: 13,
  james: 5,
  peter1: 5,
  peter2: 3,
  john1: 5,
  john2: 1,
  john3: 1,
  jude: 1,
  revelation: 22,
}

/**
 * Get chapter count for a book
 * @param bookName The book name
 * @returns The number of chapters in the book
 */
export function getChapterCount(bookName: BookName): number {
  return BOOK_CHAPTER_COUNTS[bookName] ?? 0
}

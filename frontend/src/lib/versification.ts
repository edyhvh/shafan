/**
 * Versification mapping utilities for Shafan
 *
 * Handles conversion between Hebrew (Masoretic) and English (KJV-style) versification
 * for books that have differences, particularly Psalms, Joel, and Malachi.
 */

import { BookName } from './books'

// Mapping from internal book names to OSIS codes used in versification data
const BOOK_TO_OSIS: Record<string, string> = {
  genesis: 'GEN',
  exodus: 'EXO',
  leviticus: 'LEV',
  numbers: 'NUM',
  deuteronomy: 'DEU',
  joshua: 'JOS',
  judges: 'JDG',
  ruth: 'RUT',
  isamuel: '1SA',
  iisamuel: '2SA',
  ikings: '1KI',
  iikings: '2KI',
  ichronicles: '1CH',
  iichronicles: '2CH',
  ezra: 'EZR',
  nehemiah: 'NEH',
  esther: 'EST',
  job: 'JOB',
  psalms: 'PSA',
  proverbs: 'PRO',
  ecclesiastes: 'ECC',
  songofsolomon: 'SNG',
  isaiah: 'ISA',
  jeremiah: 'JER',
  lamentations: 'LAM',
  ezekiel: 'EZK',
  daniel: 'DAN',
  hosea: 'HOS',
  joel: 'JOL',
  amos: 'AMO',
  obadiah: 'OBA',
  jonah: 'JON',
  micah: 'MIC',
  nahum: 'NAM',
  habakkuk: 'HAB',
  zephaniah: 'ZEP',
  haggai: 'HAG',
  zechariah: 'ZEC',
  malachi: 'MAL',
}

interface VersificationBookData {
  simple_map: Record<string, Record<string, string>>
  [key: string]: unknown
}

// Cached versification data
let versificationData: Record<string, VersificationBookData> | null = null
let dataLoaded = false

/**
 * Load versification data from the JSON file
 */
async function loadVersificationData(): Promise<void> {
  if (dataLoaded) return

  try {
    const response = await fetch('/data/versification/versification.json')
    if (!response.ok) {
      console.warn('Versification data not found, using default (no mappings)')
      versificationData = {}
      return
    }
    versificationData = await response.json()
    dataLoaded = true
  } catch (error) {
    console.warn('Failed to load versification data:', error)
    versificationData = {}
    dataLoaded = true
  }
}

/**
 * Get the OSIS code for a book name
 */
function getOsisCode(bookName: BookName): string | null {
  return BOOK_TO_OSIS[bookName] || null
}

/**
 * Get Christian Bible verse reference for a Hebrew verse
 *
 * @param bookName - Internal book name (e.g., 'psalms')
 * @param chapter - Hebrew chapter number
 * @param verse - Hebrew verse number
 * @returns Christian Bible verse reference (e.g., '1', '3:1') or null if no mapping exists
 */
export async function getChristianVerse(
  bookName: BookName,
  chapter: number,
  verse: number
): Promise<string | null> {
  // Ensure data is loaded
  await loadVersificationData()

  if (!versificationData) {
    return null
  }

  // Get OSIS code for this book
  const osisCode = getOsisCode(bookName)
  if (!osisCode) {
    return null // Book has no known versification differences
  }

  // Check if we have data for this book
  const bookData = versificationData[osisCode]
  if (!bookData || !bookData.simple_map) {
    return null
  }

  // Check if we have mapping for this chapter
  const chapterKey = chapter.toString()
  const chapterMap = bookData.simple_map[chapterKey]
  if (!chapterMap) {
    return null // No mapping for this chapter
  }

  // Get the mapping for this verse
  const verseKey = verse.toString()
  const christianRef = chapterMap[verseKey]

  return christianRef || null
}

/**
 * Check if a book has versification differences
 */
export async function hasVersificationDifferences(
  bookName: BookName
): Promise<boolean> {
  await loadVersificationData()

  if (!versificationData) {
    return false
  }

  const osisCode = getOsisCode(bookName)
  return osisCode ? osisCode in versificationData : false
}

/**
 * Get all books that have versification mappings
 */
export async function getBooksWithDifferences(): Promise<BookName[]> {
  await loadVersificationData()

  if (!versificationData) {
    return []
  }

  const books: BookName[] = []

  for (const [bookName, osisCode] of Object.entries(BOOK_TO_OSIS)) {
    if (versificationData[osisCode]) {
      books.push(bookName as BookName)
    }
  }

  return books
}

/**
 * Get versification info for a book (for debugging/display purposes)
 */
export async function getVersificationInfo(
  bookName: BookName
): Promise<VersificationBookData | null> {
  await loadVersificationData()

  if (!versificationData) {
    return null
  }

  const osisCode = getOsisCode(bookName)
  return osisCode ? versificationData[osisCode] : null
}

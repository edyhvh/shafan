/**
 * Book data utilities for loading and managing Shafan book data
 * Client-safe version (no fs imports)
 */

import { Book } from './types'
import { logger } from './logger'

export const AVAILABLE_BOOKS = [
  // Tanaj (Hebrew Bible/Old Testament)
  'genesis',
  'exodus',
  'leviticus',
  'numbers',
  'deuteronomy',
  'joshua',
  'judges',
  'ruth',
  'isamuel',
  'iisamuel',
  'ikings',
  'iikings',
  'ichronicles',
  'iichronicles',
  'ezra',
  'nehemiah',
  'esther',
  'job',
  'psalms',
  'proverbs',
  'ecclesiastes',
  'songofsolomon',
  'isaiah',
  'jeremiah',
  'lamentations',
  'ezekiel',
  'daniel',
  'hosea',
  'joel',
  'amos',
  'obadiah',
  'jonah',
  'micah',
  'nahum',
  'habakkuk',
  'zephaniah',
  'haggai',
  'zechariah',
  'malachi',
  // Besorah (New Testament)
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
  // Tanaj (Hebrew Bible/Old Testament)
  genesis: { he: 'בראשית', en: 'Genesis', es: 'Génesis' },
  exodus: { he: 'שמות', en: 'Exodus', es: 'Éxodo' },
  leviticus: { he: 'ויקרא', en: 'Leviticus', es: 'Levítico' },
  numbers: { he: 'במדבר', en: 'Numbers', es: 'Números' },
  deuteronomy: { he: 'דברים', en: 'Deuteronomy', es: 'Deuteronomio' },
  joshua: { he: 'יהושע', en: 'Joshua', es: 'Josué' },
  judges: { he: 'שופטים', en: 'Judges', es: 'Jueces' },
  ruth: { he: 'רות', en: 'Ruth', es: 'Rut' },
  isamuel: { he: 'שמואל א', en: '1 Samuel', es: '1 Samuel' },
  iisamuel: { he: 'שמואל ב', en: '2 Samuel', es: '2 Samuel' },
  ikings: { he: 'מלכים א', en: '1 Kings', es: '1 Reyes' },
  iikings: { he: 'מלכים ב', en: '2 Kings', es: '2 Reyes' },
  ichronicles: { he: 'דברי הימים א', en: '1 Chronicles', es: '1 Crónicas' },
  iichronicles: { he: 'דברי הימים ב', en: '2 Chronicles', es: '2 Crónicas' },
  ezra: { he: 'עזרא', en: 'Ezra', es: 'Esdras' },
  nehemiah: { he: 'נחמיה', en: 'Nehemiah', es: 'Nehemías' },
  esther: { he: 'אסתר', en: 'Esther', es: 'Ester' },
  job: { he: 'איוב', en: 'Job', es: 'Job' },
  psalms: { he: 'תהלים', en: 'Psalms', es: 'Salmos' },
  proverbs: { he: 'משלי', en: 'Proverbs', es: 'Proverbios' },
  ecclesiastes: { he: 'קהלת', en: 'Ecclesiastes', es: 'Eclesiastés' },
  songofsolomon: {
    he: 'שיר השירים',
    en: 'Song of Solomon',
    es: 'Cantar de los Cantares',
  },
  isaiah: { he: 'ישעיה', en: 'Isaiah', es: 'Isaías' },
  jeremiah: { he: 'ירמיה', en: 'Jeremiah', es: 'Jeremías' },
  lamentations: { he: 'איכה', en: 'Lamentations', es: 'Lamentaciones' },
  ezekiel: { he: 'יחזקאל', en: 'Ezekiel', es: 'Ezequiel' },
  daniel: { he: 'דניאל', en: 'Daniel', es: 'Daniel' },
  hosea: { he: 'הושע', en: 'Hosea', es: 'Oseas' },
  joel: { he: 'יואל', en: 'Joel', es: 'Joel' },
  amos: { he: 'עמוס', en: 'Amos', es: 'Amós' },
  obadiah: { he: 'עובדיה', en: 'Obadiah', es: 'Abdías' },
  jonah: { he: 'יונה', en: 'Jonah', es: 'Jonás' },
  micah: { he: 'מיכה', en: 'Micah', es: 'Miqueas' },
  nahum: { he: 'נחום', en: 'Nahum', es: 'Nahúm' },
  habakkuk: { he: 'חבקוק', en: 'Habakkuk', es: 'Habacuc' },
  zephaniah: { he: 'צפניה', en: 'Zephaniah', es: 'Sofonías' },
  haggai: { he: 'חגי', en: 'Haggai', es: 'Hageo' },
  zechariah: { he: 'זכריה', en: 'Zechariah', es: 'Zacarías' },
  malachi: { he: 'מלאכי', en: 'Malachi', es: 'Malaquías' },
  // Besorah (New Testament)
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
  // Tanaj (Hebrew Bible/Old Testament)
  genesis: { hebrew: 'בראשית', transliteration: 'bereishit' },
  exodus: { hebrew: 'שמות', transliteration: 'shemot' },
  leviticus: { hebrew: 'ויקרא', transliteration: 'vayikra' },
  numbers: { hebrew: 'במדבר', transliteration: 'bamidbar' },
  deuteronomy: { hebrew: 'דברים', transliteration: 'devarim' },
  joshua: { hebrew: 'יהושע', transliteration: 'yehoshua' },
  judges: { hebrew: 'שופטים', transliteration: 'shoftim' },
  ruth: { hebrew: 'רות', transliteration: 'rut' },
  isamuel: { hebrew: 'שמואל א', transliteration: 'shmuel alef' },
  iisamuel: { hebrew: 'שמואל ב', transliteration: 'shmuel bet' },
  ikings: { hebrew: 'מלכים א', transliteration: 'melakhim alef' },
  iikings: { hebrew: 'מלכים ב', transliteration: 'melakhim bet' },
  ichronicles: {
    hebrew: 'דברי הימים א',
    transliteration: 'divrei hayamim alef',
  },
  iichronicles: {
    hebrew: 'דברי הימים ב',
    transliteration: 'divrei hayamim bet',
  },
  ezra: { hebrew: 'עזרא', transliteration: 'ezra' },
  nehemiah: { hebrew: 'נחמיה', transliteration: 'nechemia' },
  esther: { hebrew: 'אסתר', transliteration: 'ester' },
  job: { hebrew: 'איוב', transliteration: 'iyov' },
  psalms: { hebrew: 'תהלים', transliteration: 'tehillim' },
  proverbs: { hebrew: 'משלי', transliteration: 'mishlei' },
  ecclesiastes: { hebrew: 'קהלת', transliteration: 'kohelet' },
  songofsolomon: { hebrew: 'שיר השירים', transliteration: 'shir hashirim' },
  isaiah: { hebrew: 'ישעיה', transliteration: 'yeshaya' },
  jeremiah: { hebrew: 'ירמיה', transliteration: 'yirmeya' },
  lamentations: { hebrew: 'איכה', transliteration: 'eicha' },
  ezekiel: { hebrew: 'יחזקאל', transliteration: 'yechezkel' },
  daniel: { hebrew: 'דניאל', transliteration: 'daniel' },
  hosea: { hebrew: 'הושע', transliteration: 'hoshea' },
  joel: { hebrew: 'יואל', transliteration: 'yoel' },
  amos: { hebrew: 'עמוס', transliteration: 'amos' },
  obadiah: { hebrew: 'עובדיה', transliteration: 'ovadia' },
  jonah: { hebrew: 'יונה', transliteration: 'yona' },
  micah: { hebrew: 'מיכה', transliteration: 'micha' },
  nahum: { hebrew: 'נחום', transliteration: 'nachum' },
  habakkuk: { hebrew: 'חבקוק', transliteration: 'chavakuk' },
  zephaniah: { hebrew: 'צפניה', transliteration: 'tsefania' },
  haggai: { hebrew: 'חגי', transliteration: 'chagai' },
  zechariah: { hebrew: 'זכריה', transliteration: 'zecharia' },
  malachi: { hebrew: 'מלאכי', transliteration: 'malachi' },
  // Besorah (New Testament)
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

/**
 * TypeScript types for Shafan book data structures
 */

export interface Verse {
  number: number
  text_nikud: string
  text_nikud_delitzsch?: string
  source_files: string[]
  visual_uncertainty: string[]
}

export interface Chapter {
  hebrew_letter: string
  number: number
  verses: Verse[]
}

export interface Book {
  book_name: string
  author: string
  publication_year: string
  chapters: Chapter[]
}

/**
 * TTH (Traducción del Texto Hebreo) data structures
 * Spanish translation of Hebrew scriptures with footnotes
 */

export interface TTHFootnote {
  marker: string
  number: string
  word: string
  explanation: string
}

export interface TTHVerse {
  verse: number
  tth: string
  footnotes: TTHFootnote[]
  hebrew_terms: string[]
}

export interface TTHChapter {
  chapter: number
  verses: TTHVerse[]
}

export interface TTHBookInfo {
  book_id: string
  tth_name: string
  hebrew_name: string
  english_name: string
  spanish_name: string
  section: string
  total_chapters: number
  total_verses: number
}

export interface TTHBook {
  book_info: TTHBookInfo
  chapters: TTHChapter[]
}

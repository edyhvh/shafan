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

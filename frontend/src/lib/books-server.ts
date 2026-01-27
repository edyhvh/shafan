/**
 * Server-side only book loading utilities
 * This file should NEVER be imported in client components
 */

import { Book } from './types'
import { BookName } from './books'
import { logger } from './logger'

/**
 * Load book data from JSON file (Server-side only)
 * This function uses Node.js fs module and should only be called from Server Components
 */
export async function loadBookServer(bookName: BookName): Promise<Book | null> {
  if (typeof window !== 'undefined') {
    throw new Error('loadBookServer can only be used in Server Components')
  }

  try {
    // Dynamic import to avoid bundling fs in client
    const fs = await import('fs')
    const path = await import('path')

    // Only read from public/data directory
    // This prevents Next.js file tracing from including the parent output directory
    const publicDataPath = path.join(
      process.cwd(),
      'public',
      'data',
      `${bookName}.json`
    )

    if (!fs.existsSync(publicDataPath)) {
      logger.error(`Book file not found: ${bookName}.json`, undefined, {
        bookName,
      })
      return null
    }

    const fileContents = fs.readFileSync(publicDataPath, 'utf-8')
    const data: Book = JSON.parse(fileContents)
    return data
  } catch (error) {
    logger.error(`Error loading book ${bookName}`, error, { bookName })
    return null
  }
}

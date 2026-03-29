/**
 * Server-side only TTH (Traducción del Texto Hebreo) loading utilities
 * This file should NEVER be imported in client components
 */

import type { TTHBook } from './types'
import type { BookName } from './books'
import { getTTHBookId } from './tth'
import { logger } from './logger'

/**
 * Load TTH book data from JSON file (Server-side only)
 * This function uses Node.js fs module and should only be called from Server Components
 */
export async function loadTTHServer(
  bookName: BookName
): Promise<TTHBook | null> {
  if (typeof window !== 'undefined') {
    throw new Error('loadTTHServer can only be used in Server Components')
  }

  const tthBookId = getTTHBookId(bookName)
  if (!tthBookId) {
    return null
  }

  try {
    const fs = await import('fs')
    const path = await import('path')

    const tthPath = path.join(
      process.cwd(),
      '..',
      'data',
      'tth',
      'json',
      `${tthBookId}.json`
    )

    if (!fs.existsSync(tthPath)) {
      logger.error(`TTH file not found: ${tthBookId}.json`, undefined, {
        bookName,
        tthBookId,
      })
      return null
    }

    const fileContents = fs.readFileSync(tthPath, 'utf-8')
    const data: TTHBook = JSON.parse(fileContents)
    return data
  } catch (error) {
    logger.error(`Error loading TTH book ${bookName}`, error, {
      bookName,
      tthBookId,
    })
    return null
  }
}

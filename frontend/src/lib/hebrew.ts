/**
 * Hebrew text utilities
 */

/**
 * Removes nikud (vowel points) from Hebrew text.
 * Nikud characters are in Unicode ranges:
 * - U+05B0–U+05BB (vowel points)
 * - U+05BD (meteg)
 * - U+05BF (rafe)
 * - U+05C1–U+05C2 (shin/sin dots)
 * - U+05C4–U+05C5 (upper/lower dots)
 * - U+05C7 (qamats qatan)
 */
export function removeNikud(text: string): string {
  return text.replace(
    /[\u05B0-\u05BB\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7]/g,
    ''
  )
}

/**
 * Removes cantillation marks (ta'amim) from Hebrew text.
 * Cantillation marks are in Unicode range:
 * - U+0591–U+05AF (cantillation marks)
 */
export function removeCantillation(text: string): string {
  return text.replace(/[\u0591-\u05AF]/g, '')
}

/**
 * Removes word separators (forward slashes) from Hebrew text.
 * Word separators are used in some Hebrew text formats to separate words.
 */
export function removeWordSeparators(text: string): string {
  return text.replace(/\//g, '')
}

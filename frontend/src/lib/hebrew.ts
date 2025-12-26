/**
 * Hebrew text utilities
 */

/**
 * Removes nikud (vowel points) from Hebrew text.
 * Nikud characters are in Unicode ranges:
 * - U+0591–U+05BD (cantillation marks + points)
 * - U+05BF (rafe)
 * - U+05C1–U+05C2 (shin/sin dots)
 * - U+05C4–U+05C5 (upper/lower dots)
 * - U+05C7 (qamats qatan)
 */
export function removeNikud(text: string): string {
  return text.replace(/[\u0591-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7]/g, '');
}


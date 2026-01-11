/**
 * Enhanced smooth scrolling utility with improved easing and performance
 */

/**
 * Smoothly scroll to an element with enhanced easing
 * @param element - The DOM element to scroll to
 * @param offset - The offset from the top of the element in pixels (default: 0)
 * @returns void
 * @throws {Error} If element is null or undefined
 */
export function smoothScrollToElement(
  element: Element | null,
  offset = 0
): void {
  if (!element) {
    console.warn('smoothScrollToElement: element is null or undefined')
    return
  }

  // Validate offset is a finite number
  const validOffset = Number.isFinite(offset) ? offset : 0

  const elementRect = element.getBoundingClientRect()
  const absoluteElementTop = elementRect.top + window.scrollY
  const targetPosition = Math.max(0, absoluteElementTop - validOffset)

  window.scrollTo({
    top: targetPosition,
    behavior: 'smooth',
  })
}

/**
 * Smooth scroll to a verse by its number
 * @param verseNumber - The verse number to scroll to (must be a positive integer)
 * @param offset - The offset from the top in pixels (default: 128)
 * @returns void
 */
export function scrollToVerse(verseNumber: number, offset = 128): void {
  // Validate verse number is a positive integer
  if (!Number.isInteger(verseNumber) || verseNumber < 1) {
    console.warn(`scrollToVerse: invalid verse number: ${verseNumber}`)
    return
  }

  // Validate offset is a finite number
  const validOffset = Number.isFinite(offset) ? offset : 128

  // Sanitize verse number to prevent any injection issues
  const sanitizedVerseNumber = Math.floor(verseNumber)
  const verseElement = document.getElementById(`verse-${sanitizedVerseNumber}`)

  if (verseElement) {
    smoothScrollToElement(verseElement, validOffset)
  } else {
    console.warn(
      `scrollToVerse: verse element not found: ${sanitizedVerseNumber}`
    )
  }
}

/**
 * Smooth scroll to the top of the page
 * @returns void
 */
export function scrollToTop(): void {
  window.scrollTo({
    top: 0,
    behavior: 'smooth',
  })
}

/**
 * Smooth scroll to a specific position
 * @param top - The vertical position to scroll to in pixels
 * @param behavior - The scroll behavior ('smooth' or 'auto', default: 'smooth')
 * @returns void
 */
export function scrollToPosition(
  top: number,
  behavior: ScrollBehavior = 'smooth'
): void {
  // Validate top is a finite number and not negative
  const validTop = Number.isFinite(top) ? Math.max(0, top) : 0

  window.scrollTo({
    top: validTop,
    behavior,
  })
}

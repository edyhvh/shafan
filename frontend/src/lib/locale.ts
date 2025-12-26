/**
 * Utility functions for locale handling
 */

export const locales = ['he', 'es', 'en'] as const
export type Locale = (typeof locales)[number]
export const defaultLocale: Locale = 'he'

/**
 * Extract locale from pathname
 */
export function getLocaleFromPath(pathname: string): Locale {
  const segments = pathname.split('/').filter(Boolean)
  if (segments.length > 0 && locales.includes(segments[0] as Locale)) {
    return segments[0] as Locale
  }
  return defaultLocale
}

/**
 * Remove locale from pathname
 */
export function removeLocaleFromPath(pathname: string): string {
  const segments = pathname.split('/').filter(Boolean)
  if (segments.length > 0 && locales.includes(segments[0] as Locale)) {
    return '/' + segments.slice(1).join('/')
  }
  return pathname
}

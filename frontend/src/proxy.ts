import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { locales, defaultLocale, type Locale } from './lib/locale'

/**
 * Parse Accept-Language header and return preferred locale
 * Handles quality values (q-values) to determine preference order
 */
function detectLocaleFromHeader(acceptLanguage: string): Locale {
  if (!acceptLanguage) {
    return defaultLocale
  }

  // Parse Accept-Language header
  // Format: "en-US,en;q=0.9,es;q=0.8,he;q=0.7"
  const languages = acceptLanguage
    .split(',')
    .map((lang) => {
      const [locale, qValue] = lang.trim().split(';q=')
      const quality = qValue ? parseFloat(qValue) : 1.0
      // Extract base language code (e.g., "en-US" -> "en")
      const baseLocale = locale.split('-')[0].toLowerCase()
      return { locale: baseLocale, quality }
    })
    .sort((a, b) => b.quality - a.quality) // Sort by quality (highest first)

  // Find first matching locale
  for (const { locale } of languages) {
    if (locales.includes(locale as Locale)) {
      return locale as Locale
    }
  }

  return defaultLocale
}

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Skip proxy for static files and API routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.startsWith('/data') ||
    pathname.startsWith('/favicon.ico') ||
    pathname === '/icon.svg'
  ) {
    return NextResponse.next()
  }

  // Check if pathname already has a locale
  const pathnameHasLocale = locales.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  )

  if (pathnameHasLocale) {
    return NextResponse.next()
  }

  // Detect locale from Accept-Language header with improved parsing
  const acceptLanguage = request.headers.get('accept-language') || ''
  const locale = detectLocaleFromHeader(acceptLanguage)

  // Redirect to locale-prefixed path
  const redirectPath = pathname === '/' ? `/${locale}` : `/${locale}${pathname}`
  const newUrl = new URL(redirectPath, request.url)
  console.log('[Proxy] Redirecting to:', newUrl.pathname)
  return NextResponse.redirect(newUrl)
}

// Proxy config for Next.js
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - icon.svg (icon file)
     * - data (static JSON files)
     *
     * The pattern uses .*? to make the trailing part optional,
     * allowing it to match the root path '/' as well.
     */
    '/((?!api|_next/static|_next/image|favicon.ico|icon.svg|data).*)?',
  ],
}

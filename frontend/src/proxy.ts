import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const locales = ['he', 'es', 'en']
const defaultLocale = 'he'

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Debug: log proxy execution
  console.log('[Proxy] Processing:', pathname)

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

  // Get locale from Accept-Language header or use default
  const acceptLanguage = request.headers.get('accept-language') || ''
  let locale = defaultLocale

  // Try to detect locale from Accept-Language header
  if (acceptLanguage.includes('es')) {
    locale = 'es'
  } else if (acceptLanguage.includes('en')) {
    locale = 'en'
  } else if (acceptLanguage.includes('he')) {
    locale = 'he'
  }

  // Redirect to locale-prefixed path
  const redirectPath = pathname === '/' ? `/${locale}` : `/${locale}${pathname}`
  const newUrl = new URL(redirectPath, request.url)
  console.log('[Proxy] Redirecting to:', newUrl.pathname)
  return NextResponse.redirect(newUrl)
}

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

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const locales = ['he', 'es', 'en'];
const defaultLocale = 'he';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip middleware for static files and API routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.startsWith('/data') ||
    pathname.startsWith('/favicon.ico') ||
    pathname === '/icon.svg'
  ) {
    return NextResponse.next();
  }

  // Check if pathname already has a locale
  const pathnameHasLocale = locales.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );

  if (pathnameHasLocale) {
    return NextResponse.next();
  }

  // Get locale from Accept-Language header or use default
  const acceptLanguage = request.headers.get('accept-language') || '';
  let locale = defaultLocale;

  // Try to detect locale from Accept-Language header
  if (acceptLanguage.includes('es')) {
    locale = 'es';
  } else if (acceptLanguage.includes('en')) {
    locale = 'en';
  } else if (acceptLanguage.includes('he')) {
    locale = 'he';
  }

  // Redirect to locale-prefixed path
  const newUrl = new URL(`/${locale}${pathname}`, request.url);
  return NextResponse.redirect(newUrl);
}

export const config = {
  matcher: [
    // Match all pathnames except for
    // - api routes
    // - _next/static (static files)
    // - _next/image (image optimization files)
    // - favicon.ico (favicon file)
    // - icon.svg (icon file)
    // - data directory (static JSON files)
    '/((?!api|_next/static|_next/image|favicon.ico|icon.svg|data).*)',
  ],
};

import Link from 'next/link'

/**
 * Not found page for locale-specific routes
 * Shown when a page is not found within locale routes
 */
export default function LocaleNotFound() {
  // Note: usePathname doesn't work in not-found.tsx
  // We'll show all languages

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="max-w-md w-full text-center">
        <div className="text-8xl font-bold text-black/20 mb-4">404</div>
        <h1 className="text-4xl font-bold text-black mb-4">Page Not Found</h1>
        <p className="text-lg text-gray mb-2">
          The page you&apos;re looking for doesn&apos;t exist.
        </p>
        <p className="text-lg text-gray mb-8 font-ui-hebrew" dir="rtl">
          הדף שחיפשת לא נמצא.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/he"
            className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray transition-colors"
          >
            בית (עברית)
          </Link>
          <Link
            href="/es"
            className="px-6 py-3 bg-white text-black border border-black/20 rounded-lg hover:bg-black/5 transition-colors"
          >
            Inicio (Español)
          </Link>
          <Link
            href="/en"
            className="px-6 py-3 bg-white text-black border border-black/20 rounded-lg hover:bg-black/5 transition-colors"
          >
            Home (English)
          </Link>
        </div>
      </div>
    </div>
  )
}

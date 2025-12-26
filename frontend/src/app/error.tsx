'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { logger } from '@/lib/logger'

/**
 * Global error page
 * Shown when an error occurs outside of locale routes
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error
    logger.error('Global error', error, {
      digest: error.digest,
    })
  }, [error])

  return (
    <html>
      <body>
        <div className="min-h-screen flex items-center justify-center bg-background px-4">
          <div className="max-w-md w-full text-center">
            <h1 className="text-4xl font-bold text-black mb-4">
              Something went wrong
            </h1>
            <p className="text-lg text-gray mb-8">
              We&apos;re sorry, but an unexpected error occurred. Please try
              refreshing the page.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={reset}
                className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray transition-colors"
              >
                Try again
              </button>
              <Link
                href="/"
                className="px-6 py-3 bg-white text-black border border-black/20 rounded-lg hover:bg-black/5 transition-colors"
              >
                Back to home
              </Link>
            </div>

            {process.env.NODE_ENV === 'development' && error.message && (
              <div className="mt-8 p-4 bg-red-50 border border-red-200 rounded-lg text-left">
                <p className="text-sm font-mono text-red-800 break-all">
                  {error.message}
                </p>
                {error.digest && (
                  <p className="text-xs text-red-600 mt-2">
                    Digest: {error.digest}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      </body>
    </html>
  )
}

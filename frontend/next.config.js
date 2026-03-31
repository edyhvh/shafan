import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Ultra-minimalist configuration for shafan
  reactStrictMode: true,

  // Allow LAN-origin dev clients (mobile/tablet) to access Next dev resources
  allowedDevOrigins:
    process.env.NODE_ENV === 'development' ? ['192.168.0.16'] : undefined,

  // Optimize for mobile and slow connections
  // Note: optimizeCss is now stable in Next.js 15, no longer experimental

  // i18n is handled by middleware.ts for App Router
  // Locales: he (Hebrew), es (Spanish), en (English)
  // Automatic locale detection from browser Accept-Language header

  // Static optimization - remove standalone for Vercel compatibility
  // output: 'standalone',

  // Optimize bundle size and serverless functions
  experimental: {
    // Optimize server components bundle size
    optimizePackageImports: ['react', 'react-dom'],
  },

  turbopack: {
    root: __dirname,
  },

  // Reduce serverless function size by optimizing imports
  modularizeImports: {
    '@/lib/books': {
      transform: '@/lib/books',
      skipDefaultConversion: true,
    },
  },

  // Security headers for production
  async headers() {
    const isProd = process.env.NODE_ENV === 'production'
    const baseHeaders = [
      // Prevent clickjacking
      {
        key: 'X-Frame-Options',
        value: 'DENY',
      },
      // Prevent MIME type sniffing
      {
        key: 'X-Content-Type-Options',
        value: 'nosniff',
      },
      // Enable XSS protection
      {
        key: 'X-XSS-Protection',
        value: '1; mode=block',
      },
      // Control referrer information
      {
        key: 'Referrer-Policy',
        value: 'strict-origin-when-cross-origin',
      },
      // Restrict browser features
      {
        key: 'Permissions-Policy',
        value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()',
      },
      // Opt out of cross-origin opener sharing where possible
      {
        key: 'Cross-Origin-Opener-Policy',
        value: 'same-origin-allow-popups',
      },
      // Restrict who can load resources from this origin
      {
        key: 'Cross-Origin-Resource-Policy',
        value: 'same-origin',
      },
    ]

    if (isProd) {
      baseHeaders.unshift({
        key: 'Strict-Transport-Security',
        value: 'max-age=31536000; includeSubDomains',
      })
    }

    return [
      {
        source: '/(.*)',
        headers: [
          ...baseHeaders,
          // Content Security Policy
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://storage.ko-fi.com",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://storage.ko-fi.com",
              "font-src 'self' https://fonts.gstatic.com",
              "img-src 'self' data: https:",
              "connect-src 'self' https://ko-fi.com https://storage.ko-fi.com",
              "frame-src 'self' https://ko-fi.com",
              "frame-ancestors 'none'",
              "base-uri 'self'",
              "form-action 'self'",
            ].join('; '),
          },
        ],
      },
    ]
  },
}

export default nextConfig

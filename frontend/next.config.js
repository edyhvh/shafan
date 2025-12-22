/** @type {import('next').NextConfig} */
const nextConfig = {
  // Ultra-minimalist configuration for shafan
  reactStrictMode: true,
  swcMinify: true,

  // Optimize for mobile and slow connections
  experimental: {
    optimizeCss: true,
  },

  // i18n configuration for Hebrew, Spanish, and English
  i18n: {
    locales: ['he', 'es', 'en'],
    defaultLocale: 'he',
    localeDetection: true,
  },

  // Static optimization
  output: 'standalone',

  // Headers for better caching and performance
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig


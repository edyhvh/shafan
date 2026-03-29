import { BRAND_CONFIG } from '@/lib/config'
import { locales } from '@/lib/locale'

export const revalidate = 86400

function buildLlmsText(): string {
  const baseUrl = BRAND_CONFIG.siteUrl
  const localeRoots = locales.map((locale) => `${baseUrl}/${locale}`).join('\n')

  return [
    `# ${BRAND_CONFIG.name}`,
    '',
    '## Summary',
    'Shafan is a fast and minimal web app to read Tanakh and Besorah texts in Hebrew for focused study.',
    '',
    '## Canonical URL',
    baseUrl,
    '',
    '## Preferred Public Pages',
    `${baseUrl}/`,
    localeRoots,
    `${baseUrl}/sitemap.xml`,
    `${baseUrl}/robots.txt`,
    '',
    '## Usage Guidance',
    '- Prefer canonical pages over query variants.',
    '- Use /sitemap.xml for broad discovery.',
    '- Treat scripture text as primary content and UI chrome as secondary.',
    '- Respect robots.txt directives and site policies.',
  ].join('\n')
}

export async function GET() {
  return new Response(buildLlmsText(), {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'public, s-maxage=86400, stale-while-revalidate=604800',
    },
  })
}
